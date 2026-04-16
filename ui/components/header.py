"""Standardized masthead header component."""

from __future__ import annotations

from typing import Callable

import streamlit as st

from utils.helpers import get_logo_base64
from core.auth import logout


def render_header(
    page_title: str = "Hiring Tracker Dashboard",
    subtitle: str | None = None,
    kicker: str | None = "Kompas.com Hiring Desk",
    back_button_label: str | None = None,
    back_button_key: str = "header_back",
    back_button_disabled: bool = False,
    on_back: Callable[[], None] | None = None,
) -> None:
    """Render the global masthead with logo, metadata, logout, and optional back control."""

    logo_base64 = get_logo_base64()
    role_display = st.session_state.get("role", "Division")
    user_division = st.session_state.get("user_division", "—")
    hr_admin = st.session_state.get("hr_admin")

    hr_admin_info = (
        f" • HR Admin: <strong>{hr_admin}</strong>"
        if role_display == "HR Admin" and hr_admin
        else ""
    )
    kicker_html = f'<span class="masthead-kicker">{kicker}</span>' if kicker else ""
    subtitle_html = f'<p class="masthead-subtitle">{subtitle}</p>' if subtitle else ""

    cols = st.columns([6, 1])
    
    with cols[0]:
        st.markdown(
            f"""
            <div class="masthead-card">
                <div class="masthead-brand">
                    <img src="data:image/webp;base64,{logo_base64}" alt="Kompas.com Logo" class="masthead-logo" />
                    <div class="masthead-copy">
                        {kicker_html}
                        <h1>{page_title}</h1>
                        {subtitle_html}
                        <div class="masthead-meta">
                            <span>Logged in as <strong>{user_division}</strong></span>
                            <span>Role: <span class="masthead-role">{role_display}</span>{hr_admin_info}</span>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with cols[1]:
        st.markdown('<div class="masthead-logout-wrapper">', unsafe_allow_html=True)
        if st.button("⎋ Logout", key="header_logout", use_container_width=True, type="primary"):
            logout()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
