"""
Configuration settings for Kompas.com Hiring Tracker application.
Contains global constants, file paths, and default configurations.
"""

from typing import Dict, List

# File paths
CREDENTIALS_FILE = "credentials.json"
HIRING_DATA_FILE = "data/hiring-data.json"
HR_ROLES_FILE = "hr_roles.json"
LOGO_PATH = "assets/cqdybkxstovyrla2dje3.webp"

# Page configuration
PAGE_CONFIG = {
    "page_title": "Kompas.com Hiring Tracker",
    "layout": "wide"
}

# Base hiring stages
BASE_STAGES: List[str] = [
    "Initial Interview (HR)",
    "HR & User Interview (Stage 1)",
    "Skill Test",
    "Final Interview",
    "Offering",
    "Contract Sign",
    "On Boarding"
]

# Default credentials structure
DEFAULT_CREDENTIALS: Dict[str, str] = {
    "Product & Data Division": "product123",
    "Technology Engineering Division": "tech123"
}

# Default HR roles structure
DEFAULT_HR_ROLES: Dict = {
    "superadmin": {"username": "hrsuper", "password": "hrsuper123"},
    "admins": {
        "netri": {"password": "alia217", "name": "Netri Alia Rahmi"},
        "adel": {"password": "adel345", "name": "Adelia Galuh"},
    }
}

# Short usernames for division login (username -> full division name)
DIVISION_USERNAMES: Dict[str, str] = {
    "product-data": "Product & Data Division",
    "tech-eng": "Technology Engineering Division",
    "sales": "Sales",
    "marcomm": "Marketing Communication Kompas.com",
    "stratman": "Strategy Management",
    "ga": "General Affairs",
    "vcbl": "VCBL & Pasangiklan",
    "video-sosmed": "Kompas.com News - Video & Social Media Department",
    "lative": "Lative Ads Department",
    "marres": "Marketing Research Department",
    "creative": "Creative Department",
    "hr-media": "HR Media Division",
    "text": "Kompas.com News - Text Department",
    "sales-ops": "Sales Ops & Programmatic Division",
    "kompasiana": "Kompasiana",
    "stratx": "StratX Division",
    "sustainability": "Sustainability",
    "playz": "Playz Division",
}

# GitHub repository settings for data fallback
GITHUB_REPO = "netrialiarahmi/hiring-tracker"
GITHUB_BRANCHES = ["main", "master", "copilot/update-hiring-data-json"]

# GitHub repository settings for auto-backup
GITHUB_BACKUP_REPO = "netrialiarahmi/hiring-tracker-v2"
GITHUB_BACKUP_BRANCH = "main"
GITHUB_BACKUP_ENABLED = True  # Enable/disable GitHub auto-backup

# Validation constraints
MIN_PASSWORD_LENGTH = 4
PROTECTED_DIVISION = ""  # No protected division by default

# Session state keys
SESSION_KEYS = [
    "credentials",
    "hiring_data",
    "logged_in",
    "user_division",
    "role",
    "hr_admin",
    "editing_user",
    "deleting_user"
]

# Role types
ROLE_SUPERADMIN = "HR Superadmin"
ROLE_ADMIN = "HR Admin"
ROLE_DIVISION = "Division"

# Query parameter keys
QP_LOGGED_IN = "logged_in"
QP_USER_DIVISION = "user_division"
QP_ROLE = "role"
QP_ROLE_TYPE = "role_type"
QP_HR_ADMIN = "hr_admin"
QP_LOGOUT = "logout"

# CV Matching integration settings
CV_MATCHING_REPO = "netrialiarahmi/cv-matching-auto"
CV_MATCHING_BRANCH = "main"
CV_MATCHING_RESULTS_DIR = "data/processed"
CV_MATCHING_POSITIONS_FILE = "data/job_positions.csv"
CANDIDATES_FILE = "data/candidates.json"
POSITION_LINKS_FILE = "data/position-links.json"

# Candidate status constants
CANDIDATE_STATUS_PENDING = "Pending"
CANDIDATE_STATUS_ESCALATED = "Escalated"
CANDIDATE_STATUS_INTERVIEW = "Interview"
CANDIDATE_STATUS_APPROVED = "Approved"
CANDIDATE_STATUS_REJECTED = "Rejected"
