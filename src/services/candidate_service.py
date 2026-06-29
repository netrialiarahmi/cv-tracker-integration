"""
Candidate management service.
Business logic for escalating candidates, adding comments, and fetching screening results.
"""

import os
import json
import requests
import pandas as pd
from io import StringIO
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.config.settings import (
    CV_MATCHING_REPO, CV_MATCHING_BRANCH, CANDIDATES_FILE,
    CV_MATCHING_RESULTS_DIR, CV_MATCHING_POSITIONS_FILE
)
from src.models.candidate import Candidate


def _normalize_text(value: Any) -> str:
    """Normalize free-text fields for case-insensitive matching."""
    return str(value or "").strip().lower()


def _load_position_division_map() -> Dict[str, str]:
    """Build canonical position -> division mapping from hiring-data.json."""
    try:
        from src.repositories.data_manager import load_hiring_data

        df = load_hiring_data()
        if df is None or df.empty:
            return {}

        mapping: Dict[str, str] = {}
        for _, row in df.iterrows():
            pos = _normalize_text(row.get("Job Position", ""))
            div = str(row.get("Division", "")).strip()
            if pos and div:
                mapping[pos] = div
        return mapping
    except Exception:
        return {}


def _get_github_token() -> Optional[str]:
    """Get GitHub token from environment or Streamlit secrets."""
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        import streamlit as st
        return st.secrets.get("GITHUB_TOKEN")
    except Exception:
        return None


def _get_github_headers() -> dict:
    """Get GitHub API headers."""
    token = _get_github_token()
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def load_candidates() -> List[Dict[str, Any]]:
    """Load escalated candidates from local JSON file."""
    if os.path.exists(CANDIDATES_FILE):
        try:
            with open(CANDIDATES_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            pass
    return []


def save_candidates(candidates: List[Dict[str, Any]]) -> None:
    """Save candidates to local JSON file and backup to GitHub."""
    os.makedirs(os.path.dirname(CANDIDATES_FILE), exist_ok=True)
    with open(CANDIDATES_FILE, "w") as f:
        json.dump(candidates, f, indent=4)
    _backup_candidates_to_github(candidates)


def _backup_candidates_to_github(candidates: List[Dict[str, Any]]) -> bool:
    """Backup candidates.json to the hiring-tracker-v2 GitHub repo."""
    from src.config.settings import GITHUB_BACKUP_REPO, GITHUB_BACKUP_BRANCH, GITHUB_BACKUP_ENABLED
    import base64

    if not GITHUB_BACKUP_ENABLED:
        return False

    token = _get_github_token()
    if not token:
        return False

    try:
        file_content = json.dumps(candidates, indent=4)
        encoded_content = base64.b64encode(file_content.encode()).decode()
        api_url = f"https://api.github.com/repos/{GITHUB_BACKUP_REPO}/contents/{CANDIDATES_FILE}"
        headers = _get_github_headers()

        sha = None
        try:
            response = requests.get(api_url, headers=headers, params={"ref": GITHUB_BACKUP_BRANCH}, timeout=10)
            if response.status_code == 200:
                sha = response.json().get("sha")
        except Exception:
            pass

        commit_data = {
            "message": f"Auto-backup: Update candidates.json - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "content": encoded_content,
            "branch": GITHUB_BACKUP_BRANCH,
        }
        if sha:
            commit_data["sha"] = sha

        response = requests.put(api_url, headers=headers, json=commit_data, timeout=30)
        return response.status_code in [200, 201]
    except Exception:
        return False


def fetch_screening_results(position_name: str) -> Optional[pd.DataFrame]:
    """
    Fetch screening results for a position from the cv-matching-auto repo.
    Reads the position-specific results CSV via GitHub API.
    """
    import re
    safe_name = re.sub(r'[^\w\s]', '', position_name)
    safe_name = re.sub(r'\s+', '_', safe_name)
    safe_name = re.sub(r'_+', '_', safe_name)
    path = f"{CV_MATCHING_RESULTS_DIR}/results_{safe_name}.csv"

    headers = _get_github_headers()
    raw_url = f"https://raw.githubusercontent.com/{CV_MATCHING_REPO}/{CV_MATCHING_BRANCH}/{path}"

    try:
        response = requests.get(raw_url, headers=headers, timeout=15)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df
    except Exception:
        pass

    return None


def fetch_job_positions_from_cv_matching() -> Optional[pd.DataFrame]:
    """
    Fetch job_positions.csv from cv-matching-auto repo.
    Returns DataFrame with position names and descriptions.
    """
    headers = _get_github_headers()
    raw_url = f"https://raw.githubusercontent.com/{CV_MATCHING_REPO}/{CV_MATCHING_BRANCH}/{CV_MATCHING_POSITIONS_FILE}"

    try:
        response = requests.get(raw_url, headers=headers, timeout=15)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df
    except Exception:
        pass

    return None


def escalate_candidate(screening_row: Dict[str, Any], position_key: str,
                       division: str, escalated_by: str) -> Candidate:
    """
    Escalate a candidate from screening results to the hiring tracker.
    Creates a Candidate record and saves it.
    """
    candidate = Candidate.from_screening_result(
        screening_row, position_key, division, escalated_by
    )
    candidates = load_candidates()

    # Check for duplicate (same email + position)
    for existing in candidates:
        if (existing.get("email") == candidate.email and
                existing.get("position_key") == candidate.position_key and
                candidate.email):
            return Candidate(existing)  # Already escalated

    candidates.append(candidate.to_dict())
    save_candidates(candidates)
    return candidate


def add_comment_to_candidate(candidate_id: str, author: str, division: str,
                             text: str, action: str = "comment") -> bool:
    """Add a comment to an existing candidate and update their status if needed."""
    candidates = load_candidates()
    for i, c in enumerate(candidates):
        if c.get("id") == candidate_id:
            candidate = Candidate(c)
            candidate.add_comment(author, division, text, action)

            if action == "approve":
                candidate.status = Candidate.STATUS_APPROVED
            elif action == "reject":
                candidate.status = Candidate.STATUS_REJECTED

            candidates[i] = candidate.to_dict()
            save_candidates(candidates)
            return True
    return False


def update_candidate_status(candidate_id: str, new_status: str) -> bool:
    """Update a candidate's status."""
    candidates = load_candidates()
    for i, c in enumerate(candidates):
        if c.get("id") == candidate_id:
            c["status"] = new_status
            candidates[i] = c
            save_candidates(candidates)
            return True
    return False


def submit_skill_review(
    candidate_id: str,
    reviewer_division: str,
    reviewer: str,
    ratings: Dict[str, int],
    note: str,
    decision: str,
) -> bool:
    """Persist a Division-side skill review for a candidate.

    ratings: {"soft_skill": 1-4, "value_kg": 1-4, "technical_skill": 1-4}
    decision: one of Candidate.STATUS_RECOMMENDED / STATUS_NOT_RECOMMENDED / STATUS_RESERVE
    """
    valid_decisions = {
        Candidate.STATUS_RECOMMENDED,
        Candidate.STATUS_NOT_RECOMMENDED,
        Candidate.STATUS_RESERVE,
    }
    if decision not in valid_decisions:
        return False

    def _clamp(v):
        try:
            v = int(v)
        except (TypeError, ValueError):
            return 1
        return max(1, min(4, v))

    entry = {
        "soft_skill": _clamp(ratings.get("soft_skill", 1)),
        "value_kg": _clamp(ratings.get("value_kg", 1)),
        "technical_skill": _clamp(ratings.get("technical_skill", 1)),
        "technical_skills": {
            k: _clamp(v) for k, v in (ratings.get("technical_skills") or {}).items()
        },
        "note": (note or "").strip(),
        "decision": decision,
        "reviewer": reviewer,
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    candidates = load_candidates()
    for i, c in enumerate(candidates):
        if c.get("id") != candidate_id:
            continue

        candidate = Candidate(c)
        candidate.skill_ratings[reviewer_division] = entry
        candidate.status = decision

        # Mirror the review as a comment so HR sees the trail
        tech_str = ""
        if entry["technical_skills"]:
            parts = [f"<li style='margin-bottom:0.15rem;'>{k}: <strong>{v}/4</strong></li>" for k, v in entry["technical_skills"].items()]
            tech_str = f"<strong>Technical Skills:</strong><ul style='margin-top:0.25rem;margin-bottom:0.25rem;padding-left:1.5rem;'>{''.join(parts)}</ul>"
        else:
            tech_str = f"<strong>Technical Skill:</strong> {entry['technical_skill']}/4<br>"

        summary = (
            f"<div style='line-height:1.5;'>"
            f"<strong>Skill review:</strong><br>"
            f"Soft Skill: <strong>{entry['soft_skill']}/4</strong><br>"
            f"Value KG: <strong>{entry['value_kg']}/4</strong><br>"
            f"{tech_str}"
            f"Decision: <span style='font-weight:600;color:#2563eb;'>{decision}</span>"
        )
        if entry["note"]:
            summary += f"<br><br><strong>Catatan:</strong><br>{entry['note']}"
        summary += "</div>"
        
        candidate.add_comment(reviewer, reviewer_division, summary, action="review")

        candidates[i] = candidate.to_dict()
        save_candidates(candidates)
        return True
    return False


def reset_candidate_status(candidate_id: str) -> bool:
    """Reset a candidate's status back to Escalated (undo approve/reject)."""
    return update_candidate_status(candidate_id, Candidate.STATUS_ESCALATED)


def clear_candidate_comments(candidate_id: str) -> bool:
    """Clear all comments from a candidate."""
    candidates = load_candidates()
    for i, c in enumerate(candidates):
        if c.get("id") == candidate_id:
            c["comments"] = []
            candidates[i] = c
            save_candidates(candidates)
            return True
    return False


def delete_candidate(candidate_id: str) -> bool:
    """Remove a candidate entirely (undo escalation)."""
    candidates = load_candidates()
    new_candidates = [c for c in candidates if c.get("id") != candidate_id]
    if len(new_candidates) < len(candidates):
        save_candidates(new_candidates)
        return True
    return False


def get_candidates_for_position(position_key: str) -> List[Candidate]:
    """Get all escalated candidates for a specific position."""
    candidates = load_candidates()
    return [
        Candidate(c) for c in candidates
        if c.get("position_key") == position_key
    ]


def get_candidates_for_division(division: str) -> List[Candidate]:
    """Get all escalated candidates for a specific division."""
    candidates = load_candidates()
    target_division = _normalize_text(division)
    position_division_map = _load_position_division_map()

    from src.services.division import resolve_division

    scoped: List[Candidate] = []
    for c in candidates:
        if _normalize_text(c.get("status", "")) == "transferred":
            continue

        position_key = _normalize_text(c.get("position_key", ""))
        effective_division = c.get("division", "")

        # Reconcile stale candidate division with the canonical division
        # currently assigned to that position in hiring-data.json.
        canonical = position_division_map.get(position_key, "")
        if canonical:
            effective_division = canonical
        else:
            resolved = resolve_division(c.get("position_key", ""), str(effective_division or ""))
            if resolved.get("division"):
                effective_division = resolved["division"]

        if _normalize_text(effective_division) == target_division:
            scoped.append(Candidate(c))

    return scoped
