from pydantic import BaseModel

class StockQuote(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    currency: str = "INR"
    
    # --- Advanced Stats ---
    market_cap: int | float | None = None
    pe_ratio: float | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None
    volume: int | float | None = None

class ChartData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float | int | None = None

# The data we expect from the frontend after a successful Google Login
class OAuthUserLogin(BaseModel):
    email: str
    username: str
    provider_id: str

# What we send back to the frontend
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    wallet_balance: float
    
    class Config:
        from_attributes = True

# --- JWT Authentication Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int | None = None

# --- Trading Transaction Schemas ---
class TransactionCreate(BaseModel):
    ticker_symbol: str
    quantity: int

class TransactionResponse(BaseModel):
    id: int
    ticker_symbol: str
    transaction_type: str
    quantity: int
    price_at_execution: float
    timestamp: str 
    
    class Config:
        from_attributes = True

class PortfolioHolding(BaseModel):
    ticker_symbol: str
    quantity: int
    average_buy_price: float
    current_price: float
    total_value: float
    unrealized_pnl: float

class PortfolioResponse(BaseModel):
    wallet_balance: float
    total_portfolio_value: float
    total_unrealized_pnl: float
    holdings: list[PortfolioHolding]