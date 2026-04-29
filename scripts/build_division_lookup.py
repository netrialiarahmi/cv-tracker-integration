"""
Build data/division_lookup.json from the latest Kompas employee report.

Reads `data/2025 Employee Report(08 April 2026).csv` (semicolon-delimited)
and produces a JSON keyed by normalized job title with the resolved
{division, directorate, department, section} hierarchy.

The same JSON is consumed by:
- src/services/division.py (Python runtime)
- scripts/division-lookup.js (Planner sync)

Re-run this whenever a fresher employee report lands in data/.
"""

from __future__ import annotations

import csv
import glob
import json
import os
import re
import sys
from collections import Counter
from typing import Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
OUTPUT_PATH = os.path.join(DATA_DIR, "division_lookup.json")

# Seniority / role-modifier prefixes to strip when normalizing job titles.
PREFIXES = [
    "sr.", "sr ", "senior ",
    "jr.", "jr ", "junior ",
    "asst.", "asst ", "assistant ",
    "deputy ",
    "lead ", "head of ", "chief ",
    "general manager", "gm ",
    "managing ",
]


def normalize_title(title: str) -> str:
    """Lowercase, strip seniority modifiers and punctuation, collapse spaces."""
    if not title:
        return ""
    t = title.lower().strip()
    # Remove parenthetical qualifiers
    t = re.sub(r"\([^)]*\)", " ", t)
    # Remove punctuation (keep spaces and word chars)
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    # Strip seniority prefixes (one pass; common cases)
    for p in PREFIXES:
        if t.startswith(p):
            t = t[len(p):].strip()
            break
    return t


def find_latest_employee_report() -> str | None:
    """Pick the most-recently-modified Employee Report CSV in data/."""
    candidates = sorted(
        glob.glob(os.path.join(DATA_DIR, "*Employee Report*.csv")),
        key=os.path.getmtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def build_lookup(csv_path: str) -> Dict[str, dict]:
    """
    Build {normalized_title: {division, directorate, department, section,
                              source: 'employee_report', sample_count: N}}.
    For titles that map to multiple divisions across employees, pick the most
    common one and record the count for transparency.
    """
    counter: Dict[str, Counter] = {}
    samples: Dict[str, dict] = {}

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            title_raw = (row.get("Posisi") or "").strip()
            division = (row.get("Division") or "").strip()
            if not title_raw or not division:
                continue
            key = normalize_title(title_raw)
            if not key:
                continue
            sig = (
                division,
                (row.get("Directorate") or "").strip(),
                (row.get("Department") or "").strip(),
                (row.get("Section") or "").strip(),
            )
            counter.setdefault(key, Counter())[sig] += 1
            # Keep the *first* observed raw title as a display sample
            samples.setdefault(key, {"raw_title": title_raw})

    lookup: Dict[str, dict] = {}
    for key, sigs in counter.items():
        ((division, directorate, department, section), count) = sigs.most_common(1)[0]
        lookup[key] = {
            "division": division,
            "directorate": directorate,
            "department": department,
            "section": section,
            "raw_title": samples[key]["raw_title"],
            "sample_count": count,
            "ambiguity_count": len(sigs),
            "source": "employee_report",
        }
    return lookup


def main() -> int:
    csv_path = find_latest_employee_report()
    if not csv_path:
        print("ERROR: No 'Employee Report' CSV found under data/", file=sys.stderr)
        return 1

    print(f"Reading: {csv_path}")
    lookup = build_lookup(csv_path)
    print(f"Built lookup for {len(lookup)} normalized job titles")

    payload = {
        "_meta": {
            "source_file": os.path.basename(csv_path),
            "entry_count": len(lookup),
        },
        "entries": lookup,
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Wrote: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
