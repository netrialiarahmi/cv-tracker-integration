"""
Input validation utilities.
"""

from src.config.settings import MIN_PASSWORD_LENGTH


def validate_password(password: str) -> bool:
    """
    Validate password meets minimum requirements.
    
    Args:
        password: Password string to validate
        
    Returns:
        True if password is valid, False otherwise
    """
    return len(password) >= MIN_PASSWORD_LENGTH


def validate_division_name(division: str) -> bool:
    """
    Validate division name is not empty.
    
    Args:
        division: Division name to validate
        
    Returns:
        True if division name is valid, False otherwise
    """
    return bool(division and division.strip())
