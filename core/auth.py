"""
Authentication logic for HR roles and division users.
Handles login validation, logout, and HR roles configuration loading.
"""

import streamlit as st
import os
import json
from typing import Dict, Any
from config.settings import HR_ROLES_FILE, DEFAULT_HR_ROLES
from core.session_manager import qp_clear


def get_hr_roles() -> Dict[str, Any]:
    """
    Load HR roles configuration from multiple sources with priority:
    1. .streamlit/secrets.toml (for manual edits)
    2. st.secrets (Streamlit-managed)
    3. hr_roles.json (runtime-managed)
    4. Default values
    
    Returns:
        Dictionary containing superadmin and admins configuration
    """
    # Try reading .streamlit/secrets.toml first so manual edits are visible immediately
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

    # If no/invalid TOML, try st.secrets (Streamlit-managed)
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

    # fallback to hr_roles.json (runtime-managed) or defaults
    if os.path.exists(HR_ROLES_FILE):
        with open(HR_ROLES_FILE) as f:
            return json.load(f)
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


def authenticate_user(username: str, password: str, role: str, admin_name: str = None) -> bool:
    """
    Authenticate user based on role and credentials.
    
    Args:
        username: Username for superadmin, ignored for other roles
        password: Password to validate
        role: Role type (HR Superadmin, HR Admin, Division)
        admin_name: Admin name for HR Admin role
        
    Returns:
        True if authentication successful, False otherwise
    """
    hr_roles = get_hr_roles()
    
    if role == "HR Superadmin":
        superadmin_user = hr_roles.get("superadmin", {}).get("username", "")
        superadmin_pass = hr_roles.get("superadmin", {}).get("password", "")
        return username == superadmin_user and password == superadmin_pass
    
    elif role == "HR Admin" and admin_name:
        admin_pass = hr_roles.get("admins", {}).get(admin_name, {}).get("password", "")
        return password == admin_pass
    
    elif role == "Division":
        # Division authentication is handled separately in login flow
        # This is just a placeholder
        return False
    
    return False
