"""
Helper utilities for the Hiring Tracker application.
"""

import base64
from datetime import datetime
from typing import Optional, Union, Tuple
import os

import pandas as pd

from src.config.settings import LOGO_PATH, BASE_STAGES


# ---------------------------------------------------------------------------
# Pipeline zone helpers
# ---------------------------------------------------------------------------

# Zone 0 = Urgent (needs screening): Initial Interview, HR User Interview
# Zone 1 = In Process: Skill Test, Final Interview
# Zone 2 = Nearing Completion: Offering, Contract Sign
# Zone 3 = Pool (completed): On Boarding = True or Completed Date set
# Zone 4 = Frozen

_STAGE_ZONE_MAP: dict = {
    "Initial Interview (HR)": 0,
    "HR & User Interview (Stage 1)": 0,
    "Skill Test": 1,
    "Final Interview": 1,
    "Offering": 2,
    "Contract Sign": 2,
    "On Boarding": 3,
}

ZONE_LABELS: dict = {
    0: "Needs Screening",
    1: "In Process",
    2: "Nearing Completion",
}


def get_current_stage(row) -> Optional[str]:
    """Return the current (last True) hiring stage for a position row.

    Iterates BASE_STAGES in reverse to find the furthest completed stage.
    Respects the Has Skill Test flag.  Returns None when no stage is True.
    """
    has_skill_test = bool(row.get("Has Skill Test", True))
    for stage in reversed(BASE_STAGES):
        if stage == "Skill Test" and not has_skill_test:
            continue
        try:
            val = row.get(stage) if hasattr(row, "get") else row[stage]
        except (KeyError, TypeError):
            continue
        if val is True:
            return stage
    return None


def get_stage_zone(row) -> int:
    """Return the pipeline zone integer for a position row.

    0 = Urgent (needs screening)
    1 = In Process
    2 = Nearing Completion
    3 = Pool / Completed
    4 = Frozen
    """
    if bool(row.get("Freeze", False)):
        return 4

    if bool(row.get("On Boarding", False)):
        return 3
    completed_date = str(row.get("Completed Date", "") or "").strip()
    if completed_date:
        return 3

    stage = get_current_stage(row)
    if stage is None:
        return 0  # Nothing started yet → treat as urgent
    return _STAGE_ZONE_MAP.get(stage, 1)


def split_by_pipeline_zone(df: pd.DataFrame) -> Tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    """Split a hiring DataFrame into pipeline zone sub-DataFrames.

    Returns:
        (urgent, in_process, nearing_done, pooled, frozen)
    """
    if df is None or len(df) == 0:
        empty = pd.DataFrame(columns=df.columns if df is not None else [])
        return empty, empty, empty, empty, empty

    zones = df.apply(get_stage_zone, axis=1)
    return (
        df[zones == 0].copy(),
        df[zones == 1].copy(),
        df[zones == 2].copy(),
        df[zones == 3].copy(),
        df[zones == 4].copy(),
    )


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


def extract_technical_skills_from_jd(jd_text: str) -> list[str]:
    """
    Extract technical skills from a job description text
    by parsing bullet points and excluding generic experience requirements.
    """
    if not jd_text or not isinstance(jd_text, str):
        return []

    import re

    def _finalize(items: list[str]) -> list[str]:
        out: list[str] = []
        for item in items:
            cleaned = re.sub(r"\s+", " ", str(item or "")).strip(" -.;,")
            if not cleaned:
                continue
            cleaned = re.sub(r"\s*-\s*", " - ", cleaned)
            cleaned = re.sub(r"\s+,", ",", cleaned)
            if cleaned and cleaned[0].isalpha():
                cleaned = cleaned[0].upper() + cleaned[1:]
            if cleaned not in out:
                out.append(cleaned)
        return out[:15]

    raw = jd_text.replace("\r", "\n").strip()

    # Pattern A: JD exported as one long dash-delimited paragraph with wrapped lines.
    # Example:
    #   - Pengalaman ...\nanalis ... - Latar belakang ... - Kemampuan ...
    compact = re.sub(r"\s+", " ", raw)
    if compact.startswith("-") and " - " in compact:
        dash_parts = [p.strip() for p in re.split(r"\s-\s+", compact.lstrip("- ")) if p.strip()]
        merged: list[str] = []
        for part in dash_parts:
            # Keep the final requirement as one sentence when source is split like:
            # "Kemampuan reporting & presentasi" + "Pengetahuan Lanskap Bisnis Media"
            if (
                merged
                and part.lower().startswith("pengetahuan ")
                and ("reporting" in merged[-1].lower() or "presentasi" in merged[-1].lower())
            ):
                merged[-1] = f"{merged[-1]} - {part}"
            else:
                merged.append(part)
        return _finalize(merged)

    # Pattern B: line-based bullets / numbered points.
    lines = raw.split("\n")
    skills: list[str] = []
    current = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if any(h in line for h in ("Minimum Qualifications", "Job Description:", "Requirements", "Role Expectations")):
            continue

        line = re.sub(r"^(\d+[\.)]|-|\u2022|\*)\s*", "", line).strip()
        if not line:
            continue

        is_continuation = bool(current) and (
            bool(re.match(r"^[a-z]", line))
            or current.endswith((",", "-", "/", "&"))
        )

        if is_continuation:
            current = f"{current} {line}".strip()
        else:
            if current:
                skills.append(current)
            current = line

        if re.search(r"[\.;:]$", line):
            skills.append(current)
            current = ""

    if current:
        skills.append(current)

    return _finalize(skills)
