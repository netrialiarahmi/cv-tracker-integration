"""
HR Superadmin dashboard page - full system access with hiring pipeline oversight.
"""

import streamlit as st
import pandas as pd
from streamlit.components.v1 import html
from streamlit_option_menu import option_menu
from datetime import datetime
from src.views.components.header import render_header
from src.views.components.data_table import render_reference_table
from src.services.hiring_service import add_new_position, render_position_form
from src.controllers.auth import get_hr_roles
from src.config.settings import BASE_STAGES
from src.models.hiring import calculate_position_progress, get_progress_badge
from src.utils.helpers import (
    filter_by_year_range, available_years as _available_years,
    get_current_stage, get_stage_zone, split_by_pipeline_zone,
)


SECTION_IDS = {
    "top": "sa-top",
    "search": "sa-search",
    "metrics": "sa-metrics",
    "add": "sa-add-position",
    "manage": "sa-manage",
    "summary": "sa-summary"
}
SCROLL_STORAGE_KEY = "sa_pipeline_scroll"


def _init_pipeline_state() -> None:
    st.session_state.setdefault("super_search", "")
    st.session_state.setdefault("sa_nav_target", None)
    st.session_state.setdefault("sa_current_section", SECTION_IDS["top"])
    st.session_state.setdefault("sa_metric_filter", "total")
    st.session_state.setdefault("sa_year_from", 2026)
    st.session_state.setdefault("sa_year_to", 2026)
    st.session_state.setdefault("sa_sort_by", "Default")


def _section_anchor(section_id: str) -> None:
    """Create an anchor and track it as the current section."""
    st.markdown(f'<div id="{section_id}"></div>', unsafe_allow_html=True)
    st.session_state.sa_current_section = section_id


def _inline_anchor(anchor_id: str) -> None:
    st.markdown(f'<div id="{anchor_id}"></div>', unsafe_allow_html=True)


def _navigate_to(section_id: str) -> None:
    st.session_state.sa_nav_target = section_id
    st.session_state.manage_position_page = 1
    st.rerun()


def _get_pic_display_name(pic_key: str) -> str:
    """Get display name for PIC key from HR roles config."""
    admins = get_hr_roles().get("admins", {})
    if pic_key in admins:
        return admins[pic_key].get("name", pic_key)
    return pic_key



def _calculate_hiring_days(created_date: str) -> int:
    """Calculate hiring days from created date to now."""
    if not created_date or pd.isna(created_date) or created_date == "":
        return 0
    
    try:
        # Try to parse different date formats
        for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
            try:
                created = datetime.strptime(str(created_date), fmt)
                now = datetime.now()
                delta = now - created
                return delta.days
            except ValueError:
                continue
        return 0
    except Exception:
        return 0


def _extract_year_from_date(date_str: str) -> int:
    """Extract year from date string."""
    if not date_str or pd.isna(date_str) or date_str == "":
        return 0
    
    try:
        for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
            try:
                return datetime.strptime(str(date_str), fmt).year
            except ValueError:
                continue
        return 0
    except Exception:
        return 0


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
    target = st.session_state.get("sa_nav_target", "") or ""
    script = f"""
    <script>
    const storageKey = '{SCROLL_STORAGE_KEY}';
    const target = '{target}';
    const saved = window.sessionStorage.getItem(storageKey);
    const restoreScroll = () => {{
        if (target) {{
            const el = document.getElementById(target);
            if (el) {{
                el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                window.sessionStorage.setItem(storageKey, window.scrollY.toString());
                return;
            }}
        }}
        if (saved) {{
            window.scrollTo(0, parseFloat(saved));
        }}
    }};
    window.addEventListener('load', () => setTimeout(restoreScroll, 50));
    window.addEventListener('scroll', () => {{
        window.sessionStorage.setItem(storageKey, window.scrollY.toString());
    }});
    </script>
    """
    html(script, height=0)
    if target:
        st.session_state.sa_nav_target = None



def render() -> None:
    """
    Render the HR Superadmin dashboard with full hiring pipeline access.
    """
    _init_pipeline_state()
    render_header(
        page_title="HR Superadmin Dashboard",
        subtitle="System control & hiring pipeline oversight",
        kicker="Kompas.com Talent Intelligence",
    )

    # Navigation Bar with manual_select to prevent rerun
    selected_menu = option_menu(
        menu_title=None,
        options=["Hiring Pipeline", "Screening Results"],
        icons=["bar-chart-line-fill", "file-earmark-person-fill"],
        orientation="horizontal",
        default_index=st.session_state.get("hrsuper_selected_menu", 0),
        manual_select=st.session_state.get("hrsuper_selected_menu", 0),
        key="hrsuper_option_menu",
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
    if st.session_state.get("hrsuper_selected_menu") != selected:
        st.session_state.hrsuper_selected_menu = selected
        st.rerun()
    
    # Render selected page
    if selected == 0:
        render_hiring_pipeline()
    else:
        render_screening_dashboard()


def render_hiring_pipeline() -> None:
    """
    Render hiring pipeline management tab.
    """
    _render_scroll_manager()
    filtered_data = st.session_state.hiring_data.copy()
    display_hiring_management(filtered_data)


def display_hiring_management(filtered_data: pd.DataFrame) -> None:
    """
    Display hiring management interface for HR Superadmin.
    
    Args:
        filtered_data: DataFrame containing hiring data
    """
    hr_roles = get_hr_roles()
    base_stages = BASE_STAGES
    
    # Apply search filter early (even though UI is below) to keep metrics aligned with the current query
    search_term = st.session_state.get("super_search", "")
    if search_term:
        filtered_data = filtered_data[
            (filtered_data["Job Position"].str.contains(search_term, case=False, na=False)) |
            (filtered_data["Division"].str.contains(search_term, case=False, na=False))
        ]

    # Apply status filter early (Intern / Freelance / Contract) — multiselect
    status_filter = st.session_state.get("sa_status_filter", ["All Status"])
    if isinstance(status_filter, str):
        status_filter = [status_filter]  # backward compat
    if status_filter and "All Status" not in status_filter and "Status" in filtered_data.columns:
        filtered_data = filtered_data[
            filtered_data["Status"].astype(str).str.strip().isin(status_filter)
        ]

    # Add new position - ONLY FOR SUPERADMIN (moved to the top)
    _section_anchor(SECTION_IDS["add"])
    st.markdown('<div class="content-card"><h3>Add New Position</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([3, 3, 3])
    with col1:
        new_division = st.selectbox("Division", options=list(st.session_state.credentials.keys()), key="add_div")
    with col2:
        new_position = st.text_input("Job Title", placeholder="Enter job title...", key="add_pos")
    with col3:
        try:
            hr_admins = list(hr_roles.get("admins", {}).keys())
        except (KeyError, AttributeError):
            hr_admins = []
        new_pic = st.selectbox("Assign PIC (HR Admin)", options=[""] + hr_admins, key="add_pic")
    
    has_skill_test = st.checkbox(
        "This position includes Skill Test",
        value=True,
        key="add_skilltest"
    )
    
    if st.button("Add Position", type="primary"):
        if new_position:
            add_new_position(new_division, new_position, has_skill_test, new_pic)
            st.success(f"Position '{new_position}' added! (PIC: {new_pic or 'Unassigned'})")
            st.rerun()
        else:
            st.error("Job title required")
    st.markdown('</div>', unsafe_allow_html=True)

    # Statistics - now based on filtered data
    if len(filtered_data) > 0:
        from src.views.components.metrics import render_metrics
        from src.views.components.progress_stepper import render_progress_stepper, filter_by_stage
        # Year-range filter applied to everything (metrics + stages)
        years = _available_years(filtered_data)
        year_options = ["All"] + list(range(min(years), max(years) + 1)) if years else ["All"]
        
        _section_anchor(SECTION_IDS["metrics"])
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        # All Filters (Search, Status, Year, Sort)
        f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns([3, 2, 1, 1, 1.2])
        with f_col1:
            st.text_input("Search", key="super_search", placeholder="Search by job title or division...", label_visibility="collapsed")
        with f_col2:
            st.multiselect("Status", options=["All Status", "Contract", "Intern", "Freelance"], default=st.session_state.get("sa_status_filter", ["All Status"]), key="sa_status_filter", label_visibility="collapsed")
        with f_col3:
            st.selectbox("From Year", year_options, key="sa_year_from", label_visibility="collapsed")
        with f_col4:
            st.selectbox("To Year", year_options, key="sa_year_to", label_visibility="collapsed")
        with f_col5:
            st.selectbox("Sort", ["Default", "Hiring Days ↑", "Hiring Days ↓"], key="sa_sort_by", label_visibility="collapsed")
            
        st.markdown('<h3 style="margin-top: 1rem;">Pipeline Metrics</h3>', unsafe_allow_html=True)
            
        filtered_data = filter_by_year_range(
            filtered_data,
            st.session_state.get("sa_year_from", 2026),
            st.session_state.get("sa_year_to", 2026),
        )

        render_metrics(filtered_data, interactive_key="sa_metric_filter")
        st.markdown('</div>', unsafe_allow_html=True)

        # Apply metric card filter (e.g., clicking 'In Progress' filters the data)
        active_filter = st.session_state.get("sa_metric_filter", "total")
        filtered_data = _filter_by_status(filtered_data, active_filter)

        st.markdown('<div class="content-card"><h3>Hiring Pipeline Stages</h3>', unsafe_allow_html=True)

        # Stage stepper with clickable filtering
        selected_stage = render_progress_stepper(filtered_data, session_key="sa_stage_filter", show_counts=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Apply stage filter
        if selected_stage:
            filtered_data = filter_by_stage(filtered_data, selected_stage)
    else:
        st.info("No positions match the current filters.")

    # Apply sorting
    sort_by = st.session_state.get("sa_sort_by", "Default")
    if sort_by != "Default" and "Created Date" in filtered_data.columns:
        # Calculate hiring days for each row
        # Entries without valid hiring days (completed, freeze, no date) get a special value
        def _get_sort_priority(row):
            """
            Returns (priority, hiring_days) tuple for sorting:
            - priority 0: active positions with valid hiring days (will be sorted)
            - priority 1: completed/freeze/no-date positions (pushed to end)
            """
            is_frozen = bool(row.get('Freeze', False))
            is_completed = bool(row.get('On Boarding', False)) and not is_frozen
            created_date = row.get('Created Date', '')
            
            if is_frozen or is_completed:
                return (1, 0)  # Push to end
            
            if not created_date or str(created_date).strip() == '':
                return (1, 0)  # Push to end (no date)
            
            hiring_days = _calculate_hiring_days(created_date)
            if hiring_days <= 0:
                return (1, 0)  # Push to end (invalid date)
            
            return (0, hiring_days)  # Active with valid days
        
        # Apply sort priority
        sort_data = filtered_data.apply(_get_sort_priority, axis=1)
        filtered_data["_sort_priority"] = sort_data.apply(lambda x: x[0])
        filtered_data["_hiring_days"] = sort_data.apply(lambda x: x[1])
        
        if sort_by == "Hiring Days ↑":
            # Ascending: shortest days first, then push non-sortable to end
            filtered_data = filtered_data.sort_values(
                ["_sort_priority", "_hiring_days"], 
                ascending=[True, True]
            )
        elif sort_by == "Hiring Days ↓":
            # Descending: longest days first, then push non-sortable to end
            filtered_data = filtered_data.sort_values(
                ["_sort_priority", "_hiring_days"], 
                ascending=[True, False]
            )
        # Remove the temporary columns
        filtered_data = filtered_data.drop(columns=["_sort_priority", "_hiring_days"])

    # --- Sort by zone priority (active first, completed last) ---
    if len(filtered_data) > 0:
        filtered_data["_zone"] = filtered_data.apply(get_stage_zone, axis=1)
        filtered_data = filtered_data.sort_values("_zone", kind="stable").drop(columns=["_zone"])

    # Manage positions section with smooth, stateful pagination
    if len(filtered_data) > 0:
        _section_anchor(SECTION_IDS["manage"])
        st.markdown('<div class="content-card"><h3>Manage Positions</h3>', unsafe_allow_html=True)

        # --- Pagination Config ---
        items_per_page = 7  # Fit manage positions + pagination in one viewport
        total_positions = len(filtered_data)
        total_pages = max(1, (total_positions + items_per_page - 1) // items_per_page)
        # Reset to page 1 if data changes
        if (
            'manage_position_prev_total' not in st.session_state or
            st.session_state.manage_position_prev_total != total_positions
        ):
            st.session_state.manage_position_page = 1
            st.session_state.manage_position_prev_total = total_positions
        page = st.session_state.get('manage_position_page', 1)
        # --- Data Slicing (no recompute on page change) ---
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_positions)
        paged_data = filtered_data.iloc[start_idx:end_idx]
        for idx, row in paged_data.iterrows():
            # Dynamic stages depending on whether position uses skill test
            if "Has Skill Test" in row and not row["Has Skill Test"]:
                stages = [s for s in base_stages if s != "Skill Test"]
            else:
                stages = base_stages
            progress_pct = calculate_position_progress(row, base_stages)
            badge_class, badge_text = get_progress_badge(progress_pct)
            
            # Freeze detection: use Freeze column if present, else fallback to Notes
            is_frozen = bool(row.get('Freeze', False))
            is_completed = bool(row.get('On Boarding', False)) and not is_frozen
            
            # Determine status label
            if is_frozen:
                status_label = "Freeze"
            elif is_completed:
                status_label = "Completed"
            else:
                # Calculate hiring days for in-progress positions
                created_date = row.get('Created Date', '')
                if created_date and str(created_date).strip():
                    hiring_days = _calculate_hiring_days(created_date)
                    status_label = f"{hiring_days} days" if hiring_days > 0 else "No Date"
                else:
                    status_label = "No Date"
            
            # Show PIC with display name
            pic_raw = row.get('PIC', 'Unassigned') or 'Unassigned'
            pic_display = _get_pic_display_name(pic_raw)
            # Show hire type info (Replacement For / Additional)
            hire_type = row.get('Hire Type', 'Additional')
            if hire_type == 'Replacement' and row.get('Replacement For'):
                hire_type_info = f"Replacement for {row['Replacement For']}"
            else:
                hire_type_info = "Additional"
            status_label_pos = row.get('Status', 'Contract') or 'Contract'

            current_stage = get_current_stage(row)
            zone = get_stage_zone(row)
            stage_part = f" · {current_stage}" if current_stage and current_stage != "On Boarding" else ""
            expander_title = f"{row['Job Position']}{stage_part} · {status_label} · {pic_display} · {hire_type_info} · {status_label_pos}"
            anchor_id = f"sa-position-{idx}"
            _inline_anchor(anchor_id)
            with st.expander(expander_title):
                can_edit = True  # Superadmin can edit everything
                render_position_form(idx, row, can_edit, stages)
        st.markdown('</div>', unsafe_allow_html=True)
        # --- Compact pagination ---
        if total_pages > 1:
            prev_disabled = (page == 1)
            next_disabled = (page == total_pages)
            
            outer_cols = st.columns([2, 3, 2])
            with outer_cols[1]:
                cols = st.columns([1, 3, 1])
                with cols[0]:
                    if st.button("←", key="manage_prev", disabled=prev_disabled, use_container_width=True, help="Previous", type="secondary"):
                        st.session_state.manage_position_page = max(1, page - 1)
                        st.rerun()
                with cols[1]:
                    st.markdown(f"<div style='text-align:center;padding:0.5rem 0;color:#2563eb;font-size:0.9rem;font-weight:600;'>Page {page} of {total_pages}</div>", unsafe_allow_html=True)
                with cols[2]:
                    if st.button("→", key="manage_next", disabled=next_disabled, use_container_width=True, help="Next", type="secondary"):
                        st.session_state.manage_position_page = min(total_pages, page + 1)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if len(filtered_data) > 0:
        _section_anchor(SECTION_IDS["summary"])
        st.markdown("<br>", unsafe_allow_html=True)
        render_reference_table(
            filtered_data,
            caption=""
        )


def render_screening_dashboard() -> None:
    """
    Render Screening Results tab - fetch and display CV Matching results
    for positions linked via data/position-links.json.
    UI mirrors the CV Matching dashboard: dropdown to select position, then results.
    """
    from src.services.candidate_service import (
        fetch_screening_results, escalate_candidate, load_candidates,
        delete_candidate, reset_candidate_status
    )
    from src.views.components.screening_table import render_screening_table
    from src.services.linking_service import load_position_links

    position_links = load_position_links()

    if not position_links:
        st.info("No positions linked to CV Matching yet.")
        return

    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### Screening Dashboard")

    # Build position options grouped by CV Matching position (deduplicate)
    # Exclude Pool (completed) positions from the dropdown
    cv_to_hiring = {}
    hiring_data = st.session_state.hiring_data
    for job_position, cv_position in position_links.items():
        match = hiring_data[hiring_data["Job Position"] == job_position]
        if not match.empty:
            row = match.iloc[0]
            # Skip completed/pool positions (zone 3)
            if get_stage_zone(row) == 3:
                continue
            division = row["Division"]
            if cv_position not in cv_to_hiring:
                cv_to_hiring[cv_position] = []
            cv_to_hiring[cv_position].append((job_position, division))

    cv_position_names = sorted(cv_to_hiring.keys())

    col_select, col_refresh = st.columns([6, 1])
    with col_select:
        selected_cv = st.selectbox(
            "Pilih posisi untuk melihat hasil screening",
            options=cv_position_names,
            key="sa_screening_position"
        )
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Refresh", key="refresh_cv_data"):
            st.session_state.screening_cache = {}
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    if not selected_cv:
        return

    # Get linked hiring positions for selected CV position
    linked_entries = cv_to_hiring.get(selected_cv, [])
    job_position = linked_entries[0][0] if linked_entries else selected_cv
    division = linked_entries[0][1] if linked_entries else ""

    # Check pipeline zone for selected position — warn if Offering+
    hiring_data = st.session_state.hiring_data
    pos_match = hiring_data[hiring_data["Job Position"] == job_position]
    if not pos_match.empty:
        pos_zone = get_stage_zone(pos_match.iloc[0])
        if pos_zone == 3:
            st.info("ℹ️ Posisi ini sudah **selesai** (masuk Pool). Screening tidak diperlukan.")
            return
        if pos_zone == 2:
            st.warning("⚠️ Posisi ini sudah di tahap **Offering / Contract Sign**. Screening kandidat baru tidak diprioritaskan.")

    # Fetch screening results (cached)
    cache_key = selected_cv
    if cache_key not in st.session_state.screening_cache:
        results = fetch_screening_results(selected_cv)
        st.session_state.screening_cache[cache_key] = results

    results_df = st.session_state.screening_cache.get(cache_key)

    # Build set of already-escalated emails
    all_candidates = load_candidates()
    escalated_emails = {c.get("email", "").lower() for c in all_candidates if c.get("email")}

    def handle_escalate(row_dict, pk=job_position, div=division):
        user = st.session_state.get("hr_admin") or "HR Superadmin"
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
        key_prefix=f"sa_screen_{selected_cv.replace(' ', '_')}"
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
                if st.button("Reset Status", key=f"sa_reset_status_{c.id}",
                             use_container_width=True):
                    reset_candidate_status(c.id)
                    st.success(f"{c.name} status reset to Escalated!")
                    st.rerun()