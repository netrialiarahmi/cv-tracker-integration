"""
Shared hiring management service functions.
Contains common business logic for managing hiring positions.
"""

import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from typing import List, Dict, Any
from src.config.settings import BASE_STAGES
from src.repositories.data_manager import save_hiring_data
from src.controllers.auth import get_hr_roles
from src.models.hiring import calculate_position_progress, get_progress_badge
from src.views.components.progress_badge import render_progress_badge
from src.utils.formatters import get_current_timestamp


def add_new_position(division: str, position: str, has_skill_test: bool, pic: str = "") -> None:
    """
    Add a new hiring position to the system.
    
    Args:
        division: Division name
        position: Job position title
        has_skill_test: Whether position includes skill test
        pic: Person in charge (HR Admin)
    """
    new_row = pd.DataFrame({
        "Division": [division],
        "Job Position": [position],
        "Initial Interview (HR)": [False],
        "HR & User Interview (Stage 1)": [False],
        "Has Skill Test": [has_skill_test],
        "Skill Test": [False],
        "Final Interview": [False],
        "Offering": [False],
        "Contract Sign": [False],
        "On Boarding": [False],
        "PIC": [pic],
        "Notes": [""],
        "Last Updated": [get_current_timestamp()],
        "Hire Type": ["Additional"],
        "Replacement For": [""],
        "Job Description": [""]
    })
    st.session_state.hiring_data = pd.concat(
        [st.session_state.hiring_data, new_row], ignore_index=True
    )
    save_hiring_data(st.session_state.hiring_data)


def render_position_form(idx: int, row: pd.Series, can_edit: bool, stages: List[str]) -> None:
    """
    Render the form for editing a single hiring position.
    
    Args:
        idx: DataFrame index of the position
        row: Series containing position data
        can_edit: Whether user has edit permissions
        stages: List of active stages for this position
    """
    progress_pct = calculate_position_progress(row, BASE_STAGES)
    # Freeze detection and dropdown (now using a dedicated column if available)
    if 'Freeze' not in st.session_state.hiring_data.columns:
        st.session_state.hiring_data['Freeze'] = False
    
    is_frozen = bool(row.get('Freeze', False)) if 'Freeze' in row.index else False
    
    if can_edit:
        freeze_val = st.selectbox(
            'Freeze',
            options=['No', 'Yes'],
            index=1 if is_frozen else 0,
            key=f'freeze_{idx}'
        )
        new_is_frozen = (freeze_val == 'Yes')
        if new_is_frozen != is_frozen:
            st.session_state.hiring_data.at[idx, 'Freeze'] = new_is_frozen
            st.session_state.hiring_data.at[idx, 'Last Updated'] = get_current_timestamp()
            save_hiring_data(st.session_state.hiring_data)
            st.success(f"✅ Freeze status updated to {'Yes' if new_is_frozen else 'No'}")
            st.rerun()
    
    if is_frozen:
        st.markdown(
            "<div style='color:#0d6efd;font-weight:bold;margin-bottom:8px;'>🧊 This position is currently under <span style='background:#ffd700;padding:2px 8px;border-radius:6px;'>freeze</span></div>",
            unsafe_allow_html=True
        )
    render_progress_badge(progress_pct)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Edit position name
    if can_edit:
        st.markdown("#### ✏️ Edit Position Name")
        new_position_name = st.text_input(
            "Job Position",
            value=row['Job Position'],
            key=f"position_name_{idx}",
            label_visibility="collapsed"
        )
        if new_position_name != row['Job Position'] and new_position_name:
            st.session_state.hiring_data.at[idx, 'Job Position'] = new_position_name
            st.session_state.hiring_data.at[idx, 'Last Updated'] = get_current_timestamp()
            save_hiring_data(st.session_state.hiring_data)
            st.success(f"✅ Position name updated to '{new_position_name}'")
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
    
    # PIC selection (Superadmin only)
    if st.session_state.get("role") == "HR Superadmin":
        hr_roles = get_hr_roles()
        try:
            hr_admins = list(hr_roles.get("admins", {}).keys())
        except (KeyError, AttributeError):
            hr_admins = []
        
        edit_pic = st.selectbox(
            "Assign PIC (HR Admin)",
            options=[""] + hr_admins,
            index=hr_admins.index(row["PIC"]) + 1 if "PIC" in row and row["PIC"] in hr_admins else 0,
            key=f"edit_pic_{idx}"
        )
        if edit_pic != row.get("PIC", ""):
            st.session_state.hiring_data.at[idx, "PIC"] = edit_pic
            st.session_state.hiring_data.at[idx, 'Last Updated'] = get_current_timestamp()
            save_hiring_data(st.session_state.hiring_data)
            st.success(f"✅ PIC updated to {edit_pic or 'Unassigned'}")
            st.rerun()
    
    # Hire type
    if can_edit:
        hire_type = st.selectbox(
            "Hire Type",
            options=["Additional", "Replacement"],
            index=0 if row.get("Hire Type", "Additional") == "Additional" else 1,
            key=f"hire_type_{idx}"
        )
        
        replacement_for = ""
        if hire_type == "Replacement":
            replacement_for = st.text_input(
                "Replacement For",
                value=row.get("Replacement For", ""),
                placeholder="Enter name being replaced",
                key=f"replacement_for_{idx}"
            )

        # Status (Contract / Intern / Freelance) — auto-detected from Planner
        # labels/task name on sync, but editable here.
        status_options = ["Contract", "Intern", "Freelance"]
        current_status = row.get("Status", "Contract") or "Contract"
        if current_status not in status_options:
            status_options = [current_status] + status_options
        new_status = st.selectbox(
            "Status",
            options=status_options,
            index=status_options.index(current_status),
            key=f"status_{idx}",
        )
        if new_status != current_status:
            st.session_state.hiring_data.at[idx, "Status"] = new_status
            st.session_state.hiring_data.at[idx, "Last Updated"] = get_current_timestamp()
            save_hiring_data(st.session_state.hiring_data)
            st.success(f"✅ Status updated to {new_status}")
            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
    else:
        hire_type = row.get("Hire Type", "Additional")
        replacement_for = row.get("Replacement For", "")
    
    # Hiring stages checkboxes
    if can_edit:
        st.markdown("#### 📝 Hiring Stages")
        cols = st.columns(4)
        stage_changed = False
        for i, stage in enumerate(stages):
            # Skip Skill Test if not needed for this position
            if stage == "Skill Test" and not row.get('Has Skill Test', True):
                continue
            with cols[i % 4]:
                new_value = st.checkbox(
                    stage,
                    value=bool(row[stage]),
                    key=f"mgmt_stage_{idx}_{stage}"
                )
                if new_value != bool(row[stage]):
                    st.session_state.hiring_data.at[idx, stage] = new_value
                    stage_changed = True
                    
                    # Cascading checkbox logic: if a stage is checked, auto-check all previous stages
                    if new_value:
                        for j, prev_stage in enumerate(stages):
                            if j < i:
                                # Skip Skill Test if not needed for this position
                                if prev_stage == "Skill Test" and not row.get('Has Skill Test', True):
                                    continue
                                if not bool(row[prev_stage]):
                                    st.session_state.hiring_data.at[idx, prev_stage] = True
        
        if stage_changed:
            st.session_state.hiring_data.at[idx, 'Last Updated'] = get_current_timestamp()
            save_hiring_data(st.session_state.hiring_data)
            st.success("✅ Hiring stages updated!")
            st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
    
    # Job description
    if can_edit:
        st.markdown("#### 📋 Job Description")
        job_desc = st.text_area(
            "Job Description",
            value=row.get("Job Description", ""),
            height=150,
            key=f"job_desc_{idx}",
            help="Enter the full job description",
            label_visibility="collapsed"
        )
        st.markdown("<hr>", unsafe_allow_html=True)
    else:
        job_desc = row.get("Job Description", "")
    
    # File attachments
    if can_edit:
        render_file_attachments(idx, row)
    
    # Skill test toggle (Superadmin only)
    if st.session_state.get("role") == "HR Superadmin":
        use_skill_test = st.checkbox(
            "Include Skill Test for this position",
            value=row.get("Has Skill Test", True),
            key=f"skilltest_toggle_{idx}"
        )
        if use_skill_test != row.get("Has Skill Test", True):
            st.session_state.hiring_data.at[idx, "Has Skill Test"] = use_skill_test
            st.session_state.hiring_data.at[idx, 'Last Updated'] = get_current_timestamp()
            save_hiring_data(st.session_state.hiring_data)
            st.success(f"✅ Updated: {'Skill Test included' if use_skill_test else 'Skill Test skipped'}")
            st.rerun()
        
        # Edit Division
        new_division_name = st.selectbox(
            "Edit Division",
            options=list(st.session_state.credentials.keys()),
            index=list(st.session_state.credentials.keys()).index(row["Division"]) if row["Division"] in st.session_state.credentials else 0,
            key=f"edit_division_{idx}"
        )
        if new_division_name != row["Division"]:
            st.session_state.hiring_data.at[idx, "Division"] = new_division_name
            st.session_state.hiring_data.at[idx, 'Last Updated'] = get_current_timestamp()
            save_hiring_data(st.session_state.hiring_data)
            st.success(f"✅ Division updated to {new_division_name}")
            st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
    
    # Notes
    if can_edit:
        st.markdown("#### 💬 Notes")
        notes_text = st.text_area(
            "Notes",
            value=row.get("Notes", ""),
            height=100,
            key=f"notes_{idx}",
            help="Add notes or comments about this position",
            label_visibility="collapsed",
            placeholder="Add notes here..."
        )
        st.markdown("<hr>", unsafe_allow_html=True)
    else:
        notes_text = row.get("Notes", "")
        # Read-only notes display for non-editors
        if notes_text:
            st.markdown("#### 💬 Notes")
            st.info(notes_text)
    
    if "Last Updated" in row:
        st.caption(f"🕒 Last Updated: {row['Last Updated']}")
    
    # Save/Delete/Duplicate buttons
    btn_col1, btn_col2, btn_col3 = st.columns([3, 1, 1])
    with btn_col1:
        if can_edit and st.button("💾 Save Changes", key=f"save_{idx}", use_container_width=True):
            st.session_state.hiring_data.at[idx, "Hire Type"] = hire_type
            st.session_state.hiring_data.at[idx, "Replacement For"] = replacement_for if hire_type == "Replacement" else ""
            st.session_state.hiring_data.at[idx, "Job Description"] = job_desc
            st.session_state.hiring_data.at[idx, "Notes"] = notes_text
            st.session_state.hiring_data.at[idx, 'Last Updated'] = get_current_timestamp()
            save_hiring_data(st.session_state.hiring_data)
            st.success("✅ Changes saved successfully")
            st.rerun()
    with btn_col2:
        if st.session_state.get("role") == "HR Superadmin":
            if st.button("🗑️ Delete", key=f"delete_{idx}", use_container_width=True):
                st.session_state.hiring_data = st.session_state.hiring_data.drop(idx).reset_index(drop=True)
                save_hiring_data(st.session_state.hiring_data)
                st.success("✅ Position deleted!")
                st.rerun()
    with btn_col3:
        if st.button("📄 Duplicate", key=f"duplicate_{idx}", use_container_width=True):
            duplicate_row = row.copy()
            duplicate_row["Notes"] = ""
            # Keep hiring stages as-is from the original position (don't reset to False)
            st.session_state.hiring_data = pd.concat(
                [st.session_state.hiring_data, pd.DataFrame([duplicate_row])],
                ignore_index=True
            )
            save_hiring_data(st.session_state.hiring_data)
            st.success("✅ Position duplicated!")
            st.rerun()


def render_file_attachments(idx: int, row: pd.Series) -> None:
    """
    Render file attachment section for a position.
    
    Args:
        idx: DataFrame index of the position
        row: Series containing position data
    """
    st.markdown("#### 📎 Attachments")
    uploaded_files = st.file_uploader(
        "Upload supporting documents",
        accept_multiple_files=True,
        key=f"files_{idx}",
        help="Upload PDFs, images, or documents"
    )
    
    if uploaded_files:
        if "Attachments" not in st.session_state.hiring_data.columns:
            st.session_state.hiring_data["Attachments"] = [[] for _ in range(len(st.session_state.hiring_data))]
        
        current_attachments = st.session_state.hiring_data.at[idx, "Attachments"]
        if not isinstance(current_attachments, list):
            current_attachments = []
        
        for file in uploaded_files:
            file_contents = file.read()
            file_data = {
                "name": file.name,
                "content": base64.b64encode(file_contents).decode(),
                "type": file.type
            }
            current_attachments.append(file_data)
        
        st.session_state.hiring_data.at[idx, "Attachments"] = current_attachments
        st.session_state.hiring_data.at[idx, 'Last Updated'] = get_current_timestamp()
        save_hiring_data(st.session_state.hiring_data)
        st.success("✅ Files uploaded!")
        st.rerun()
    
    # Display existing attachments
    existing_attachments = row.get("Attachments", [])
    if existing_attachments and isinstance(existing_attachments, list) and len(existing_attachments) > 0:
        st.markdown("**Existing Attachments:**")
        for file_idx, file in enumerate(existing_attachments):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"📄 {file['name']}")
            with col2:
                st.download_button(
                    "Download",
                    data=base64.b64decode(file["content"]),
                    file_name=file["name"],
                    mime=file.get("type", "application/octet-stream"),
                    key=f"download_{idx}_{file_idx}"
                )
            with col3:
                if st.button("🗑️", key=f"del_file_{idx}_{file_idx}"):
                    existing_attachments.pop(file_idx)
                    st.session_state.hiring_data.at[idx, "Attachments"] = existing_attachments
                    st.session_state.hiring_data.at[idx, 'Last Updated'] = get_current_timestamp()
                    save_hiring_data(st.session_state.hiring_data)
                    st.success("✅ File deleted!")
                    st.rerun()
    
    st.markdown("<hr>", unsafe_allow_html=True)
