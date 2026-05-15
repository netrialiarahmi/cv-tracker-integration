"""
User management models and operations.
Handles division user CRUD operations.
"""

import streamlit as st
from typing import Optional
from src.repositories.data_manager import save_credentials, save_hiring_data
from src.config.settings import PROTECTED_DIVISION
from src.controllers.auth import hash_password


class User:
    """Represents a division user with role-based properties."""
    
    def __init__(self, division: str, password: str):
        """
        Initialize a User instance.
        
        Args:
            division: Division name
            password: User password
        """
        self.division = division
        self.password = password
    
    @property
    def is_hr(self) -> bool:
        """Check if user belongs to Human Resource division."""
        return self.division == "Human Resource"
    
    def to_dict(self) -> dict:
        """Convert user to dictionary format."""
        return {
            "division": self.division,
            "password": self.password
        }


def add_new_user(division: str, password: str) -> None:
    """
    Add a new division user to the system.
    
    Args:
        division: Division name
        password: User password
    """
    st.session_state.credentials[division] = hash_password(password)
    save_credentials(st.session_state.credentials)


def update_user(old_division: str, new_division: str, new_password: str) -> None:
    """
    Update an existing user's division name and/or password.
    Also updates all hiring data associated with the old division.
    
    Args:
        old_division: Current division name
        new_division: New division name
        new_password: New password
    """
    if old_division != new_division:
        del st.session_state.credentials[old_division]
        st.session_state.hiring_data.loc[
            st.session_state.hiring_data['Division'] == old_division, 'Division'
        ] = new_division
        save_hiring_data(st.session_state.hiring_data)
    st.session_state.credentials[new_division] = hash_password(new_password)
    save_credentials(st.session_state.credentials)


def delete_user(division: str) -> bool:
    """
    Delete a division user and all associated hiring data.
    Cannot delete protected divisions.
    
    Args:
        division: Division name to delete
        
    Returns:
        True if deletion successful, False otherwise
    """
    # Don't allow deletion of protected division or "Human Resource"
    if division in st.session_state.credentials and division != "Human Resource" and division != PROTECTED_DIVISION:
        del st.session_state.credentials[division]
        save_credentials(st.session_state.credentials)
        st.session_state.hiring_data = st.session_state.hiring_data[
            st.session_state.hiring_data['Division'] != division
        ]
        save_hiring_data(st.session_state.hiring_data)
        return True
    return False
