"""HR Admin dashboard page - PIC-filtered hiring management with briefing UX."""

import streamlit as st
import pandas as pd
from streamlit.components.v1 import html

from ui.components.header import render_header
from ui.components.data_table import render_reference_table
from services.hiring_service import render_position_form
from config.settings import BASE_STAGES
from models.hiring import calculate_position_progress, get_progress_badge


AD_SECTION_IDS = {
    "top": "ad-top",
    "search": "ad-search",
    "metrics": "ad-metrics",
    "manage": "ad-manage",
    "summary": "ad-summary"
}
AD_SCROLL_KEY = "ad_pipeline_scroll"


def _init_admin_state() -> None:
    st.session_state.setdefault("ad_search", "")
    st.session_state.setdefault("ad_nav_target", None)
    st.session_state.setdefault("ad_current_section", AD_SECTION_IDS["top"])
    st.session_state.setdefault("ad_metric_filter", "total")


def _anchor(section_id: str) -> None:
    st.markdown(f'<div id="{section_id}"></div>', unsafe_allow_html=True)
    st.session_state.ad_current_section = section_id


def _inline_anchor(section_id: str) -> None:
    st.markdown(f'<div id="{section_id}"></div>', unsafe_allow_html=True)


def _filter_by_status(df: pd.DataFrame, status_key: str) -> pd.DataFrame:
    """Filter dataframe by status key from metric card."""
    if status_key == "total" or len(df) == 0:
        return df

    if "Freeze" in df.columns:
        freeze_mask = df["Freeze"] == True
    else:
        notes_series = df.get("Notes", pd.Series("", index=df.index))
        freeze_mask = notes_series.astype(str).str.lower().str.contains("freeze")

    if status_key == "freeze":
        return df[freeze_mask]
    elif status_key == "completed":
        completed_mask = (df["On Boarding"] == True) & (~freeze_mask)
        return df[completed_mask]
    elif status_key == "in_progress":
        completed_mask = (df["On Boarding"] == True) & (~freeze_mask)
        return df[~(completed_mask | freeze_mask)]

    return df


def _render_scroll_manager() -> None:
    target = st.session_state.get("ad_nav_target", "") or ""
    script = f"""
    <script>
    const key = '{AD_SCROLL_KEY}';
    const target = '{target}';
    const saved = window.sessionStorage.getItem(key);
    const restore = () => {{
        if (target) {{
            const el = document.getElementById(target);
            if (el) {{
                el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                window.sessionStorage.setItem(key, window.scrollY.toString());
                return;
            }}
        }}
        if (saved) {{
            window.scrollTo(0, parseFloat(saved));
        }}
    }};
    window.addEventListener('load', () => setTimeout(restore, 50));
    window.addEventListener('scroll', () => {{
        window.sessionStorage.setItem(key, window.scrollY.toString());
    }});
    </script>
    """
    html(script, height=0)
    if target:
        st.session_state.ad_nav_target = None


def render() -> None:
    """
    Render the HR Admin dashboard with PIC-filtered positions.
    """
    _init_admin_state()
    assigned_pic = st.session_state.get("hr_admin")
    subtitle = f"Assignments for {assigned_pic}" if assigned_pic else "PIC-focused hiring queue"
    render_header(
        page_title="HR Admin Dashboard",
        subtitle=subtitle,
        kicker="Kompas.com Hiring Desk",
    )
    _render_scroll_manager()

    st.info(f"### 📋 Hiring Pipeline — Assigned to **{st.session_state.hr_admin}**")

    df = st.session_state.hiring_data.copy()

    pic_name = (st.session_state.hr_admin or "").strip().lower()
    if "PIC" in df.columns and pic_name:
        assigned = df[df["PIC"].astype(str).str.strip().str.lower() == pic_name].copy()
    else:
        assigned = pd.DataFrame()
    
    # Tab selection
    tab_pipeline, tab_screening = st.tabs(["📊 Hiring Pipeline", "🔍 Screening Results"])

    with tab_pipeline:
        _render_pipeline_tab(assigned)

    with tab_screening:
        _render_screening_tab(assigned)


def _render_pipeline_tab(assigned: pd.DataFrame) -> None:
    """Render the hiring pipeline management tab."""
    if assigned.empty:
        st.warning("⚠️ No positions assigned to you yet.")
    else:
        # Display metrics as horizontal cards
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                color: white;
            ">
                <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">
                    {len(assigned)}
                </div>
                <div style="font-size: 1rem; opacity: 0.9;">
                    📊 Assigned Positions
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            unique_divisions = assigned['Division'].nunique()
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                color: white;
            ">
                <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">
                    {unique_divisions}
                </div>
                <div style="font-size: 1rem; opacity: 0.9;">
                    🏢 Divisions
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        display_hiring_management(assigned)


def display_hiring_management(filtered_data: pd.DataFrame) -> None:
    """
    Display hiring management interface for HR Admin.
    
    Args:
        filtered_data: Filtered DataFrame containing assigned positions
    """
    # Base stages
    base_stages = BASE_STAGES
    
    # Apply filters based on current state before rendering controls
    search_term = st.session_state.get("ad_search", "")
    if search_term:
        filtered_data = filtered_data[
            (filtered_data["Job Position"].str.contains(search_term, case=False, na=False)) |
            (filtered_data["Division"].str.contains(search_term, case=False, na=False))
        ]

    # Metrics (interactive like superadmin)
    if len(filtered_data) > 0:
        from ui.components.metrics import render_metrics
        from ui.components.progress_stepper import render_progress_stepper, filter_by_stage

        _anchor(AD_SECTION_IDS["metrics"])
        st.markdown('<div class="content-card"><h3>Pipeline Metrics</h3>', unsafe_allow_html=True)
        render_metrics(filtered_data, interactive_key="ad_metric_filter")
        st.markdown('</div>', unsafe_allow_html=True)

        # Apply pipeline status filter
        active_filter = st.session_state.get("ad_metric_filter", "total")
        filtered_data = _filter_by_status(filtered_data, active_filter)

        # Stage stepper with clickable filtering
        st.markdown('<div class="content-card"><h3>Hiring Pipeline Stages</h3>', unsafe_allow_html=True)
        selected_stage = render_progress_stepper(filtered_data, session_key="ad_stage_filter", show_counts=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Apply stage filter
        if selected_stage:
            filtered_data = filter_by_stage(filtered_data, selected_stage)
    else:
        st.info("No results match the current filters.")

    # Search controls (after metrics for cleaner flow)
    _anchor(AD_SECTION_IDS["search"])
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    search_term = st.text_input(
        "Search",
        key="ad_search",
        placeholder="Search by job title or division...",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Manage positions section
    if len(filtered_data) > 0:
        _anchor(AD_SECTION_IDS["manage"])
        st.markdown('<div class="content-card"><h3>Manage Positions</h3>', unsafe_allow_html=True)
        for idx, row in filtered_data.iterrows():
            # Dynamic stages depending on whether position uses skill test
            if "Has Skill Test" in row and not row["Has Skill Test"]:
                stages = [s for s in base_stages if s != "Skill Test"]
            else:
                stages = base_stages
            
            progress_pct = calculate_position_progress(row, base_stages)
            badge_class, badge_text = get_progress_badge(progress_pct)
            pic_display = f"👤 {row.get('PIC', 'Unassigned')}" if row.get('PIC') else "👤 Unassigned"
            hire_type = row.get('Hire Type', 'Additional')
            if hire_type == 'Replacement' and row.get('Replacement For'):
                hire_type_info = f"Replacement for {row['Replacement For']}"
            else:
                hire_type_info = "Additional"

            anchor_id = f"ad-position-{idx}"
            _inline_anchor(anchor_id)
            with st.expander(f"{row['Job Position']} • {pic_display} • {hire_type_info}"):
                can_edit = st.session_state.get("role") in ["HR Superadmin", "HR Admin"]
                render_position_form(idx, row, can_edit, stages)
        
        st.markdown('</div>', unsafe_allow_html=True)

    if len(filtered_data) > 0:
        _anchor(AD_SECTION_IDS["summary"])
        st.markdown("<br>", unsafe_allow_html=True)
        render_reference_table(
            filtered_data,
            caption=""
        )


def _render_screening_tab(assigned: pd.DataFrame) -> None:
    """Render screening results tab for HR Admin."""
    from services.candidate_service import (
        fetch_screening_results, escalate_candidate, load_candidates
    )
    from ui.components.screening_table import render_screening_table

    if assigned.empty:
        st.info("No assigned positions to show screening results for.")
        return

    # Filter to positions that have CV Matching links
    if "CV Matching Position" not in assigned.columns:
        assigned["CV Matching Position"] = ""

    linked = assigned[assigned["CV Matching Position"].astype(str).str.strip() != ""]

    if linked.empty:
        st.info("No assigned positions are linked to CV Matching. Ask HR Superadmin to link positions in the Screening Results tab.")
        return

    if st.button("🔄 Refresh Screening Data", key="ad_refresh_screening"):
        st.session_state.screening_cache = {}

    all_candidates = load_candidates()
    escalated_emails = {c.get("email", "").lower() for c in all_candidates if c.get("email")}

    for idx, row in linked.iterrows():
        cv_position = row["CV Matching Position"]
        position_key = row["Job Position"]
        division = row["Division"]

        st.markdown(f"### 📋 {position_key} → {cv_position}")

        cache_key = cv_position
        if cache_key not in st.session_state.screening_cache:
            results = fetch_screening_results(cv_position)
            st.session_state.screening_cache[cache_key] = results

        results_df = st.session_state.screening_cache.get(cache_key)

        def handle_escalate(row_dict, pk=position_key, div=division):
            user = st.session_state.get("hr_admin", "HR Admin")
            candidate = escalate_candidate(row_dict, pk, div, user)
            st.success(f"✅ {candidate.name} escalated to user interview!")
            st.rerun()

        render_screening_table(
            results_df, position_key, division,
            escalated_emails, on_escalate=handle_escalate,
            key_prefix=f"ad_screen_{idx}"
        )
