"""
Resume link utilities.
Handles detection and fallback for expired GCS signed URLs.
"""

import time
from urllib.parse import urlparse, parse_qs


def is_gcs_signed_url(url: str) -> bool:
    """Check if a URL is a Google Cloud Storage signed URL."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        return (
            parsed.scheme in {"http", "https"}
            and "storage.googleapis.com" in parsed.netloc
            and ("Expires" in parsed.query or "X-Goog-Expires" in parsed.query
                 or "X-Goog-Date" in parsed.query)
        )
    except Exception:
        return False


def is_gcs_url_expired(url: str) -> bool:
    """Check if a GCS signed URL has expired.

    Supports both V2 (Expires=epoch) and V4 (X-Goog-Date + X-Goog-Expires) signing.
    Returns False for non-GCS URLs or URLs without expiration info.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        params = parse_qs(parsed.query)

        # V2 signed URL: has "Expires" parameter (Unix epoch seconds)
        expires_values = params.get("Expires", [])
        if expires_values:
            try:
                return int(expires_values[0]) < int(time.time())
            except (TypeError, ValueError):
                return False

        # V4 signed URL: has "X-Goog-Date" and "X-Goog-Expires" parameters
        goog_date = params.get("X-Goog-Date", [])
        goog_expires = params.get("X-Goog-Expires", [])
        if goog_date and goog_expires:
            try:
                from datetime import datetime
                import calendar
                # X-Goog-Date format: 20250509T183203Z
                dt = datetime.strptime(goog_date[0], "%Y%m%dT%H%M%SZ")
                expires_seconds = int(goog_expires[0])
                expiry_time = calendar.timegm(dt.timetuple()) + expires_seconds
                
                # Check if it really expired
                return expiry_time < time.time()
            except (ValueError, TypeError):
                return False

        return False
    except Exception:
        return False


def get_resume_display_info(resume_link: str, application_link: str = "",
                            kalibrr_link: str = ""):
    """Determine the best available link and label for viewing a resume.

    Returns:
        tuple: (url, label, is_expired)
            - url: The best URL to use (resume if valid, fallback otherwise)
            - label: Display label for the link
            - is_expired: True if the original resume link was expired
    """
    # No resume link at all
    if not resume_link or not resume_link.strip():
        if application_link and application_link.strip():
            return application_link.strip(), "Resume (via Kalibrr)", False
        if kalibrr_link and kalibrr_link.strip():
            return kalibrr_link.strip(), "Resume (via Profile)", False
        return "", "", False

    resume_link = resume_link.strip()

    # Check if it's an expired GCS signed URL
    if is_gcs_signed_url(resume_link) and is_gcs_url_expired(resume_link):
        # Fallback to application link or kalibrr profile
        if application_link and application_link.strip():
            return application_link.strip(), "Resume (via Kalibrr)", True
        if kalibrr_link and kalibrr_link.strip():
            return kalibrr_link.strip(), "Resume (via Profile)", True
        return "", "", True

    # Resume link is still valid — show as direct PDF
    return resume_link, "Resume (PDF)", False
