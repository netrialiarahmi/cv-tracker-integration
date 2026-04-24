"""
Feedback model for CV Matching prompt adjustment.
Aggregates user comments into adjusted job requirements.
"""

from typing import List, Dict, Any
from datetime import datetime


class UserFeedbackEntry:
    """A single feedback entry from a division user."""

    def __init__(self, data: Dict[str, Any]):
        self.author = data.get("author", "")
        self.division = data.get("division", "")
        self.candidate_name = data.get("candidate_name", "")
        self.action = data.get("action", "")  # "approve", "reject", "comment"
        self.text = data.get("text", "")
        self.timestamp = data.get("timestamp", "")

    def to_dict(self) -> dict:
        return {
            "author": self.author,
            "division": self.division,
            "candidate_name": self.candidate_name,
            "action": self.action,
            "text": self.text,
            "timestamp": self.timestamp,
        }


class PositionFeedback:
    """Aggregated feedback for a specific position, used to adjust AI prompts."""

    def __init__(self, data: Dict[str, Any]):
        self.position_name = data.get("position_name", "")
        self.division = data.get("division", "")
        self.original_requirements = data.get("original_requirements", "")
        self.user_feedback = [
            UserFeedbackEntry(f) if isinstance(f, dict) else f
            for f in data.get("user_feedback", [])
        ]
        self.adjusted_requirements = data.get("adjusted_requirements", "")
        self.last_updated = data.get("last_updated", "")

    def add_feedback(self, author: str, division: str, candidate_name: str,
                     action: str, text: str) -> None:
        entry = UserFeedbackEntry({
            "author": author,
            "division": division,
            "candidate_name": candidate_name,
            "action": action,
            "text": text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        self.user_feedback.append(entry)
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._regenerate_adjusted_requirements()

    def _regenerate_adjusted_requirements(self) -> None:
        """Regenerate adjusted requirements from original + all feedback."""
        if not self.user_feedback:
            self.adjusted_requirements = self.original_requirements
            return

        rejection_reasons = []
        approval_qualities = []
        general_comments = []

        for fb in self.user_feedback:
            if fb.action == "reject" and fb.text:
                rejection_reasons.append(f"- {fb.candidate_name}: {fb.text}")
            elif fb.action == "approve" and fb.text:
                approval_qualities.append(f"- {fb.candidate_name}: {fb.text}")
            elif fb.action == "comment" and fb.text:
                general_comments.append(f"- {fb.candidate_name}: {fb.text}")

        sections = [self.original_requirements]

        if rejection_reasons:
            sections.append(
                "\n\n--- USER INTERVIEW FEEDBACK (Rejection Reasons) ---\n"
                "Previous candidates were rejected for the following reasons. "
                "Deprioritize candidates with similar issues:\n"
                + "\n".join(rejection_reasons)
            )

        if approval_qualities:
            sections.append(
                "\n\n--- USER INTERVIEW FEEDBACK (Approved Qualities) ---\n"
                "The following qualities were noted in approved candidates. "
                "Prioritize candidates with similar attributes:\n"
                + "\n".join(approval_qualities)
            )

        if general_comments:
            sections.append(
                "\n\n--- USER INTERVIEW FEEDBACK (General Notes) ---\n"
                "Additional notes from hiring managers:\n"
                + "\n".join(general_comments)
            )

        self.adjusted_requirements = "\n".join(sections)

    def to_dict(self) -> dict:
        return {
            "position_name": self.position_name,
            "division": self.division,
            "original_requirements": self.original_requirements,
            "user_feedback": [f.to_dict() for f in self.user_feedback],
            "adjusted_requirements": self.adjusted_requirements,
            "last_updated": self.last_updated,
        }
