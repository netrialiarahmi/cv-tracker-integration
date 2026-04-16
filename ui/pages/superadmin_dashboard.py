"""
HR Superadmin dashboard page - full system access with user management.
"""

import streamlit as st
import pandas as pd
from streamlit.components.v1 import html
from streamlit_option_menu import option_menu
from datetime import datetime
from ui.components.header import render_header
from ui.components.data_table import render_reference_table
from models.user import add_new_user, update_user, delete_user
from services.hiring_service import add_new_position, render_position_form
from core.auth import get_hr_roles
from config.settings import BASE_STAGES
from utils.validators import validate_password
from models.hiring import calculate_position_progress, get_progress_badge


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
    st.session_state.setdefault("sa_year_from", "All")
    st.session_state.setdefault("sa_year_to", "All")
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
    Render the HR Superadmin dashboard with user management and full hiring pipeline access.
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
        options=["User Management", "Hiring Pipeline", "Screening Results"],
        icons=["people-fill", "bar-chart-line-fill", "file-earmark-person-fill"],
        orientation="horizontal",
        default_index=st.session_state.get("hrsuper_selected_menu", 0),
        manual_select=st.session_state.get("hrsuper_selected_menu", 0),
        key="hrsuper_option_menu",
        styles={
            "container": {
                "padding": "5px 0",
                "background-color": "#2563eb",
                "border-radius": "8px",
                "width": "100%",
                "margin-bottom": "2rem",
            },
            "icon": {"color": "#f9fafb", "font-size": "18px"},
            "nav-link": {
                "color": "#f9fafb",
                "font-size": "15px",
                "text-align": "center",
                "margin": "0 10px",
                "--hover-color": "rgba(239, 68, 68, 0.2)",
                "padding": "10px 10px",
                "border-radius": "16px",
            },
            "nav-link-selected": {
                "background-color": "#ef4444",
                "color": "#ffffff",
                "font-weight": "bold",
                "border-radius": "8px",
                "padding": "10px 15px",
                "box-shadow": "0px 4px 10px rgba(239, 68, 68, 0.3)",
            },
        },
    )
    
    selected = 0 if selected_menu == "User Management" else (1 if selected_menu == "Hiring Pipeline" else 2)
    if st.session_state.get("hrsuper_selected_menu") != selected:
        st.session_state.hrsuper_selected_menu = selected
        st.rerun()
    
    # Render selected page
    if selected == 0:
        render_user_management()
    elif selected == 1:
        render_hiring_pipeline()
    else:
        render_screening_dashboard()


def render_user_management() -> None:
    """
    Render user management tab for managing division users.
    """
    st.markdown('<div class="content-card"><h3>Registered Users</h3>', unsafe_allow_html=True)
    for division in st.session_state.credentials.keys():
        col1, col2, col3 = st.columns([4, 3, 2])
        with col1:
            st.write(f"**{division}**")
        with col2:
            st.write(st.session_state.credentials[division])
        with col3:
            if division != "Human Resource":
                action_cols = st.columns(2)
                with action_cols[0]:
                    if st.button("✏️", key=f"edit_btn_{division}", use_container_width=True, help="Edit"):
                        st.session_state.editing_user = division
                        st.rerun()
                with action_cols[1]:
                    if st.button("🗑️", key=f"delete_btn_{division}", use_container_width=True, help="Delete"):
                        st.session_state.deleting_user = division
                        st.rerun()
            else:
                st.write("🔒 Protected")
        
        if st.session_state.editing_user == division:
            st.markdown("---")
            edit_col1, edit_col2 = st.columns(2)
            with edit_col1:
                new_div_name = st.text_input("Division Name", value=division, key=f"edit_name_{division}")
            with edit_col2:
                new_password = st.text_input("New Password (leave blank to keep current)", type="password", placeholder="Leave blank to keep current", key=f"edit_pass_{division}")
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("💾 Save", key=f"save_{division}", use_container_width=True, type="primary"):
                    if not new_div_name:
                        st.error("❌ Division name is required.")
                    elif new_password and not validate_password(new_password):
                        st.error("❌ Password must be at least 4 characters.")
                    else:
                        password_to_use = new_password if new_password else st.session_state.credentials[division]
                        update_user(division, new_div_name, password_to_use)
                        st.session_state.editing_user = None
                        st.success("✅ User updated successfully")
                        st.rerun()
            with btn_col2:
                if st.button("Cancel", key=f"cancel_{division}", use_container_width=True):
                    st.session_state.editing_user = None
                    st.rerun()
            st.markdown("---")
        
        if "deleting_user" in st.session_state and st.session_state.deleting_user == division:
            st.markdown("---")
            st.warning(f"⚠️ Delete '{division}'? This will also delete all hiring data.")
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("✅ Delete", key=f"confirm_delete_{division}", use_container_width=True, type="primary"):
                    if delete_user(division):
                        st.session_state.deleting_user = None
                        st.success(f"✅ '{division}' deleted")
                        st.rerun()
            with btn_col2:
                if st.button("Cancel", key=f"cancel_delete_{division}", use_container_width=True):
                    st.session_state.deleting_user = None
                    st.rerun()
            st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Add New Division", expanded=False):
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            new_div = st.text_input("Division Name", placeholder="e.g., Marketing")
        with col2:
            new_pwd = st.text_input("Password", type="password", placeholder="Min. 4 characters")
        if st.button("Create Division", use_container_width=True):
            if not new_div or not new_pwd:
                st.error("❌ All fields required")
            elif not validate_password(new_pwd):
                st.error("❌ Password too short (min. 4 characters)")
            elif new_div in st.session_state.credentials:
                st.error("❌ Division already exists")
            else:
                add_new_user(new_div, new_pwd)
                st.success(f"✅ Division '{new_div}' created successfully")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


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
    
    if st.button("➕ Add Position", type="primary"):
        if new_position:
            add_new_position(new_division, new_position, has_skill_test, new_pic)
            st.success(f"✅ Position '{new_position}' added! (PIC: {new_pic or 'Unassigned'})")
            st.rerun()
        else:
            st.error("❌ Job title required")
    st.markdown('</div>', unsafe_allow_html=True)

    # Statistics - now based on filtered data
    if len(filtered_data) > 0:
        from ui.components.metrics import render_metrics
        from ui.components.progress_stepper import render_progress_stepper, filter_by_stage
        _section_anchor(SECTION_IDS["metrics"])
        st.markdown('<div class="content-card"><h3>Pipeline Metrics</h3>', unsafe_allow_html=True)
        render_metrics(filtered_data, interactive_key="sa_metric_filter")
        st.markdown('</div>', unsafe_allow_html=True)

        # Apply status filter
        active_filter = st.session_state.get("sa_metric_filter", "total")
        filtered_data = _filter_by_status(filtered_data, active_filter)

        # Stage stepper with clickable filtering
        st.markdown('<div class="content-card"><h3>Hiring Pipeline Stages</h3>', unsafe_allow_html=True)
        selected_stage = render_progress_stepper(filtered_data, session_key="sa_stage_filter", show_counts=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Apply stage filter
        if selected_stage:
            filtered_data = filter_by_stage(filtered_data, selected_stage)
    else:
        st.info("No positions match the current filters.")

    # Search bar with sort (positioned after metrics for visual flow)
    _section_anchor(SECTION_IDS["search"])
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    with col1:
        st.text_input(
            "Search",
            key="super_search",
            placeholder="Search by job title or division...",
            label_visibility="collapsed"
        )
    with col2:
        st.selectbox("Sort", ["Default", "Hiring Days ↑", "Hiring Days ↓"], key="sa_sort_by", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply year range filter
    year_from = st.session_state.get("sa_year_from", "All")
    year_to = st.session_state.get("sa_year_to", "All")
    
    if (year_from != "All" or year_to != "All") and "Created Date" in filtered_data.columns:
        def _in_year_range(date_str):
            if not date_str or pd.isna(date_str) or date_str == "":
                return False
            year = _extract_year_from_date(date_str)
            if year == 0:
                return False
            
            # If only year_from is set
            if year_from != "All" and year_to == "All":
                return year >= year_from
            # If only year_to is set
            elif year_from == "All" and year_to != "All":
                return year <= year_to
            # If both are set
            elif year_from != "All" and year_to != "All":
                return year_from <= year <= year_to
            return True
        
        filtered_data = filtered_data[filtered_data["Created Date"].apply(_in_year_range)]
    
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
    
    # Manage positions section with smooth, stateful pagination
    if len(filtered_data) > 0:
        _section_anchor(SECTION_IDS["manage"])
        st.markdown('<div class="content-card"><h3>Manage Positions</h3>', unsafe_allow_html=True)
        
        # Year range filter
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown("### ")
        with col2:
            # Extract available years from Created Date
            available_years = []
            if "Created Date" in filtered_data.columns:
                for date_str in filtered_data["Created Date"].dropna():
                    try:
                        for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
                            try:
                                year = datetime.strptime(str(date_str), fmt).year
                                if year not in available_years:
                                    available_years.append(year)
                                break
                            except ValueError:
                                continue
                    except Exception:
                        pass
            available_years = sorted(available_years) if available_years else []
            
            # Year range options
            if available_years:
                min_year = min(available_years)
                max_year = max(available_years)
                year_options = ["All"] + list(range(min_year, max_year + 1))
            else:
                year_options = ["All"]
            
            st.selectbox("From Year", year_options, key="sa_year_from", label_visibility="collapsed")
        with col3:
            st.selectbox("To Year", year_options, key="sa_year_to", label_visibility="collapsed")
        
        # --- Pagination Config ---
        items_per_page = 10  # Fixed at 10 items per page
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
                status_label = "🧊 Freeze"
            elif is_completed:
                status_label = "✅ Completed"
            else:
                # Calculate hiring days for in-progress positions
                created_date = row.get('Created Date', '')
                if created_date and str(created_date).strip():
                    hiring_days = _calculate_hiring_days(created_date)
                    status_label = f"{hiring_days} days" if hiring_days > 0 else "⚠️ No Date"
                else:
                    status_label = "⚠️ No Date"
            
            # Show PIC in expander title
            pic_display = f"👤 {row.get('PIC', 'Unassigned')}" if row.get('PIC') else "👤 Unassigned"
            # Show hire type info (Replacement For / Additional)
            hire_type = row.get('Hire Type', 'Additional')
            if hire_type == 'Replacement' and row.get('Replacement For'):
                hire_type_info = f"Replacement for {row['Replacement For']}"
            else:
                hire_type_info = "Additional"
            
            expander_title = f"{row['Job Position']} • {status_label} • {pic_display} • {hire_type_info}"
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
            
            # Center the pagination
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
    Render Screening Results tab - fetch and display CV Matching results,
    link positions, and escalate candidates.
    """
    from services.candidate_service import (
        fetch_screening_results, fetch_job_positions_from_cv_matching,
        escalate_candidate, get_candidates_for_position, load_candidates
    )
    from ui.components.screening_table import render_screening_table
    from core.data_manager import save_hiring_data

    st.markdown('<div class="content-card"><h3>🔗 Position Linking & Screening Results</h3>', unsafe_allow_html=True)
    st.info("Link hiring positions to CV Matching positions, then view screening results and escalate candidates to user interview.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Fetch CV matching positions (cached in session)
    if st.button("🔄 Refresh CV Matching Data", key="refresh_cv_data"):
        st.session_state.cv_positions_cache = None
        st.session_state.screening_cache = {}

    if st.session_state.cv_positions_cache is None:
        cv_positions_df = fetch_job_positions_from_cv_matching()
        if cv_positions_df is not None and not cv_positions_df.empty:
            st.session_state.cv_positions_cache = cv_positions_df["Job Position"].tolist()
        else:
            st.session_state.cv_positions_cache = []

    cv_position_names = st.session_state.cv_positions_cache

    if not cv_position_names:
        st.warning("⚠️ Could not fetch positions from CV Matching repo. Check GitHub token.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Get hiring positions that have linked CV matching positions
    hiring_data = st.session_state.hiring_data.copy()

    # Ensure CV Matching Position column exists
    if "CV Matching Position" not in hiring_data.columns:
        hiring_data["CV Matching Position"] = ""
        st.session_state.hiring_data["CV Matching Position"] = ""

    # Position linking section
    st.markdown('<div class="content-card"><h3>🔗 Link Positions</h3>', unsafe_allow_html=True)
    st.caption("Map each hiring tracker position to its CV Matching counterpart.")

    for idx, row in hiring_data.iterrows():
        col1, col2 = st.columns([3, 4])
        with col1:
            st.markdown(f"**{row['Job Position']}** ({row['Division']})")
        with col2:
            current_link = row.get("CV Matching Position", "")
            options = ["(Not linked)"] + cv_position_names
            current_idx = 0
            if current_link and current_link in cv_position_names:
                current_idx = cv_position_names.index(current_link) + 1

            new_link = st.selectbox(
                f"CV Matching Position for {row['Job Position']}",
                options=options,
                index=current_idx,
                key=f"cv_link_{idx}",
                label_visibility="collapsed"
            )

            new_link_val = "" if new_link == "(Not linked)" else new_link
            if new_link_val != current_link:
                st.session_state.hiring_data.at[idx, "CV Matching Position"] = new_link_val
                save_hiring_data(st.session_state.hiring_data)
                st.success(f"✅ Linked to '{new_link_val or 'None'}'")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Screening results for linked positions
    linked_positions = hiring_data[
        hiring_data["CV Matching Position"].astype(str).str.strip() != ""
    ]

    if linked_positions.empty:
        st.info("No positions linked to CV Matching yet. Use the dropdowns above to link positions.")
        return

    st.markdown('<div class="content-card"><h3>📊 Screening Results</h3>', unsafe_allow_html=True)

    # Build set of already-escalated emails
    all_candidates = load_candidates()
    escalated_emails = {c.get("email", "").lower() for c in all_candidates if c.get("email")}

    for idx, row in linked_positions.iterrows():
        cv_position = row["CV Matching Position"]
        position_key = row["Job Position"]
        division = row["Division"]

        st.markdown(f"### 📋 {position_key} → {cv_position}")

        # Fetch screening results (cached)
        cache_key = cv_position
        if cache_key not in st.session_state.screening_cache:
            results = fetch_screening_results(cv_position)
            st.session_state.screening_cache[cache_key] = results

        results_df = st.session_state.screening_cache.get(cache_key)

        def handle_escalate(row_dict, pk=position_key, div=division):
            user = st.session_state.get("hr_admin") or "HR Superadmin"
            candidate = escalate_candidate(row_dict, pk, div, user)
            st.success(f"✅ {candidate.name} escalated to user interview!")
            st.rerun()

        render_screening_table(
            results_df, position_key, division,
            escalated_emails, on_escalate=handle_escalate,
            key_prefix=f"sa_screen_{idx}"
        )

    st.markdown('</div>', unsafe_allow_html=True)