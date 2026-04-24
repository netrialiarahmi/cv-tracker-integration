"""
Progress badge component for displaying hiring stage completion.
"""

import streamlit as st
from src.models.hiring import get_progress_badge


def render_progress_badge(progress_pct: float) -> None:
    """
    Render a colored progress badge based on completion percentage.
    
    Args:
        progress_pct: Progress percentage (0-100)
    """
    badge_class, badge_text = get_progress_badge(progress_pct)
    st.markdown(f'<span class="progress-badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)
