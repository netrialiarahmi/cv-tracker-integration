"""HR Admin dashboard page - PIC-filtered hiring management with briefing UX."""

import streamlit as st
import pandas as pd
from streamlit.components.v1 import html
from streamlit_option_menu import option_menu

from src.views.components.header import render_header
from src.views.components.data_table import render_reference_table
from src.services.hiring_service import render_position_form
from src.config.settings import BASE_STAGES
from src.models.hiring import calculate_position_progress, get_progress_badge
from src.utils.helpers import filter_by_year_range, available_years as _available_years


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
    st.session_state.setdefault("ad_year_from", "All")
    st.session_state.setdefault("ad_year_to", "All")


def _get_pic_display_name(pic_key: str) -> str:
    """Get display name for PIC key from HR roles config."""
    from src.controllers.auth import get_hr_roles
    roles = get_hr_roles()
    admins = roles.get("admins", {})
    if pic_key in admins:
        return admins[pic_key].get("name", pic_key)
    return pic_key


def _calculate_hiring_days(created_date: str) -> int:
    """Calculate hiring days from created date to now."""
    if not created_date or str(created_date).strip() == "":
        return 0
    from datetime import datetime
    import pandas as pd
    if pd.isna(created_date):
        return 0
    for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
        try:
            created = datetime.strptime(str(created_date), fmt)
            return (datetime.now() - created).days
        except ValueError:
            continue
    return 0


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
    display_name = st.session_state.get("hr_admin_name", assigned_pic)
    subtitle = f"Assignments for {display_name}" if display_name else "PIC-focused hiring queue"
    render_header(
        page_title="HR Admin Dashboard",
        subtitle=subtitle,
        kicker="Kompas.com Hiring Desk",
    )
    _render_scroll_manager()

    st.info(f"### Hiring Pipeline — Assigned to **{display_name}**")

    df = st.session_state.hiring_data.copy()

    pic_name = (st.session_state.hr_admin or "").strip().lower()
    if "PIC" in df.columns and pic_name:
        assigned = df[df["PIC"].astype(str).str.strip().str.lower() == pic_name].copy()
    else:
        assigned = pd.DataFrame()

    # Navigation Bar
    selected_menu = option_menu(
        menu_title=None,
        options=["Hiring Pipeline", "Screening Results"],
        icons=["bar-chart-line-fill", "file-earmark-person-fill"],
        orientation="horizontal",
        default_index=st.session_state.get("admin_selected_menu", 0),
        manual_select=st.session_state.get("admin_selected_menu", 0),
        key="admin_option_menu",
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
    if st.session_state.get("admin_selected_menu") != selected:
        st.session_state.admin_selected_menu = selected
        st.rerun()

    if selected == 0:
        _render_pipeline_tab(assigned)
    else:
        _render_screening_tab(assigned)


def _render_pipeline_tab(assigned: pd.DataFrame) -> None:
    """Render the hiring pipeline management tab."""
    if assigned.empty:
        st.warning("No positions assigned to you yet.")
    else:
        # Display summary metrics
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #2563eb 0%, #1e3a8a 100%);
                padding: 1.25rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(37,99,235,0.2);
                color: white;
            ">
                <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem;">
                    {len(assigned)}
                </div>
                <div style="font-size: 0.85rem; opacity: 0.85; font-weight: 500;">
                    Assigned Positions
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            unique_divisions = assigned['Division'].nunique()
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                padding: 1.25rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(15,23,42,0.15);
                color: white;
            ">
                <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem;">
                    {unique_divisions}
                </div>
                <div style="font-size: 0.85rem; opacity: 0.85; font-weight: 500;">
                    Divisions
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

    # Apply status filter early (Intern / Freelance / Contract)
    status_filter = st.session_state.get("ad_status_filter", "All")
    if status_filter and status_filter != "All" and "Status" in filtered_data.columns:
        filtered_data = filtered_data[
            filtered_data["Status"].astype(str).str.strip() == status_filter
        ]

    # Metrics (interactive like superadmin)
    if len(filtered_data) > 0:
        from src.views.components.metrics import render_metrics
        from src.views.components.progress_stepper import render_progress_stepper, filter_by_stage

        _anchor(AD_SECTION_IDS["metrics"])
        st.markdown('<div class="content-card"><h3>Pipeline Metrics</h3>', unsafe_allow_html=True)
        render_metrics(filtered_data, interactive_key="ad_metric_filter")
        st.markdown('</div>', unsafe_allow_html=True)

        # Apply pipeline status filter
        active_filter = st.session_state.get("ad_metric_filter", "total")
        filtered_data = _filter_by_status(filtered_data, active_filter)

        # Year-range filter (drives stage badge counts)
        years = _available_years(filtered_data)
        year_options = ["All"] + list(range(min(years), max(years) + 1)) if years else ["All"]
        st.markdown('<div class="content-card"><h3>Hiring Pipeline Stages</h3>', unsafe_allow_html=True)
        yc1, yc2, yc3 = st.columns([6, 1, 1])
        with yc2:
            st.selectbox("From Year", year_options, key="ad_year_from", label_visibility="collapsed")
        with yc3:
            st.selectbox("To Year", year_options, key="ad_year_to", label_visibility="collapsed")
        filtered_data = filter_by_year_range(
            filtered_data,
            st.session_state.get("ad_year_from", "All"),
            st.session_state.get("ad_year_to", "All"),
        )

        # Stage stepper with clickable filtering
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
    col1, col2 = st.columns([5, 1])
    with col1:
        st.text_input(
            "Search",
            key="ad_search",
            placeholder="Search by job title or division...",
            label_visibility="collapsed"
        )
    with col2:
        st.selectbox("Status", ["All", "Contract", "Intern", "Freelance"], key="ad_status_filter", label_visibility="collapsed")
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

            # Status label with hiring days
            is_frozen = bool(row.get('Freeze', False))
            is_completed = bool(row.get('On Boarding', False)) and not is_frozen
            if is_frozen:
                status_label = "Freeze"
            elif is_completed:
                status_label = "Completed"
            else:
                created_date = row.get('Created Date', '')
                if created_date and str(created_date).strip():
                    hiring_days = _calculate_hiring_days(created_date)
                    status_label = f"{hiring_days} days" if hiring_days > 0 else "In Progress"
                else:
                    status_label = "In Progress"

            pic_raw = row.get('PIC', 'Unassigned') or 'Unassigned'
            pic_display = _get_pic_display_name(pic_raw)
            hire_type = row.get('Hire Type', 'Additional')
            if hire_type == 'Replacement' and row.get('Replacement For'):
                hire_type_info = f"Replacement for {row['Replacement For']}"
            else:
                hire_type_info = "Additional"
            status_label_pos = row.get('Status', 'Contract') or 'Contract'

            anchor_id = f"ad-position-{idx}"
            _inline_anchor(anchor_id)
            with st.expander(f"{row['Job Position']} · {status_label} · {pic_display} · {hire_type_info} · {status_label_pos}"):
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
    from src.services.candidate_service import (
        fetch_screening_results, escalate_candidate, load_candidates,
        delete_candidate, reset_candidate_status
    )
    from src.views.components.screening_table import render_screening_table
    from src.services.linking_service import load_position_links

    if assigned.empty:
        st.info("No assigned positions to show screening results for.")
        return

    # Get position links from backend config, filtered to assigned positions
    position_links = load_position_links()
    assigned_positions = set(assigned["Job Position"].tolist())
    linked = {k: v for k, v in position_links.items() if k in assigned_positions}

    if not linked:
        st.info("No assigned positions are linked to CV Matching.")
        return

    # Deduplicate by CV position
    cv_to_hiring = {}
    for job_position, cv_position in linked.items():
        match = assigned[assigned["Job Position"] == job_position]
        if not match.empty:
            division = match.iloc[0]["Division"]
            if cv_position not in cv_to_hiring:
                cv_to_hiring[cv_position] = []
            cv_to_hiring[cv_position].append((job_position, division))

    cv_position_names = sorted(cv_to_hiring.keys())

    col_select, col_refresh = st.columns([6, 1])
    with col_select:
        selected_cv = st.selectbox(
            "Pilih posisi untuk melihat hasil screening",
            options=cv_position_names,
            key="ad_screening_position"
        )
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Refresh", key="ad_refresh_screening"):
            st.session_state.screening_cache = {}
            st.rerun()

    if not selected_cv:
        return

    linked_entries = cv_to_hiring.get(selected_cv, [])
    job_position = linked_entries[0][0] if linked_entries else selected_cv
    division = linked_entries[0][1] if linked_entries else ""

    cache_key = selected_cv
    if cache_key not in st.session_state.screening_cache:
        results = fetch_screening_results(selected_cv)
        st.session_state.screening_cache[cache_key] = results

    results_df = st.session_state.screening_cache.get(cache_key)

    all_candidates = load_candidates()
    escalated_emails = {c.get("email", "").lower() for c in all_candidates if c.get("email")}

    def handle_escalate(row_dict, pk=job_position, div=division):
        user = st.session_state.get("hr_admin", "HR Admin")
        candidate = escalate_candidate(row_dict, pk, div, user)
        st.success(f"{candidate.name} escalated to user interview!")
        st.rerun()

    def handle_reset_escalation(email):
        candidates = load_candidates()
        for c in candidates:
            if c.get("email", "").lower() == email.lower():
                delete_candidate(c["id"])
        st.success("Escalation reset!")
        st.rerun()

    render_screening_table(
        results_df, job_position, division,
        escalated_emails, on_escalate=handle_escalate,
        on_reset_escalation=handle_reset_escalation,
        key_prefix=f"ad_screen_{selected_cv.replace(' ', '_')}"
    )

    # --- Escalated Candidates Management ---
    from src.models.candidate import Candidate
    position_candidates = [
        Candidate(c) for c in all_candidates
        if c.get("position_key") == job_position
    ]
    actioned = [c for c in position_candidates
                if c.status in [Candidate.STATUS_APPROVED, Candidate.STATUS_REJECTED]]

    if actioned:
        st.markdown("---")
        st.markdown("### Candidate Status Management")
        st.caption("Reset candidates that were approved or rejected back to Escalated status.")
        for c in actioned:
            status_color = "#16a34a" if c.status == Candidate.STATUS_APPROVED else "#dc2626"
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(
                    f"**{c.name}** — "
                    f'<span style="color:{status_color};font-weight:600;">{c.status}</span>',
                    unsafe_allow_html=True
                )
            with col_btn:
                if st.button("Reset Status", key=f"ad_reset_status_{c.id}",
                             use_container_width=True):
                    reset_candidate_status(c.id)
                    st.success(f"{c.name} status reset to Escalated!")
                    st.rerun()
