from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Portfolio
from app.auth import get_current_user
from app.schemas import PortfolioResponse, PortfolioHolding
import yfinance as yf

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

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
        return float(price) if price else 0.0
    except:
        return 0.0

@router.get("", response_model=PortfolioResponse)
def get_portfolio(db: db_dependency, current_user: user_dependency):
    holdings = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).all()
    
    active_holdings = []
    total_portfolio_value = 0.0
    total_unrealized_pnl = 0.0
    
    for holding in holdings:
        current_price = get_live_price(holding.ticker_symbol)
        
        # fallback to average buy price if API fails
        if current_price == 0.0:
            current_price = holding.average_buy_price
            
        total_value = current_price * holding.quantity
        unrealized_pnl = (current_price - holding.average_buy_price) * holding.quantity
        
        total_portfolio_value += total_value
        total_unrealized_pnl += unrealized_pnl
        
        active_holdings.append(PortfolioHolding(
            ticker_symbol=holding.ticker_symbol,
            quantity=holding.quantity,
            average_buy_price=round(holding.average_buy_price, 2),
            current_price=round(current_price, 2),
            total_value=round(total_value, 2),
            unrealized_pnl=round(unrealized_pnl, 2)
        ))
            
    return PortfolioResponse(
        wallet_balance=round(current_user.wallet_balance, 2),
        total_portfolio_value=round(total_portfolio_value, 2),
        total_unrealized_pnl=round(total_unrealized_pnl, 2),
        holdings=active_holdings
    )
