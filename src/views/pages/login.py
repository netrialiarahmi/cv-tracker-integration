"""
Login page — unified username + password authentication.
Auto-detects role (Superadmin / Admin / Division) from credentials.
"""

import streamlit as st
from src.utils.helpers import get_logo_base64
from src.controllers.auth import authenticate_user
from src.controllers.session_manager import qp_clear, qp_update


LOGIN_SESSION_KEYS = ["logged_in", "user_division", "role", "hr_admin", "hr_admin_name"]


def _set_login_state(auth_result: dict) -> None:
    """Set session state and query params after successful login."""
    # Selective clear — only reset login keys, keep credentials & hiring_data
    for key in LOGIN_SESSION_KEYS:
        st.session_state.pop(key, None)
    qp_clear()

    st.session_state.logged_in = True
    st.session_state.user_division = auth_result["division"]
    st.session_state.role = auth_result["role"]
    st.session_state.hr_admin = auth_result["hr_admin"]
    st.session_state.hr_admin_name = auth_result["display_name"]

    qp_update({
        "logged_in": "1",
        "user_division": auth_result["division"],
        "role": auth_result["role"],
        "role_type": auth_result["role"],
        "hr_admin": auth_result["hr_admin"] or "",
    })


def render() -> None:
    """Render the unified login page."""
    logo_base64 = get_logo_base64()

    # --- Card header (logo + title) ---
    st.markdown(f"""
    <div class="login-container">
        <div class="login-logo">
            <img src="data:image/webp;base64,{logo_base64}" alt="Kompas.com" />
            <h2 class="login-title">Kompas.com<br>Hiring Desk</h2>
        </div>
        <p class="login-subtitle">
            Recruitment management &amp; screening platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- Login form (Streamlit widgets — centered via CSS max-width) ---
    col_l, col_form, col_r = st.columns([1.5, 2, 1.5])
    with col_form:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Please enter username and password.")
                else:
                    result = authenticate_user(username, password)
                    if result:
                        _set_login_state(result)
                        st.success(f"Welcome, {result['display_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Footer ---
    st.markdown("""
    <p style="text-align:center; margin-top:2rem; color:#94a3b8; font-size:0.78rem;">
        &copy; 2025 Kompas.com &mdash; Human Resource Division
    </p>
    """, unsafe_allow_html=True)
