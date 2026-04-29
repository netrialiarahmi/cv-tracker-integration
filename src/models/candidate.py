"""
Candidate data models for CV Matching integration.
Represents candidates escalated from HR screening to user interview.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class CandidateComment:
    """Represents a single comment on a candidate."""

    def __init__(self, data: Dict[str, Any]):
        self.author = data.get("author", "")
        self.division = data.get("division", "")
        self.text = data.get("text", "")
        self.timestamp = data.get("timestamp", "")
        self.action = data.get("action", "")  # "comment", "approve", "reject"

    def to_dict(self) -> dict:
        return {
            "author": self.author,
            "division": self.division,
            "text": self.text,
            "timestamp": self.timestamp,
            "action": self.action,
        }


class Candidate:
    """Represents a candidate escalated from CV Matching screening."""

    # Status constants
    STATUS_PENDING = "Pending"
    STATUS_ESCALATED = "Escalated"
    STATUS_INTERVIEW = "Interview"
    # Legacy values (kept for backwards compatibility with existing data)
    STATUS_APPROVED = "Approved"
    STATUS_REJECTED = "Rejected"
    # New decision values used by the Division dashboard review flow
    STATUS_RECOMMENDED = "Rekomendasi"
    STATUS_NOT_RECOMMENDED = "Tidak Direkomendasi"
    STATUS_RESERVE = "Cadangan"

    # Map legacy → new value at read time so existing candidates.json renders
    # with the new labels without a data migration.
    LEGACY_STATUS_MAP = {
        STATUS_APPROVED: STATUS_RECOMMENDED,
        STATUS_REJECTED: STATUS_NOT_RECOMMENDED,
    }

    # Decision values that mark a candidate as actioned (not pending review)
    ACTIONED_STATUSES = (
        STATUS_APPROVED, STATUS_REJECTED,
        STATUS_RECOMMENDED, STATUS_NOT_RECOMMENDED, STATUS_RESERVE,
    )

    ALL_STATUSES = [
        STATUS_PENDING, STATUS_ESCALATED, STATUS_INTERVIEW,
        STATUS_RECOMMENDED, STATUS_NOT_RECOMMENDED, STATUS_RESERVE,
    ]

    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", "")
        self.name = data.get("name", "")
        self.email = data.get("email", "")
        self.phone = data.get("phone", "")
        self.match_score = data.get("match_score", 0)
        self.ai_summary = data.get("ai_summary", "")
        self.strengths = data.get("strengths", [])
        self.weaknesses = data.get("weaknesses", [])
        self.gaps = data.get("gaps", [])
        self.resume_link = data.get("resume_link", "")
        self.kalibrr_link = data.get("kalibrr_link", "")
        self.application_link = data.get("application_link", "")
        self.latest_job_title = data.get("latest_job_title", "")
        self.latest_company = data.get("latest_company", "")
        self.education = data.get("education", "")
        self.university = data.get("university", "")
        self.major = data.get("major", "")
        raw_status = data.get("status", self.STATUS_ESCALATED)
        # Normalize legacy statuses to the new labels at read time
        self.status = self.LEGACY_STATUS_MAP.get(raw_status, raw_status)
        self.position_key = data.get("position_key", "")
        self.division = data.get("division", "")
        self.escalated_by = data.get("escalated_by", "")
        self.escalated_at = data.get("escalated_at", "")
        self.date_applied = data.get("date_applied", "")
        self.date_processed = data.get("date_processed", "")
        # Per-division skill review entries:
        # { "<reviewer_division>": {soft_skill, value_kg, technical_skill,
        #                          note, decision, reviewer, submitted_at} }
        ratings = data.get("skill_ratings") or {}
        self.skill_ratings: Dict[str, Dict[str, Any]] = (
            ratings if isinstance(ratings, dict) else {}
        )
        self.comments = [
            CandidateComment(c) if isinstance(c, dict) else c
            for c in data.get("comments", [])
        ]

    def add_comment(self, author: str, division: str, text: str, action: str = "comment") -> None:
        comment = CandidateComment({
            "author": author,
            "division": division,
            "text": text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
        })
        self.comments.append(comment)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "match_score": self.match_score,
            "ai_summary": self.ai_summary,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "gaps": self.gaps,
            "resume_link": self.resume_link,
            "kalibrr_link": self.kalibrr_link,
            "application_link": self.application_link,
            "latest_job_title": self.latest_job_title,
            "latest_company": self.latest_company,
            "education": self.education,
            "university": self.university,
            "major": self.major,
            "status": self.status,
            "position_key": self.position_key,
            "division": self.division,
            "escalated_by": self.escalated_by,
            "escalated_at": self.escalated_at,
            "date_applied": self.date_applied,
            "date_processed": self.date_processed,
            "skill_ratings": self.skill_ratings,
            "comments": [c.to_dict() for c in self.comments],
        }

    @staticmethod
    def from_screening_result(row: Dict[str, Any], position_key: str, division: str, escalated_by: str) -> "Candidate":
        """Create a Candidate from a CV Matching screening result row."""
        # Parse strengths/weaknesses/gaps from semicolon-separated strings
        def parse_list(val):
            if isinstance(val, list):
                return val
            if isinstance(val, str) and val.strip():
                return [s.strip() for s in val.split(";") if s.strip()]
            return []

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        email = str(row.get("Candidate Email", "")).strip()
        name = str(row.get("Candidate Name", "")).strip()
        candidate_id = f"{position_key}_{email or name}_{now}".replace(" ", "_")

        return Candidate({
            "id": candidate_id,
            "name": name,
            "email": email,
            "phone": str(row.get("Phone", "")).strip(),
            "match_score": int(row.get("Match Score", 0)) if row.get("Match Score") else 0,
            "ai_summary": str(row.get("AI Summary", "")).strip(),
            "strengths": parse_list(row.get("Strengths", [])),
            "weaknesses": parse_list(row.get("Weaknesses", [])),
            "gaps": parse_list(row.get("Gaps", [])),
            "resume_link": str(row.get("Resume Link", "")).strip(),
            "kalibrr_link": str(row.get("Kalibrr Profile", "")).strip(),
            "application_link": str(row.get("Application Link", "")).strip(),
            "latest_job_title": str(row.get("Latest Job Title", "")).strip(),
            "latest_company": str(row.get("Latest Company", "")).strip(),
            "education": str(row.get("Education", "")).strip(),
            "university": str(row.get("University", "")).strip(),
            "major": str(row.get("Major", "")).strip(),
            "status": Candidate.STATUS_ESCALATED,
            "position_key": position_key,
            "division": division,
            "escalated_by": escalated_by,
            "escalated_at": now,
            "date_applied": str(row.get("Date Applied", "")).strip(),
            "date_processed": str(row.get("Date Processed", "")).strip(),
            "comments": [],
        })
