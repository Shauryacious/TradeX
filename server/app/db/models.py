"""
Database Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.db.database import Base


class Tweet(Base):
    """Tweet model for storing monitored tweets"""
    
    __tablename__ = "tweets"
    
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String, unique=True, index=True, nullable=False)
    author_username = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String, nullable=True)  # positive, negative, neutral
    processed = Column(Boolean, default=False)
    created_at_db = Column(DateTime, server_default=func.now())


class Trade(Base):
    """Trade model for storing executed trades"""
    
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    side = Column(String, nullable=False)  # buy, sell
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    order_id = Column(String, unique=True, nullable=True)
    status = Column(String, nullable=False)  # pending, filled, cancelled, rejected
    tweet_id = Column(Integer, nullable=True)  # Reference to Tweet
    sentiment_score = Column(Float, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Position(Base):
    """Current position model"""
    
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    quantity = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

