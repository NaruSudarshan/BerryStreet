from typing import Annotated
from fastapi import APIRouter, HTTPException, Path, Query
import yfinance as yf
from app.schemas import StockQuote, ChartData

router = APIRouter(prefix="/stocks", tags=["Market"])

# Reusable Annotated Type for ticker symbols
StockSymbol = Annotated[
    str, 
    Path(
        min_length=2, 
        max_length=15, 
        description="The stock ticker symbol (e.g., RELIANCE, TCS, INFY)",
        example="TCS"
    )
]

POPULAR_TICKERS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SBIN.NS"]

@router.get("/popular", response_model=list[StockQuote])
def get_popular_stocks():
    """
    Returns live quotes for a predefined list of popular Indian stocks.
    Useful for populating the frontend Discover/Home page.
    """
    popular_data = []
    # yfinance can be slightly slow when fetching .info in a loop, 
    # but for 5 tickers it works perfectly fine for our use case.
    for symbol in POPULAR_TICKERS:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            # 'currentPrice' check confirms we received valid financial data
            if "currentPrice" in info:
                popular_data.append({
                    "symbol": symbol, 
                    "company_name": info.get("shortName", symbol),
                    "current_price": info["currentPrice"],
                    "currency": info.get("financialCurrency", "INR"),
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE"),
                    "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                    "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                    "volume": info.get("volume")
                })
        except Exception:
            # We silently pass exceptions here so that if one ticker fails 
            # (e.g. Yahoo Finance timeout), it doesn't crash the whole homepage list.
            pass
            
    return popular_data

@router.get("/{symbol}", response_model=StockQuote)
def get_live_price(symbol: StockSymbol):
    symbol = symbol.upper()
    
    # Auto-NSE logic for the Indian market
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        query_symbol = f"{symbol}.NS"
    else:
        query_symbol = symbol
        
    ticker = yf.Ticker(query_symbol)
    info = ticker.info
    
    if "currentPrice" not in info:
        raise HTTPException(status_code=404, detail=f"Stock symbol {symbol} not found on NSE/BSE.")
    
    # Return the formatted data
    return {
        "symbol": query_symbol, 
        "company_name": info.get("shortName", symbol),
        "current_price": info["currentPrice"],
        "currency": info.get("financialCurrency", "INR"),
        
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "volume": info.get("volume")
    }

@router.get("/{symbol}/chart", response_model=list[ChartData])
def get_chart_data(
    symbol: StockSymbol, 
    period: Annotated[str, Query(description="Time period (e.g., 1mo, 1y, 5y)")] = "1y"
):
    symbol = symbol.upper()
    
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        query_symbol = f"{symbol}.NS"
    else:
        query_symbol = symbol
        
    ticker = yf.Ticker(query_symbol)
    history = ticker.history(period=period)
    
    if history.empty:
        raise HTTPException(status_code=404, detail="No chart data found.")
    
    chart_data = []
    for index, row in history.iterrows():
        chart_data.append({
            "date": index.strftime("%Y-%m-%d"),
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"]
        })
        
    return chart_data