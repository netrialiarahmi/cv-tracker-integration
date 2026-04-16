"""Metrics display component for dashboard statistics."""

import pandas as pd
import streamlit as st

from models.hiring import calculate_position_progress
from config.settings import BASE_STAGES


def render_metrics(filtered_data: pd.DataFrame, interactive_key: str = None) -> None:
    """Render responsive dashboard-style metric cards, optionally interactive."""
    if len(filtered_data) == 0:
        return

    total = len(filtered_data)

    if "Freeze" in filtered_data.columns:
        freeze_mask = filtered_data["Freeze"] == True
    else:
        notes_series = filtered_data.get("Notes", pd.Series("", index=filtered_data.index))
        freeze_mask = notes_series.astype(str).str.lower().str.contains("freeze")

    freeze = int(freeze_mask.sum())
    completed = int(((filtered_data["On Boarding"] == True) & (~freeze_mask)).sum())
    in_progress = max(0, total - completed - freeze)

    progress_values = [
        calculate_position_progress(row, BASE_STAGES)
        for _, row in filtered_data.iterrows()
    ]
    avg_progress = sum(progress_values) / len(progress_values) if progress_values else 0

    metrics = [
        {"key": "total", "label": "Total Positions", "value": f"{total}", "clickable": True},
        {"key": "completed", "label": "Completed", "value": f"{completed}", "clickable": True},
        {"key": "in_progress", "label": "In Progress", "value": f"{in_progress}", "clickable": True},
        {"key": "freeze", "label": "Freeze", "value": f"{freeze}", "clickable": True},
        {"key": "avg", "label": "Avg Progress", "value": f"{avg_progress:.0f}%", "clickable": False},
    ]

    if not interactive_key:
        cards_html = "".join(
            f"<div class='metric-card'><span class='metric-card-label'>{m['label']}</span><span class='metric-card-value'>{m['value']}</span></div>"
            for m in metrics
        )
        st.markdown(f"<div class='metric-card-grid'>{cards_html}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        return

    st.session_state.setdefault(interactive_key, "total")
    active = st.session_state.get(interactive_key, "total")
    
    cols = st.columns(5)
    for col, metric in zip(cols, metrics):
        with col:
            is_active = (metric["key"] == active)
            if st.button(
                f"{metric['label']}\n\n{metric['value']}",
                key=f"{interactive_key}_{metric['key']}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                disabled=not metric["clickable"],
            ):
                if metric["clickable"]:
                    st.session_state[interactive_key] = metric["key"]
                    st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
