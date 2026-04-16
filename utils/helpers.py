"""
Helper utilities for the Hiring Tracker application.
"""

import base64
from typing import Optional
import os
from config.settings import LOGO_PATH, LEGACY_LOGO_PATH


def get_logo_base64() -> str:
    """
    Load and encode logo image as base64 string.
    Tries new path first, falls back to legacy path.
    
    Returns:
        Base64 encoded logo string
    """
    logo_file = LOGO_PATH if os.path.exists(LOGO_PATH) else LEGACY_LOGO_PATH
    try:
        with open(logo_file, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        # Return empty string if logo not found
        return ""


def encode_file_base64(file_contents: bytes) -> str:
    """
    Encode file contents as base64 string.
    
    Args:
        file_contents: Raw file bytes
        
    Returns:
        Base64 encoded string
    """
    return base64.b64encode(file_contents).decode()


def decode_file_base64(encoded_str: str) -> bytes:
    """
    Decode base64 string to file contents.
    
    Args:
        encoded_str: Base64 encoded string
        
    Returns:
        Decoded file bytes
    """
    return base64.b64decode(encoded_str)
