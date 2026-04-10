from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import yfinance as yf
from app.database import get_db
from app.models import User, Transaction, Portfolio
from app.auth import get_current_user
from app.schemas import TransactionCreate, TransactionResponse

router = APIRouter(prefix="/trade", tags=["Trading"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]

def get_live_price(ticker_symbol: str) -> float:
    try:
        ticker_symbol = ticker_symbol.upper()
        if not ticker_symbol.endswith(".NS") and not ticker_symbol.endswith(".BO"):
            ticker_symbol = f"{ticker_symbol}.NS"
            
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
        if not price:
            raise ValueError(f"Price data not found for {ticker_symbol}")
        return float(price)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch price for {ticker_symbol}: {str(e)}")

def format_ticker(symbol: str) -> str:
    symbol = symbol.upper()
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        return f"{symbol}.NS"
    return symbol

@router.post("/buy", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def buy_stock(trade_in: TransactionCreate, db: db_dependency, current_user: user_dependency):
    if trade_in.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        
    ticker = format_ticker(trade_in.ticker_symbol)
    current_price = get_live_price(ticker)
    total_cost = current_price * trade_in.quantity
    
    # 1. Check if user has enough balance
    if current_user.wallet_balance < total_cost:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        
    # 2. Deduct balance
    current_user.wallet_balance -= total_cost
    
    # 3. Create the transaction record
    new_transaction = Transaction(
        user_id=current_user.id,
        ticker_symbol=ticker,
        transaction_type="BUY",
        quantity=trade_in.quantity,
        price_at_execution=current_price
    )
    db.add(new_transaction)
    
    # 4. Update Portfolio
    portfolio_entry = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id,
        Portfolio.ticker_symbol == ticker
    ).first()
    
    if portfolio_entry:
        total_value = (portfolio_entry.quantity * portfolio_entry.average_buy_price) + total_cost
        new_quantity = portfolio_entry.quantity + trade_in.quantity
        portfolio_entry.average_buy_price = total_value / new_quantity
        portfolio_entry.quantity = new_quantity
    else:
        portfolio_entry = Portfolio(
            user_id=current_user.id,
            ticker_symbol=ticker,
            quantity=trade_in.quantity,
            average_buy_price=current_price
        )
        db.add(portfolio_entry)
        
    db.commit()
    db.refresh(new_transaction)
    
    return {
        "id": new_transaction.id,
        "ticker_symbol": new_transaction.ticker_symbol,
        "transaction_type": new_transaction.transaction_type,
        "quantity": new_transaction.quantity,
        "price_at_execution": new_transaction.price_at_execution,
        "timestamp": new_transaction.timestamp.isoformat()
    }

@router.post("/sell", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def sell_stock(trade_in: TransactionCreate, db: db_dependency, current_user: user_dependency):
    if trade_in.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        
    ticker = format_ticker(trade_in.ticker_symbol)
    
    # 1. Verify user holdings
    portfolio_entry = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id,
        Portfolio.ticker_symbol == ticker
    ).first()
    
    if not portfolio_entry or portfolio_entry.quantity < trade_in.quantity:
        owned = portfolio_entry.quantity if portfolio_entry else 0
        raise HTTPException(status_code=400, detail=f"Insufficient shares. You only own {owned} shares of {ticker}.")
        
    # 2. Add funds back to wallet using current price
    current_price = get_live_price(ticker)
    total_revenue = current_price * trade_in.quantity
    current_user.wallet_balance += total_revenue
    
    # 3. Update Portfolio
    portfolio_entry.quantity -= trade_in.quantity
    if portfolio_entry.quantity == 0:
        db.delete(portfolio_entry)
        
    # 4. Record the transaction
    new_transaction = Transaction(
        user_id=current_user.id,
        ticker_symbol=ticker,
        transaction_type="SELL",
        quantity=trade_in.quantity,
        price_at_execution=current_price
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return {
        "id": new_transaction.id,
        "ticker_symbol": new_transaction.ticker_symbol,
        "transaction_type": new_transaction.transaction_type,
        "quantity": new_transaction.quantity,
        "price_at_execution": new_transaction.price_at_execution,
        "timestamp": new_transaction.timestamp.isoformat()
    }
