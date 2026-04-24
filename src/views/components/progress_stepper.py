"""Progress stepper component for visualizing hiring stages."""

import streamlit as st
import pandas as pd
from typing import Optional
from src.config.settings import BASE_STAGES

_STAGE_LABELS = {
    "Initial Interview (HR)": ("Initial HR", "First screening"),
    "HR & User Interview (Stage 1)": ("HR & User", "Stage 1"),
    "Skill Test": ("Skill Test", "Assessment"),
    "Final Interview": ("Final", "Last interview"),
    "Offering": ("Offering", "Job offer"),
    "Contract Sign": ("Contract", "Sign docs"),
    "On Boarding": ("On Board", "Start date"),
}


def render_progress_stepper(
    data: pd.DataFrame,
    session_key: str = "stage_filter",
    show_counts: bool = True,
) -> Optional[str]:
    """Render a clickable progress stepper. Each stage is a column-based button."""
    if len(data) == 0:
        st.info("No data available for pipeline visualization.")
        return None

    sel_key = f"{session_key}_selected"
    st.session_state.setdefault(sel_key, None)

    # ---------- calculate stats ----------
    stage_stats = {s: 0 for s in BASE_STAGES}
    stage_reached = {s: 0 for s in BASE_STAGES}

    for _, row in data.iterrows():
        try:
            current_stage = None
            has_skill_test = row.get("Has Skill Test", True)
            for stage in reversed(BASE_STAGES):
                if stage == "Skill Test" and not has_skill_test:
                    continue
                if stage in row.index and row[stage] is True:
                    current_stage = stage
                    break
            if current_stage is not None:
                stage_stats[current_stage] += 1
                ci = BASE_STAGES.index(current_stage)
                for j, s in enumerate(BASE_STAGES):
                    if j <= ci:
                        if s == "Skill Test" and not has_skill_test:
                            continue
                        stage_reached[s] += 1
        except Exception:
            continue

    total = len(data)
    current_filter = st.session_state[sel_key]

    # ---------- filter banner ----------
    if current_filter:
        c1, c2 = st.columns([5, 1])
        with c1:
            st.info(f"Filtered by: **{current_filter}** ({stage_stats.get(current_filter, 0)} positions)")
        with c2:
            if st.button("Clear filter", key=f"{session_key}_clear"):
                st.session_state[sel_key] = None
                st.rerun()

    # ---------- render each step as column ----------
    cols = st.columns(len(BASE_STAGES))
    for i, stage in enumerate(BASE_STAGES):
        count = stage_stats[stage]
        reached = stage_reached[stage]

        if reached == total and total > 0:
            status = "completed"
        elif reached > 0:
            status = "active"
        else:
            status = "upcoming"

        is_selected = current_filter == stage
        title, subtitle = _STAGE_LABELS.get(stage, (stage, ""))
        icon = "\u2713" if status == "completed" else str(i + 1)
        badge_html = f'<span class="step-badge">{count}</span>' if count > 0 else ""
        selected_cls = " selected" if is_selected else ""

        with cols[i]:
            # Visual circle + label
            st.markdown(
                f'<div class="step-col{selected_cls}">'
                f'  <div class="step-circle {status}">{icon}{badge_html}</div>'
                f'  <div class="step-title">{title}</div>'
                f'  <div class="step-sub">{subtitle}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            # Clickable button
            if st.button("Select", key=f"{session_key}_btn_{i}", use_container_width=True):
                if st.session_state[sel_key] == stage:
                    st.session_state[sel_key] = None
                else:
                    st.session_state[sel_key] = stage
                st.rerun()

    return st.session_state[sel_key]


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
