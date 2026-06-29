"""
Division lookup service.

Resolves a hiring `Job Position` (job title from Planner) to its canonical
division/directorate/department/section using the table built from the latest
Kompas Employee Report (see `scripts/build_division_lookup.py`).

The same JSON payload (`data/division_lookup.json`) is also consumed by the
JavaScript Planner sync (`scripts/division-lookup.js`).
"""

from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from typing import Dict, Optional

LOOKUP_PATH = os.path.join("data", "division_lookup.json")

_PREFIXES = (
    "sr.", "sr ", "senior ",
    "jr.", "jr ", "junior ",
    "asst.", "asst ", "assistant ",
    "deputy ",
    "lead ", "head of ", "chief ",
    "general manager", "gm ",
    "managing ",
)

_MANUAL_DIVISION_FALLBACKS = (
    (re.compile(r"\bdata analyst\b.*\bbi\b", re.IGNORECASE), "Strategy Management Division"),
    (re.compile(r"\bbusiness development\b", re.IGNORECASE), "Strategy Management Division"),
)


def normalize_title(title: str) -> str:
    """Match the normalization used by `scripts/build_division_lookup.py`."""
    if not title:
        return ""
    t = str(title).lower().strip()
    t = re.sub(r"\([^)]*\)", " ", t)
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    for p in _PREFIXES:
        if t.startswith(p):
            t = t[len(p):].strip()
            break
    return t


@lru_cache(maxsize=1)
def load_division_lookup() -> Dict[str, dict]:
    """Load and cache the division lookup table. Returns {} when missing."""
    if not os.path.exists(LOOKUP_PATH):
        return {}
    try:
        with open(LOOKUP_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    return payload.get("entries", {}) if isinstance(payload, dict) else {}


def _token_set_match(query: str, entries: Dict[str, dict]) -> Optional[str]:
    """Fallback fuzzy match: pick the entry whose token set has the highest overlap."""
    q_tokens = set(query.split())
    if not q_tokens:
        return None
    best_key = None
    best_score = 0.0
    for key in entries.keys():
        k_tokens = set(key.split())
        if not k_tokens:
            continue
        overlap = len(q_tokens & k_tokens)
        if overlap >= 2 or (overlap >= 1 and (q_tokens <= k_tokens or k_tokens <= q_tokens)):
            score = overlap / max(len(q_tokens), len(k_tokens))
            if score > best_score:
                best_score = score
                best_key = key
    return best_key if best_score >= 0.5 else None


def _manual_division_fallback(job_position: str) -> Optional[dict]:
    """Apply fixed manual fallback rules for known position naming patterns."""
    source_text = (job_position or "").strip()
    if not source_text:
        return None

    for pattern, division in _MANUAL_DIVISION_FALLBACKS:
        if pattern.search(source_text):
            return {
                "division": division,
                "directorate": "",
                "department": "",
                "section": "",
                "source": "manual_fallback",
            }
    return None


def resolve_division(job_position: str, current_division: str = "") -> dict:
    """
    Resolve the canonical division hierarchy for a given job title.

    Returns a dict with keys:
        division, directorate, department, section, source

    `source` is one of:
        - "lookup_exact"    — exact-match on normalized title
        - "lookup_fuzzy"    — token-set fallback match
        - "planner"         — no lookup match; falls back to the Planner-supplied division
    """
    entries = load_division_lookup()
    fallback = {
        "division": current_division or "",
        "directorate": "",
        "department": "",
        "section": "",
        "source": "planner",
    }
    manual = _manual_division_fallback(job_position)
    if manual:
        return manual

    if not entries or not job_position:
        return fallback

    key = normalize_title(job_position)
    hit = entries.get(key)
    if hit:
        return {
            "division": hit.get("division", ""),
            "directorate": hit.get("directorate", ""),
            "department": hit.get("department", ""),
            "section": hit.get("section", ""),
            "source": "lookup_exact",
        }

    fuzzy_key = _token_set_match(key, entries)
    if fuzzy_key:
        hit = entries[fuzzy_key]
        return {
            "division": hit.get("division", ""),
            "directorate": hit.get("directorate", ""),
            "department": hit.get("department", ""),
            "section": hit.get("section", ""),
            "source": "lookup_fuzzy",
        }

    return fallback


def suggest_correction(job_position: str, current_division: str) -> Optional[dict]:
    """
    Return a suggested correction when the lookup-derived division differs
    from `current_division`. Returns None when they agree or no suggestion exists.
    """
    resolved = resolve_division(job_position, current_division)
    if resolved["source"] == "planner" or not resolved["division"]:
        return None
    if (current_division or "").strip().lower() == resolved["division"].strip().lower():
        return None
    return resolved
