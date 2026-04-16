"""
Session state management for Streamlit application.
Handles session initialization, query parameter management, and state restoration.
"""

import streamlit as st
from typing import Dict, Any, Optional
from config.settings import (
    SESSION_KEYS, QP_LOGGED_IN, QP_USER_DIVISION, QP_ROLE_TYPE, 
    QP_HR_ADMIN, ROLE_ADMIN, ROLE_SUPERADMIN
)


def initialize_session_state() -> None:
    """
    Initialize all required session state variables if they don't exist.
    """
    from core.data_manager import load_credentials, load_hiring_data
    
    if "credentials" not in st.session_state:
        st.session_state.credentials = load_credentials()
    if "hiring_data" not in st.session_state:
        st.session_state.hiring_data = load_hiring_data()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_division" not in st.session_state:
        st.session_state.user_division = None
    if "role" not in st.session_state:
        st.session_state.role = "User"
    if "hr_admin" not in st.session_state:
        st.session_state.hr_admin = None
    if "editing_user" not in st.session_state:
        st.session_state.editing_user = None
    if "deleting_user" not in st.session_state:
        st.session_state.deleting_user = None
    if "candidates_cache" not in st.session_state:
        st.session_state.candidates_cache = None
    if "screening_cache" not in st.session_state:
        st.session_state.screening_cache = {}
    if "cv_positions_cache" not in st.session_state:
        st.session_state.cv_positions_cache = None


def qp_get(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get query parameter value with compatibility for Streamlit < 1.30.
    
    Args:
        key: Query parameter key
        default: Default value if key not found
        
    Returns:
        Query parameter value or default
    """
    try:
        if hasattr(st, "query_params"):
            return st.query_params.get(key, default)
        vals = st.experimental_get_query_params().get(key)
        return vals[0] if vals else default
    except Exception:
        return default


def qp_update(params: Dict[str, Any]) -> None:
    """
    Update query parameters with compatibility for Streamlit < 1.30.
    
    Args:
        params: Dictionary of parameters to update
    """
    try:
        if hasattr(st, "query_params"):
            st.query_params.update({k: str(v) for k, v in params.items()})
        else:
            existing = st.experimental_get_query_params()
            for k, v in params.items():
                existing[k] = [str(v)]
            st.experimental_set_query_params(**existing)
    except Exception:
        pass


def qp_clear() -> None:
    """
    Clear all query parameters with compatibility for Streamlit < 1.30.
    """
    try:
        if hasattr(st, "query_params"):
            st.query_params.clear()
        else:
            # Setting no params clears existing in experimental API
            st.experimental_set_query_params()
    except Exception:
        pass


def restore_session_from_query_params() -> None:
    """
    Restore session state from query parameters if present.
    Supports session persistence across page reloads.
    """
    if qp_get(QP_LOGGED_IN) == "1":
        # Apply only if not already logged in
        if not st.session_state.get("logged_in", False):
            role_type = qp_get(QP_ROLE_TYPE)
            if role_type == "Division":
                st.session_state.logged_in = True
                st.session_state.user_division = qp_get(QP_USER_DIVISION)
                st.session_state.role = "Division"
                st.session_state.hr_admin = None
            elif role_type == ROLE_ADMIN:
                st.session_state.logged_in = True
                st.session_state.user_division = "Human Resource"
                st.session_state.role = ROLE_ADMIN
                st.session_state.hr_admin = qp_get(QP_HR_ADMIN)
            elif role_type == ROLE_SUPERADMIN:
                st.session_state.logged_in = True
                st.session_state.user_division = "Human Resource"
                st.session_state.role = ROLE_SUPERADMIN
                st.session_state.hr_admin = None
