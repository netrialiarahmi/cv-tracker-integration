"""
Feedback service for adjusting CV Matching prompts based on user comments.
Aggregates feedback and syncs to the cv-matching-auto repo.
"""

import os
import json
import base64
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List
from config.settings import CV_MATCHING_REPO, CV_MATCHING_BRANCH
from models.feedback import PositionFeedback

FEEDBACK_FILE = "data/feedback.json"


def _get_github_token() -> Optional[str]:
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        import streamlit as st
        return st.secrets.get("GITHUB_TOKEN")
    except Exception:
        return None


def load_all_feedback() -> Dict[str, Dict[str, Any]]:
    """Load all position feedback from local JSON file. Keyed by position_name."""
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            pass
    return {}


def save_all_feedback(feedback_data: Dict[str, Dict[str, Any]]) -> None:
    """Save all feedback to local JSON file."""
    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback_data, f, indent=4)


def get_position_feedback(position_name: str) -> Optional[PositionFeedback]:
    """Get feedback for a specific position."""
    all_feedback = load_all_feedback()
    if position_name in all_feedback:
        return PositionFeedback(all_feedback[position_name])
    return None


def add_feedback_for_position(position_name: str, division: str,
                              original_requirements: str, author: str,
                              candidate_name: str, action: str, text: str) -> PositionFeedback:
    """
    Add feedback entry for a position and regenerate adjusted requirements.
    Creates the PositionFeedback if it doesn't exist yet.
    """
    all_feedback = load_all_feedback()

    if position_name in all_feedback:
        pf = PositionFeedback(all_feedback[position_name])
    else:
        pf = PositionFeedback({
            "position_name": position_name,
            "division": division,
            "original_requirements": original_requirements,
        })

    pf.add_feedback(author, division, candidate_name, action, text)
    all_feedback[position_name] = pf.to_dict()
    save_all_feedback(all_feedback)

    # Auto-sync to cv-matching-auto repo
    sync_feedback_to_cv_matching(position_name, pf)

    return pf


def sync_feedback_to_cv_matching(position_name: str, feedback: PositionFeedback) -> bool:
    """
    Push feedback JSON to the cv-matching-auto repo.
    Writes to feedback/{position_safe_name}.json so auto_screen.py can read it.
    """
    import re
    token = _get_github_token()
    if not token:
        return False

    safe_name = re.sub(r'[^\w\s]', '', position_name)
    safe_name = re.sub(r'\s+', '_', safe_name)
    safe_name = re.sub(r'_+', '_', safe_name)
    path = f"feedback/{safe_name}.json"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    api_url = f"https://api.github.com/repos/{CV_MATCHING_REPO}/contents/{path}"

    try:
        file_content = json.dumps(feedback.to_dict(), indent=4)
        encoded_content = base64.b64encode(file_content.encode()).decode()

        # Check if file exists
        sha = None
        try:
            response = requests.get(api_url, headers=headers,
                                    params={"ref": CV_MATCHING_BRANCH}, timeout=10)
            if response.status_code == 200:
                sha = response.json().get("sha")
        except Exception:
            pass

        commit_data = {
            "message": f"Update feedback for {position_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "content": encoded_content,
            "branch": CV_MATCHING_BRANCH,
        }
        if sha:
            commit_data["sha"] = sha

        response = requests.put(api_url, headers=headers, json=commit_data, timeout=30)
        return response.status_code in [200, 201]
    except Exception:
        return False
