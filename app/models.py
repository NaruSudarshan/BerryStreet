from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    provider_id = Column(String, unique=True)
    wallet_balance = Column(Float, default=100000.0) # start with ₹1,00,000 INR
    
    # Relationships
    transactions = relationship("Transaction", back_populates="owner")
    portfolios = relationship("Portfolio", back_populates="owner")

class Portfolio(Base):
    __tablename__ = "portfolios"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ticker_symbol = Column(String, index=True)
    quantity = Column(Integer)
    average_buy_price = Column(Float)
    
    owner = relationship("User", back_populates="portfolios")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ticker_symbol = Column(String, index=True)
    transaction_type = Column(String) # "BUY" or "SELL"
    quantity = Column(Integer)
    price_at_execution = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="transactions")