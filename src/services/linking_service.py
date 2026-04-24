"""
Position linking service.
Manages the mapping between hiring tracker positions and CV Matching positions.
Links are stored in data/position-links.json (edited manually, no UI).
"""

import json
import os
from typing import Optional

from src.config.settings import POSITION_LINKS_FILE


def load_position_links() -> dict:
    """Load position links from JSON file. Returns {hiring_position: cv_matching_position}."""
    if not os.path.exists(POSITION_LINKS_FILE):
        return {}
    with open(POSITION_LINKS_FILE, "r") as f:
        return json.load(f)


def get_cv_position(job_position: str) -> Optional[str]:
    """Get the CV Matching position name for a hiring tracker position, or None if not linked."""
    links = load_position_links()
    return links.get(job_position)


def get_linked_positions() -> list:
    """Return list of (hiring_position, cv_matching_position) tuples for all linked positions."""
    return list(load_position_links().items())
