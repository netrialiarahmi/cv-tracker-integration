"""Division dashboard page - read-only view with executive briefing UX."""

import streamlit as st
import pandas as pd
from streamlit.components.v1 import html
from streamlit_option_menu import option_menu

from src.views.components.header import render_header
from src.views.components.metrics import render_metrics
from src.views.components.data_table import render_reference_table
from src.models.hiring import calculate_position_progress, get_progress_badge
from src.config.settings import BASE_STAGES
from src.utils.helpers import (
    filter_by_year_range, available_years as _available_years,
    get_current_stage, get_stage_zone, split_by_pipeline_zone,
)


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
    st.session_state.setdefault("div_year_from", "All")
    st.session_state.setdefault("div_year_to", "All")


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
        st.warning("Session expired or division not set. Please log in again.")
        if st.button("Back to Login"):
            from src.controllers.auth import logout
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
    
    # Filter data for user's division — only active (non-frozen) positions
    filtered_data = st.session_state.hiring_data[
        st.session_state.hiring_data["Division"].astype(str) == str(user_div)
    ].copy()
    if "Freeze" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["Freeze"] != True].copy()

    # Navigation Bar
    selected_menu = option_menu(
        menu_title=None,
        options=["Hiring Pipeline", "Candidates"],
        icons=["bar-chart-line-fill", "people-fill"],
        orientation="horizontal",
        default_index=st.session_state.get("div_selected_menu", 0),
        manual_select=st.session_state.get("div_selected_menu", 0),
        key="div_option_menu",
        styles={
            "container": {
                "padding": "4px 0",
                "background-color": "#2563eb",
                "border-radius": "10px",
                "width": "100%",
                "margin-bottom": "1.5rem",
            },
            "icon": {"color": "#f9fafb", "font-size": "16px"},
            "nav-link": {
                "color": "#f9fafb",
                "font-size": "14px",
                "text-align": "center",
                "margin": "0 8px",
                "--hover-color": "rgba(255, 255, 255, 0.1)",
                "padding": "8px 12px",
                "border-radius": "8px",
            },
            "nav-link-selected": {
                "background-color": "rgba(255, 255, 255, 0.2)",
                "color": "#ffffff",
                "font-weight": "600",
                "border-radius": "8px",
                "padding": "8px 14px",
            },
        },
    )

    selected = 0 if selected_menu == "Hiring Pipeline" else 1
    if st.session_state.get("div_selected_menu") != selected:
        st.session_state.div_selected_menu = selected
        st.rerun()

    if selected == 0:
        _render_pipeline_tab(filtered_data)
    else:
        _render_candidates_tab(user_div, filtered_data)


def _render_pipeline_tab(filtered_data: pd.DataFrame) -> None:
    """Render the hiring pipeline overview tab."""
    
    # Display hiring pipeline (metrics only) at the top
    filtered_data = display_hiring_pipeline_metrics(filtered_data)

    # Hiring Pipeline Stages with year-range filter (drives stage counts)
    if len(filtered_data) > 0:
        from src.views.components.progress_stepper import render_progress_stepper, filter_by_stage

        years = _available_years(filtered_data)
        year_options = ["All"] + list(range(min(years), max(years) + 1)) if years else ["All"]
        st.markdown('<div class="content-card"><h3>Hiring Pipeline Stages</h3>', unsafe_allow_html=True)
        yc1, yc2, yc3 = st.columns([6, 1, 1])
        with yc2:
            st.selectbox("From Year", year_options, key="div_year_from", label_visibility="collapsed")
        with yc3:
            st.selectbox("To Year", year_options, key="div_year_to", label_visibility="collapsed")
        filtered_data = filter_by_year_range(
            filtered_data,
            st.session_state.get("div_year_from", "All"),
            st.session_state.get("div_year_to", "All"),
        )
        selected_stage = render_progress_stepper(filtered_data, session_key="div_stage_filter", show_counts=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if selected_stage:
            filtered_data = filter_by_stage(filtered_data, selected_stage)

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
        '<div class="section-heading"><h3>Hiring Pipeline</h3></div>',
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
    st.markdown("### Position Details")
    
    # Search widget
    _anchor(DIV_SECTION_IDS["search"])
    search_term = st.text_input("Search positions", placeholder="Search by job title or notes...", key="div_search")
    
    # Apply search filter
    if search_term:
        filtered_data = filtered_data[
            filtered_data["Job Position"].str.contains(search_term, case=False, na=False) |
            filtered_data.get("Notes", pd.Series("", index=filtered_data.index)).astype(str).str.contains(search_term, case=False, na=False)
        ]
    
    # Split pool and sort active by zone priority
    _zones = filtered_data.apply(get_stage_zone, axis=1)
    pool_data = filtered_data[_zones == 3].copy()
    filtered_data = filtered_data[_zones != 3].copy()
    if len(filtered_data) > 0:
        filtered_data["_zone"] = filtered_data.apply(get_stage_zone, axis=1)
        filtered_data = filtered_data.sort_values("_zone", kind="stable").drop(columns=["_zone"])

    # Display active position cards
    for idx, row in filtered_data.iterrows():
        # Determine active stages based on Has Skill Test
        if row.get('Has Skill Test', True):
            active_stages = stages
        else:
            active_stages = [s for s in stages if s != "Skill Test"]
        
        progress_pct = calculate_position_progress(row, stages)
        badge_class, badge_text = get_progress_badge(progress_pct)
        pic_info = f"PIC: {row.get('PIC', 'Unassigned')}" if "PIC" in row else ""
        
        # Show hire type info (Replacement For / Additional)
        hire_type = row.get('Hire Type', 'Additional')
        if hire_type == 'Replacement' and row.get('Replacement For'):
            hire_type_info = f"Replacement for {row['Replacement For']}"
        else:
            hire_type_info = "Additional"
        status_label_pos = row.get('Status', 'Contract') or 'Contract'

        anchor_id = f"div-position-{idx}"
        _inline_anchor(anchor_id)
        key_sig = f"{row['Division']}::{row['Job Position']}::{idx}"
        is_active = st.session_state.get("div_active_position") == key_sig
        with st.expander(f"**{row['Job Position']}** • {pic_info} • {hire_type_info} • {status_label_pos}", expanded=is_active):
            st.markdown(f'<span class="progress-badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Beautiful read-only hiring stage display
            st.markdown("#### Hiring Stages")
            from src.views.components.stage_indicator import render_stage_indicator
            render_stage_indicator(row, active_stages)
    
            # Notes and date
            if row.get("Notes"):
                st.markdown("#### Notes")
                st.info(row["Notes"])
            if "Last Updated" in row:
                st.caption(f"Last Updated: {row['Last Updated']}")

    # --- Pool section: completed positions ---
    if len(pool_data) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="section-heading"><h3>Completed Positions ({len(pool_data)})</h3></div>', unsafe_allow_html=True)
        st.caption("Positions that have successfully completed the recruitment process.")
        for idx, row in pool_data.iterrows():
            active_stages = stages if row.get('Has Skill Test', True) else [s for s in stages if s != "Skill Test"]
            completed_date = str(row.get('Completed Date', '') or '').strip()
            pool_status = completed_date if completed_date else "Completed"
            pic_info = f"PIC: {row.get('PIC', 'Unassigned')}" if "PIC" in row else ""
            hire_type = row.get('Hire Type', 'Additional')
            if hire_type == 'Replacement' and row.get('Replacement For'):
                hire_type_info = f"Replacement for {row['Replacement For']}"
            else:
                hire_type_info = "Additional"
            status_label_pos = row.get('Status', 'Contract') or 'Contract'
            _inline_anchor(f"div-pool-{idx}")
            with st.expander(f"**{row['Job Position']}** • {pool_status} • {pic_info} • {hire_type_info} • {status_label_pos}"):
                progress_pct = calculate_position_progress(row, stages)
                badge_class, badge_text = get_progress_badge(progress_pct)
                st.markdown(f'<span class="progress-badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### Hiring Stages")
                from src.views.components.stage_indicator import render_stage_indicator
                render_stage_indicator(row, active_stages)
                if row.get("Notes"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("#### Notes")
                    st.info(row["Notes"])
                if "Last Updated" in row:
                    st.caption(f"Last Updated: {row['Last Updated']}")


def _render_candidates_tab(user_div: str, filtered_data: pd.DataFrame) -> None:
    """
    Render the Candidates tab for division users.
    Shows escalated candidates (resume-only view) and lets reviewers submit
    Soft Skill / Value KG / Technical Skill ratings (1–4) plus a decision:
    Rekomendasi, Tidak Direkomendasi, or Cadangan.
    """
    from src.services.candidate_service import (
        get_candidates_for_division, submit_skill_review,
        reset_candidate_status, clear_candidate_comments,
        fetch_job_positions_from_cv_matching
    )
    from src.services.feedback_service import add_feedback_for_position
    from src.views.components.candidate_card import render_candidate_card
    from src.models.candidate import Candidate
    from src.utils.helpers import extract_technical_skills_from_jd

    st.markdown("### Candidates for User Interview")
    st.info(
        "Tinjau resume kandidat lalu beri penilaian Soft Skill, Value KG, dan "
        "Technical Skill (skala 1–4). Pilih: Rekomendasi, Tidak Direkomendasi, "
        "atau Cadangan."
    )

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

    # Position filter
    position_options = ["All"] + list(positions.keys())
    position_filter = st.selectbox(
        "Filter by position",
        position_options,
        key="div_candidate_position_filter"
    )

    # Map decision → feedback action understood downstream by feedback_service
    decision_to_action = {
        Candidate.STATUS_RECOMMENDED: "approve",
        Candidate.STATUS_NOT_RECOMMENDED: "reject",
        Candidate.STATUS_RESERVE: "reserve",
    }
    
    cv_positions_df = fetch_job_positions_from_cv_matching()

    for position_key, pos_candidates in positions.items():
        # Apply position filter
        if position_filter != "All" and position_key != position_filter:
            continue

        # Get job description for feedback and auto-skills
        job_desc = ""
        if cv_positions_df is not None and not cv_positions_df.empty:
            match = cv_positions_df[cv_positions_df["Job Position"] == position_key]
            if not match.empty:
                job_desc = match.iloc[0].get("Job Description", "")
        
        # Auto-extract skills if we found a JD
        auto_skills = extract_technical_skills_from_jd(job_desc) if job_desc else []

        if not pos_candidates:
            continue

        st.markdown(f"---")
        st.markdown(f"#### {position_key}")
        st.caption(f"{len(pos_candidates)} candidate(s)")

        for i, candidate in enumerate(pos_candidates):
            def make_review_handler(cand=candidate, pos=position_key, jd=job_desc):
                def handler(candidate_id, ratings, note, decision):
                    ok = submit_skill_review(
                        candidate_id=candidate_id,
                        reviewer_division=user_div,
                        reviewer=f"User {user_div}",
                        ratings=ratings,
                        note=note,
                        decision=decision,
                    )
                    if not ok:
                        st.error("Failed to submit review.")
                        return
                    # Mirror to feedback for cv-matching-auto sync
                    tech_detail = ""
                    tech_skills = ratings.get("technical_skills", {})
                    if tech_skills:
                        tech_parts = ", ".join(f"{k}: {v}/4" for k, v in tech_skills.items())
                        tech_detail = f"Technical Skills: {tech_parts}."
                    else:
                        tech_detail = f"Technical Skill: {ratings['technical_skill']}/4."
                    feedback_text = (
                        f"Soft Skill: {ratings['soft_skill']}/4, "
                        f"Value KG: {ratings['value_kg']}/4, "
                        f"{tech_detail} "
                        f"Decision: {decision}."
                    )
                    if note:
                        feedback_text += f" Catatan: {note}"
                    try:
                        add_feedback_for_position(
                            pos, user_div, jd, f"User {user_div}",
                            cand.name,
                            decision_to_action.get(decision, "comment"),
                            feedback_text,
                        )
                    except Exception:
                        pass
                    st.success(f"Penilaian disimpan: {decision}")
                    st.rerun()
                return handler

            def make_reset_handler(cid):
                def handler(candidate_id):
                    reset_candidate_status(candidate_id)
                    st.success("Status reset to Escalated!")
                    st.rerun()
                return handler

            def make_clear_comments_handler(cid):
                def handler(candidate_id):
                    clear_candidate_comments(candidate_id)
                    st.success("Comments cleared!")
                    st.rerun()
                return handler

            render_candidate_card(
                candidate,
                key_prefix=f"div_cand_{position_key}_{i}",
                show_actions=True,
                division_view=True,
                reviewer_division=user_div,
                on_skill_review=make_review_handler(),
                on_reset=make_reset_handler(candidate.id),
                on_clear_comments=make_clear_comments_handler(candidate.id),
                auto_skills=auto_skills,
            )
