import yfinance as yf
from fastapi import APIRouter, HTTPException, Path, Query
from app.schemas import StockQuote, ChartData
from typing import Annotated

router = APIRouter(prefix="/market", tags=["Market"])

StockSymbol = Annotated[
    str, 
    Path(
        min_length=2, 
        max_length=15, 
        description="The stock ticker symbol (e.g., RELIANCE, TCS, INFY)"
    )
]

def format_ticker(symbol: str) -> str:
    symbol = symbol.upper()
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        return f"{symbol}.NS"
    return symbol

POPULAR_TICKERS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SBIN.NS"]

@router.get("/popular", response_model=list[StockQuote])
def get_popular_stocks():
    popular_data = []
    for symbol in POPULAR_TICKERS:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if "currentPrice" in info:
                popular_data.append(StockQuote(
                    symbol=symbol, 
                    company_name=info.get("shortName", symbol),
                    current_price=info["currentPrice"],
                    currency=info.get("financialCurrency", "INR"),
                    market_cap=info.get("marketCap"),
                    pe_ratio=info.get("trailingPE"),
                    fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
                    fifty_two_week_low=info.get("fiftyTwoWeekLow"),
                    volume=info.get("volume")
                ))
        except Exception:
            pass
    return popular_data

@router.get("/quote/{ticker_symbol}", response_model=StockQuote)
def get_quote(ticker_symbol: StockSymbol):
    query_symbol = format_ticker(ticker_symbol)
    try:
        ticker = yf.Ticker(query_symbol)
        info = ticker.info
        
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
        if current_price is None:
            raise HTTPException(status_code=404, detail=f"Price data not found for {query_symbol}")
            
        return StockQuote(
            symbol=query_symbol,
            company_name=info.get("longName", info.get("shortName", query_symbol)),
            current_price=current_price,
            currency=info.get("currency", "INR"),
            market_cap=info.get("marketCap"),
            pe_ratio=info.get("trailingPE"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            volume=info.get("volume")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chart/{ticker_symbol}", response_model=list[ChartData])
def get_chart(ticker_symbol: StockSymbol, interval: str = "1d", period: str = "1mo"):
    query_symbol = format_ticker(ticker_symbol)
    try:
        ticker = yf.Ticker(query_symbol)
        hist = ticker.history(period=period, interval=interval)
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"Chart data not found for {query_symbol}")
            
        chart_data = []
        for index, row in hist.iterrows():
            date_str = index.strftime("%Y-%m-%d %H:%M:%S") if hasattr(index, "strftime") else str(index)
            chart_data.append(ChartData(
                date=date_str,
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=row.get("Volume", 0)
            ))
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
