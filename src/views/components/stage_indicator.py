import streamlit as st
import pandas as pd

def render_stage_indicator(row: pd.Series, active_stages: list[str]) -> None:
    """
    Render a beautiful, read-only horizontal pill indicator for hiring stages.
    """
    html_str = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; margin-top: 8px;">'
    
    # Check if position is completed
    is_frozen = bool(row.get('Freeze', False))
    is_completed = bool(row.get('On Boarding', False)) and not is_frozen

    for stage in active_stages:
        is_done = bool(row.get(stage, False))
        
        if is_done:
            bg_color = "#dcfce7"
            text_color = "#166534"
            icon = "✓"
            border = "1px solid #bbf7d0"
        else:
            bg_color = "#f3f4f6"
            text_color = "#6b7280"
            icon = "○"
            border = "1px solid #e5e7eb"
            
        html_str += f"""
        <div style="
            background-color: {bg_color};
            color: {text_color};
            border: {border};
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        ">
            <span>{icon}</span> {stage}
        </div>
        """
    html_str += "</div>"
    st.markdown(html_str, unsafe_allow_html=True)
