"""
Custom Exception Classes
"""


class TradeXException(Exception):
    """Base exception for TradeX application"""
    pass


class TwitterAPIError(TradeXException):
    """Twitter API related errors"""
    pass


class TradingAPIError(TradeXException):
    """Trading API related errors"""
    pass


class SentimentAnalysisError(TradeXException):
    """Sentiment analysis related errors"""
    pass


class ConfigurationError(TradeXException):
    """Configuration related errors"""
    pass

