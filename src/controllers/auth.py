"""
Authentication logic for HR roles and division users.
Handles login validation, logout, and HR roles configuration loading.
"""

import streamlit as st
import os
import json
import hashlib
from typing import Dict, Any, Optional
from src.config.settings import HR_ROLES_FILE, DEFAULT_HR_ROLES, DIVISION_USERNAMES
from src.controllers.session_manager import qp_clear

_HASH_SALT = "kgmedia26:"


def _check_password(plain: str, stored: str) -> bool:
    """Compare a plain-text password against a stored value (plain or sha256: hash)."""
    if stored.startswith("sha256:"):
        return stored == "sha256:" + hashlib.sha256((_HASH_SALT + plain).encode()).hexdigest()
    return plain == stored


def hash_password(plain: str) -> str:
    """Return sha256-hashed password for storage in credentials.json."""
    return "sha256:" + hashlib.sha256((_HASH_SALT + plain).encode()).hexdigest()


def get_hr_roles() -> Dict[str, Any]:
    """
    Load HR roles configuration from multiple sources with priority:
    1. hr_roles.json (runtime-managed source of truth)
    2. .streamlit/secrets.toml (for manual edits)
    3. st.secrets (Streamlit-managed)
    4. Default values
    
    Returns:
        Dictionary containing superadmin and admins configuration
    """
    # 1) Prefer runtime-managed JSON in repo/workspace.
    if os.path.exists(HR_ROLES_FILE):
        try:
            with open(HR_ROLES_FILE, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if isinstance(payload, dict):
                return payload
        except Exception:
            # Continue to other providers when file is malformed/unreadable.
            pass

    # 2) Try reading .streamlit/secrets.toml
    toml_path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(toml_path):
        try:
            try:
                import tomllib as toml  # Python 3.11+
            except Exception:
                import toml  # fallback if package installed
            with open(toml_path, "rb") as f:
                toml_data = toml.load(f)
            hr = toml_data.get("hr_roles", {}) or {}
            result = {"admins": {}}

            # admins
            for admin_name, admin_data in hr.get("admins", {}).items():
                if isinstance(admin_data, dict):
                    pwd = admin_data.get("password", "")
                else:
                    pwd = str(admin_data)
                result["admins"][admin_name] = {"password": pwd}

            # superadmin: support both plural and legacy single entry
            if "superadmins" in hr and isinstance(hr["superadmins"], dict):
                first_user = next(iter(hr["superadmins"]), None)
                if first_user:
                    entry = hr["superadmins"][first_user]
                    pwd = entry.get("password", "") if isinstance(entry, dict) else str(entry)
                    result["superadmin"] = {"username": first_user, "password": pwd}
                else:
                    result["superadmin"] = {"username": "", "password": ""}
            elif "superadmin" in hr and isinstance(hr["superadmin"], dict):
                sa = hr["superadmin"]
                result["superadmin"] = {"username": sa.get("username", ""), "password": sa.get("password", "")}
            else:
                result.setdefault("superadmin", {"username": "", "password": ""})

            return result
        except Exception:
            # If file parsing fails, continue to try st.secrets / json fallback
            pass

    # 3) If no/invalid TOML, try st.secrets (Streamlit-managed)
    try:
        hr_data = st.secrets.get("hr_roles")
        if hr_data:
            result = {"admins": {}}
            for admin_name, admin_data in hr_data.get("admins", {}).items():
                result["admins"][admin_name] = {
                    "password": admin_data.get("password", "") if isinstance(admin_data, dict) else str(admin_data)
                }
            if "superadmins" in hr_data and isinstance(hr_data["superadmins"], dict):
                first_user = next(iter(hr_data["superadmins"]), None)
                if first_user:
                    entry = hr_data["superadmins"][first_user]
                    pwd = entry.get("password", "") if isinstance(entry, dict) else str(entry)
                    result["superadmin"] = {"username": first_user, "password": pwd}
                else:
                    result["superadmin"] = {"username": "", "password": ""}
            elif "superadmin" in hr_data and isinstance(hr_data["superadmin"], dict):
                sa = hr_data["superadmin"]
                result["superadmin"] = {"username": sa.get("username", ""), "password": sa.get("password", "")}
            else:
                result.setdefault("superadmin", {"username": "", "password": ""})
            return result
    except Exception:
        pass

    # 4) Final fallback
    return DEFAULT_HR_ROLES


def logout() -> None:
    """
    Clear all session state and query parameters, then trigger a rerun.
    """
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Clear query params
    qp_clear()
    st.rerun()


def authenticate_user(username: str, password: str, admin_name: str = None) -> Optional[Dict[str, str]]:
    """
    Unified authentication — auto-detect role from username + password.
    Check order: superadmin → admins → divisions.

    Returns:
        Dict with role info on success: {"role", "division", "hr_admin", "display_name"}
        None on failure.
    """
    hr_roles = get_hr_roles()
    username_lower = username.strip().lower()

    # 1. Check superadmin (with hardcoded fallback for deployment)
    sa = hr_roles.get("superadmin", {})
    sa_username = sa.get("username", "").lower() if sa else ""
    sa_password = sa.get("password", "") if sa else ""
    
    # Hardcoded fallback if hr_roles not properly loaded
    if not sa_username and username_lower == "hrsuper":
        sa_username = "hrsuper"
        sa_password = "hrsuper123"
    
    if username_lower == sa_username and password == sa_password:
        return {
            "role": "HR Superadmin",
            "division": "Human Resource",
            "hr_admin": None,
            "display_name": "HR Superadmin",
        }

    # 2. Check HR admins (with fallback defaults)
    admins_dict = hr_roles.get("admins", {})
    if not admins_dict:
        # Fallback to DEFAULT_HR_ROLES if not loaded
        admins_dict = DEFAULT_HR_ROLES.get("admins", {})
    
    for admin_key, admin_data in admins_dict.items():
        if username_lower == admin_key.lower():
            admin_pass = admin_data.get("password", "") if isinstance(admin_data, dict) else str(admin_data)
            if password == admin_pass:
                display = admin_data.get("name", admin_key) if isinstance(admin_data, dict) else admin_key
                return {
                    "role": "HR Admin",
                    "division": "Human Resource",
                    "hr_admin": admin_key,
                    "display_name": display,
                }
            break  # username matched but wrong password

    # 3. Check divisions by short username
    division_name = DIVISION_USERNAMES.get(username_lower)

    # Also allow full division name as username (reverse lookup)
    if not division_name:
        for full_name in st.session_state.get("credentials", {}).keys():
            if username_lower == full_name.strip().lower():
                division_name = full_name
                break

    if division_name:
        credentials = st.session_state.get("credentials", {})
        stored = credentials.get(division_name, "")
        if _check_password(password, stored):
            return {
                "role": "Division",
                "division": division_name,
                "hr_admin": None,
                "display_name": division_name,
            }

    return None
