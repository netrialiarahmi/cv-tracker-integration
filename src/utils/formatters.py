"""
Formatting utilities for dates, text, and display values.
"""

from datetime import datetime


def format_datetime(dt: datetime) -> str:
    """
    Format datetime object to standard string format.
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted datetime string (YYYY-MM-DD HH:MM:SS)
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_current_timestamp() -> str:
    """
    Get current timestamp as formatted string.
    
    Returns:
        Current timestamp string
    """
    return format_datetime(datetime.now())


def mask_password(password: str) -> str:
    """
    Mask password for display purposes.
    
    Args:
        password: Password to mask
        
    Returns:
        Masked password string
    """
    return "•" * len(password)
