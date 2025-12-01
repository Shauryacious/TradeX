"""
Helper utility functions
"""

from typing import Any, Dict
from datetime import datetime


def format_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Format API response"""
    return {
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
    }


def validate_symbol(symbol: str) -> bool:
    """Validate stock symbol format"""
    return symbol.isalpha() and 1 <= len(symbol) <= 5


def calculate_pnl(entry_price: float, current_price: float, quantity: float) -> float:
    """Calculate profit/loss"""
    return (current_price - entry_price) * quantity

