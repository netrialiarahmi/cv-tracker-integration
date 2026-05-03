"""
Kompas.com Hiring Tracker Application
Main entry point - clean and modular architecture.
"""

import streamlit as st
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

from src.controllers.session_manager import initialize_session_state, restore_session_from_query_params, qp_get
from src.controllers.auth import logout
from src.views.pages import login, superadmin_dashboard, admin_dashboard, division_dashboard
from src.views.styles.custom_css import inject_custom_css
from src.config.settings import PAGE_CONFIG, LOGO_PATH
from datetime import datetime

# --------------------------
# Page Configuration
# --------------------------
# Load logo for page iconx
logo_file = LOGO_PATH
try:
    logo = Image.open(logo_file)
    st.set_page_config(
        page_title=PAGE_CONFIG["page_title"],
        page_icon=logo,
        layout=PAGE_CONFIG["layout"]
    )
except FileNotFoundError:
    # Fallback without logo
    st.set_page_config(
        page_title=PAGE_CONFIG["page_title"],
        layout=PAGE_CONFIG["layout"]
    )

# --------------------------
# Inject Custom Styles
# --------------------------
inject_custom_css()

# --------------------------
# Initialize Session State
# --------------------------
initialize_session_state()
restore_session_from_query_params()

# --------------------------
# Check for Logout Signal
# --------------------------
if qp_get("logout") == "1":
    logout()
    st.rerun()

# --------------------------
# Route Based on Login State
# --------------------------
if not st.session_state.get('logged_in', False):
    # Show login page
    login.render()
else:
    # Show appropriate dashboard based on role
    role = st.session_state.get('role')
    
    if role == 'HR Superadmin':
        superadmin_dashboard.render()
    elif role == 'HR Admin':
        admin_dashboard.render()
    else:
        # Division user
        division_dashboard.render()

# --------------------------
# Footer
# --------------------------
if st.session_state.get('logged_in', False):
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; color: #94a3b8; font-size: 0.75rem;">
        © 2025 Kompas.com — Human Resource Division<br>
        Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)
