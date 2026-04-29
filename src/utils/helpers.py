"""
Helper utilities for the Hiring Tracker application.
"""

import base64
from datetime import datetime
from typing import Optional, Union
import os

import pandas as pd

from src.config.settings import LOGO_PATH


_DATE_FORMATS = ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S")


def extract_year(date_value) -> int:
    """Best-effort year extraction. Returns 0 when the value can't be parsed."""
    if date_value is None:
        return 0
    try:
        if pd.isna(date_value):
            return 0
    except (TypeError, ValueError):
        pass
    s = str(date_value).strip()
    if not s:
        return 0
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).year
        except ValueError:
            continue
    return 0


def filter_by_year_range(
    df: pd.DataFrame,
    year_from: Union[str, int] = "All",
    year_to: Union[str, int] = "All",
    date_col: str = "Created Date",
) -> pd.DataFrame:
    """
    Filter a hiring DataFrame by [year_from, year_to] inclusive.

    "All" disables that bound. When both are "All" the DataFrame is returned
    unchanged. Rows whose `date_col` is missing/unparseable are excluded only
    when at least one bound is active.
    """
    if df is None or len(df) == 0:
        return df
    if year_from == "All" and year_to == "All":
        return df
    if date_col not in df.columns:
        return df

    def _in_range(value) -> bool:
        year = extract_year(value)
        if year == 0:
            return False
        if year_from != "All" and year < int(year_from):
            return False
        if year_to != "All" and year > int(year_to):
            return False
        return True

    return df[df[date_col].apply(_in_range)]


def available_years(df: pd.DataFrame, date_col: str = "Created Date") -> list:
    """Return a sorted list of unique years parsed from `date_col`."""
    if df is None or len(df) == 0 or date_col not in df.columns:
        return []
    years = set()
    for value in df[date_col].dropna():
        y = extract_year(value)
        if y:
            years.add(y)
    return sorted(years)


def get_logo_base64() -> str:
    """
    Load and encode logo image as base64 string.
    Tries new path first, falls back to legacy path.
    
    Returns:
        Base64 encoded logo string
    """
    logo_file = LOGO_PATH
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
