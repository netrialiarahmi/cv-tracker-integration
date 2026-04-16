"""Division dashboard page - read-only view with executive briefing UX."""

import streamlit as st
import pandas as pd
from streamlit.components.v1 import html

from ui.components.header import render_header
from ui.components.metrics import render_metrics
from ui.components.data_table import render_reference_table
from models.hiring import calculate_position_progress, get_progress_badge
from config.settings import BASE_STAGES


DIV_SECTION_IDS = {
    "top": "div-top",
    "search": "div-search",
    "metrics": "div-metrics",
    "summary": "div-summary",
    "details": "div-details"
}
DIV_SCROLL_KEY = "div_scroll"


def _init_div_state() -> None:
    st.session_state.setdefault("div_show_freeze_only", False)
    st.session_state.setdefault("div_nav_stack", [])
    st.session_state.setdefault("div_nav_target", None)
    st.session_state.setdefault("div_current_section", DIV_SECTION_IDS["top"])
    st.session_state.setdefault("div_active_position", None)
    st.session_state.setdefault("div_metric_filter", "total")


def _anchor(section_id: str) -> None:
    st.session_state.div_current_section = section_id
    st.markdown(f'<div id="{section_id}"></div>', unsafe_allow_html=True)


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
    target = st.session_state.get("div_nav_target", "") or ""
    script = f"""
    <script>
    const key = '{DIV_SCROLL_KEY}';
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
        st.session_state.div_nav_target = None


def render() -> None:
    """
    Render the division dashboard with read-only hiring progress view.
    """
    user_div = st.session_state.get("user_division")
    if not user_div or user_div == "None":
        st.warning("⚠️ Session expired or division not set. Please log in again.")
        if st.button("🔐 Back to Login"):
            from core.auth import logout
            logout()
            st.rerun()
        st.stop()
    
    render_header(
        page_title=f"{user_div} Hiring Briefing",
        subtitle="Executive summary for division leaders",
        kicker="Kompas.com Hiring Desk"
    )
    _init_div_state()
    _render_scroll_manager()
    
    # Filter data for user's division
    filtered_data = st.session_state.hiring_data[
        st.session_state.hiring_data["Division"].astype(str) == str(user_div)
    ].copy()

    # Tab selection
    tab_pipeline, tab_candidates = st.tabs(["📊 Hiring Pipeline", "👥 Candidates"])

    with tab_pipeline:
        _render_pipeline_tab(filtered_data)

    with tab_candidates:
        _render_candidates_tab(user_div, filtered_data)


def _render_pipeline_tab(filtered_data: pd.DataFrame) -> None:
    """Render the hiring pipeline overview tab."""
    
    # Display hiring pipeline (metrics only) at the top
    filtered_data = display_hiring_pipeline_metrics(filtered_data)

    # Summary table
    _anchor(DIV_SECTION_IDS["summary"])
    st.markdown("<br>", unsafe_allow_html=True)
    render_reference_table(
        filtered_data,
        caption=""
    )
    
    # Position details with search
    display_position_details(filtered_data)



def display_hiring_pipeline_metrics(filtered_data: pd.DataFrame) -> pd.DataFrame:
    """
    Display hiring pipeline metrics for division users (read-only).
    Returns the filtered dataframe after applying metric-based filters.
    """
    _anchor(DIV_SECTION_IDS["metrics"])
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-heading"><h3>📊 Hiring Pipeline</h3></div>',
        unsafe_allow_html=True
    )

    if len(filtered_data) == 0:
        st.warning("No positions found for your division")
        st.markdown('</div>', unsafe_allow_html=True)
        return filtered_data

    render_metrics(filtered_data, interactive_key="div_metric_filter")
    st.markdown('</div>', unsafe_allow_html=True)

    active_filter = st.session_state.get("div_metric_filter", "total")
    return _filter_by_status(filtered_data, active_filter)


def display_position_details(filtered_data: pd.DataFrame) -> None:
    """
    Display position details for division users (read-only).
    
    Args:
        filtered_data: Filtered DataFrame for the division
    """
    stages = BASE_STAGES
    
    if len(filtered_data) == 0:
        return
    
    # Position details header
    _anchor(DIV_SECTION_IDS["details"])
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📋 Position Details")
    
    # Search widget
    _anchor(DIV_SECTION_IDS["search"])
    search_term = st.text_input("🔍 Search positions", placeholder="Search by job title or notes...", key="div_search")
    
    # Apply search filter
    if search_term:
        filtered_data = filtered_data[
            filtered_data["Job Position"].str.contains(search_term, case=False, na=False) |
            filtered_data.get("Notes", pd.Series("", index=filtered_data.index)).astype(str).str.contains(search_term, case=False, na=False)
        ]
    
    # Display position cards
    for idx, row in filtered_data.iterrows():
        # Determine active stages based on Has Skill Test
        if row.get('Has Skill Test', True):
            active_stages = stages
        else:
            active_stages = [s for s in stages if s != "Skill Test"]
        
        progress_pct = calculate_position_progress(row, stages)
        badge_class, badge_text = get_progress_badge(progress_pct)
        pic_info = f"👤 PIC: {row.get('PIC', 'Unassigned')}" if "PIC" in row else ""
        
        # Show hire type info (Replacement For / Additional)
        hire_type = row.get('Hire Type', 'Additional')
        if hire_type == 'Replacement' and row.get('Replacement For'):
            hire_type_info = f"Replacement for {row['Replacement For']}"
        else:
            hire_type_info = "Additional"
    
        anchor_id = f"div-position-{idx}"
        _inline_anchor(anchor_id)
        key_sig = f"{row['Division']}::{row['Job Position']}::{idx}"
        is_active = st.session_state.get("div_active_position") == key_sig
        with st.expander(f"**{row['Job Position']}** • {pic_info} • {hire_type_info}", expanded=is_active):
            st.markdown(f'<span class="progress-badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Read-only hiring stage display
            st.markdown("#### 📝 Hiring Stages")
            
            # Display stages as read-only status indicators
            cols = st.columns(4)
            for i, stage in enumerate(active_stages):
                with cols[i % 4]:
                    status = "✅" if row[stage] else "⏳"
                    st.markdown(f"{status} **{stage}**")
            st.markdown("<br>", unsafe_allow_html=True)
    
            # Notes and date
            if row.get("Notes"):
                st.markdown("#### 💬 Notes")
                st.info(row["Notes"])
            if "Last Updated" in row:
                st.caption(f"🕒 Last Updated: {row['Last Updated']}")


def _render_candidates_tab(user_div: str, filtered_data: pd.DataFrame) -> None:
    """
    Render the Candidates tab for division users.
    Shows escalated candidates with commenting and approve/reject actions.
    """
    from services.candidate_service import (
        get_candidates_for_division, add_comment_to_candidate
    )
    from services.feedback_service import add_feedback_for_position
    from ui.components.candidate_card import render_candidate_card
    from models.candidate import Candidate

    st.markdown("### 👥 Candidates for User Interview")
    st.info("Review candidates escalated from HR screening. Add comments, approve, or reject candidates. Your feedback will improve future screening accuracy.")

    candidates = get_candidates_for_division(user_div)

    if not candidates:
        st.warning("No candidates have been escalated to your division yet.")
        return

    # Group by position
    positions = {}
    for c in candidates:
        pos = c.position_key
        if pos not in positions:
            positions[pos] = []
        positions[pos].append(c)

    # Status filter
    status_filter = st.selectbox(
        "Filter by status",
        ["All"] + Candidate.ALL_STATUSES,
        key="div_candidate_status_filter"
    )

    for position_key, pos_candidates in positions.items():
        # Get job description for feedback
        job_desc = ""
        for _, row in filtered_data.iterrows():
            if row["Job Position"] == position_key:
                job_desc = row.get("Job Description", "")
                break

        # Filter by status
        if status_filter != "All":
            pos_candidates = [c for c in pos_candidates if c.status == status_filter]

        if not pos_candidates:
            continue

        st.markdown(f"---")
        st.markdown(f"#### 📋 {position_key}")
        st.caption(f"{len(pos_candidates)} candidate(s)")

        for i, candidate in enumerate(pos_candidates):
            def make_comment_handler(cid, pos=position_key, jd=job_desc):
                def handler(candidate_id, text):
                    add_comment_to_candidate(
                        candidate_id, user_div, user_div, text, "comment"
                    )
                    # Also sync feedback to cv-matching
                    add_feedback_for_position(
                        pos, user_div, jd, user_div,
                        candidate.name, "comment", text
                    )
                    st.success("💬 Comment added!")
                    st.rerun()
                return handler

            def make_approve_handler(cid, pos=position_key, jd=job_desc):
                def handler(candidate_id, text):
                    add_comment_to_candidate(
                        candidate_id, user_div, user_div, text, "approve"
                    )
                    add_feedback_for_position(
                        pos, user_div, jd, user_div,
                        candidate.name, "approve", text
                    )
                    st.success("✅ Candidate approved!")
                    st.rerun()
                return handler

            def make_reject_handler(cid, pos=position_key, jd=job_desc):
                def handler(candidate_id, text):
                    add_comment_to_candidate(
                        candidate_id, user_div, user_div, text, "reject"
                    )
                    add_feedback_for_position(
                        pos, user_div, jd, user_div,
                        candidate.name, "reject", text
                    )
                    st.success("❌ Candidate rejected. Feedback sent to screening.")
                    st.rerun()
                return handler

            render_candidate_card(
                candidate,
                key_prefix=f"div_cand_{position_key}_{i}",
                show_actions=True,
                on_comment=make_comment_handler(candidate.id),
                on_approve=make_approve_handler(candidate.id),
                on_reject=make_reject_handler(candidate.id),
            )
