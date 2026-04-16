"""Progress stepper component for visualizing hiring stages."""

import streamlit as st
import pandas as pd
from typing import Optional
from config.settings import BASE_STAGES


def render_progress_stepper(
    data: pd.DataFrame,
    session_key: str = "stage_filter",
    show_counts: bool = True
) -> Optional[str]:
    """Render a clickable progress stepper showing hiring stages."""
    if len(data) == 0:
        st.info("No data available for pipeline visualization.")
        return None
    
    # Initialize session state
    if f"{session_key}_selected" not in st.session_state:
        st.session_state[f"{session_key}_selected"] = None
    
    # Calculate stage statistics - count positions where this is their CURRENT stage
    stage_stats = {stage: 0 for stage in BASE_STAGES}
    # Track how many positions have REACHED or PASSED each stage
    stage_reached = {stage: 0 for stage in BASE_STAGES}
    
    for idx, row in data.iterrows():
        try:
            current_stage = None
            has_skill_test = row.get("Has Skill Test", True)
            
            # Find the highest completed stage for this position
            for stage in reversed(BASE_STAGES):
                if stage == "Skill Test" and not has_skill_test:
                    continue
                if stage in row.index and row[stage] == True:
                    current_stage = stage
                    break
            
            if current_stage is not None:
                stage_stats[current_stage] += 1
                
                # Count all stages this position has reached/passed
                current_idx = BASE_STAGES.index(current_stage)
                for j, s in enumerate(BASE_STAGES):
                    if j <= current_idx:
                        # Skip skill test if position doesn't have it
                        if s == "Skill Test" and not has_skill_test:
                            continue
                        stage_reached[s] += 1
        except Exception:
            continue
    
    total_positions = len(data)
    current_filter = st.session_state[f"{session_key}_selected"]
    
    # Show filter status and clear button
    if current_filter:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.info(f"📌 Filtered by: **{current_filter}** ({stage_stats.get(current_filter, 0)} positions)")
        with col2:
            if st.button("✕ Clear", key=f"{session_key}_clear"):
                st.session_state[f"{session_key}_selected"] = None
                st.rerun()
    
    # Short labels for display
    stage_labels = {
        "Initial Interview (HR)": ("Initial HR", "First screening"),
        "HR & User Interview (Stage 1)": ("HR & User", "Stage 1"),
        "Skill Test": ("Skill Test", "Assessment"),
        "Final Interview": ("Final", "Last interview"),
        "Offering": ("Offering", "Job offer"),
        "Contract Sign": ("Contract", "Sign docs"),
        "On Boarding": ("On Boarding", "Start date")
    }
    
    # Build stepper using Streamlit columns
    cols = st.columns(len(BASE_STAGES))
    
    for i, stage in enumerate(BASE_STAGES):
        count = stage_stats[stage]
        reached = stage_reached[stage]
        
        # Determine stage status based on positions that have REACHED this stage
        # Green = all positions passed this stage
        # Blue = some positions have reached/passed this stage
        # Gray = no positions have reached this stage yet
        if reached == total_positions and total_positions > 0:
            circle_color = "#10b981"  # Green - all passed
            text_color = "#1e293b"
        elif reached > 0:
            circle_color = "#2563eb"  # Blue - some reached
            text_color = "#1e293b"
        else:
            circle_color = "#94a3b8"  # Gray - not reached yet
            text_color = "#94a3b8"
        
        # Highlight selected
        is_selected = current_filter == stage
        border_style = "3px solid #2563eb" if is_selected else "none"
        
        title, subtitle = stage_labels.get(stage, (stage, ""))
        icon = "✓" if count == total_positions and total_positions > 0 else str(i + 1)
        
        with cols[i]:
            # Render step indicator as clickable
            badge_html = f'<span style="position:absolute;top:-5px;right:5px;background:#ef4444;color:white;font-size:0.65rem;font-weight:700;padding:2px 6px;border-radius:999px;">{count}</span>' if count > 0 else ''
            
            step_html = f'''<div style="display:flex;flex-direction:column;align-items:center;position:relative;padding:8px;border-radius:12px;border:{border_style};cursor:pointer;">
<div style="width:48px;height:48px;border-radius:50%;background:{circle_color};color:white;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:0.95rem;position:relative;">{icon}{badge_html}</div>
<div style="text-align:center;margin-top:8px;">
<div style="font-size:0.8rem;font-weight:600;color:{text_color};">{title}</div>
<div style="font-size:0.65rem;color:#64748b;">{subtitle}</div>
</div>
</div>'''
            st.markdown(step_html, unsafe_allow_html=True)
            
            # Clickable button underneath
            if st.button("Select", key=f"{session_key}_btn_{i}", use_container_width=True):
                if st.session_state[f"{session_key}_selected"] == stage:
                    st.session_state[f"{session_key}_selected"] = None
                else:
                    st.session_state[f"{session_key}_selected"] = stage
                st.rerun()
    
    return st.session_state[f"{session_key}_selected"]


def filter_by_stage(data: pd.DataFrame, stage: Optional[str]) -> pd.DataFrame:
    """Filter hiring data by specific stage."""
    if not stage or stage not in BASE_STAGES:
        return data
    
    if stage not in data.columns:
        return pd.DataFrame(columns=data.columns)
    
    filtered_indices = []
    
    for idx, row in data.iterrows():
        try:
            has_skill_test = row.get("Has Skill Test", True)
            current_stage = None
            
            for s in reversed(BASE_STAGES):
                if s == "Skill Test" and not has_skill_test:
                    continue
                if s in row.index and row[s] == True:
                    current_stage = s
                    break
            
            if current_stage == stage:
                filtered_indices.append(idx)
        except Exception:
            continue
    
    return data.loc[filtered_indices] if filtered_indices else pd.DataFrame(columns=data.columns)


