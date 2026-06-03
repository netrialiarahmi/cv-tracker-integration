"""
Screening results table component.
Displays CV Matching screening results with sortable columns and escalation buttons.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Callable


def _clean(val) -> str:
    """Return empty string for nan/None/empty values."""
    if val is None:
        return ""
    s = str(val).strip()
    if s.lower() in ("nan", "none", ""):
        return ""
    return s


def _score_color(score: int) -> str:
    if score >= 85:
        return "#16a34a"
    elif score >= 70:
        return "#2563eb"
    elif score >= 55:
        return "#d97706"
    elif score >= 30:
        return "#ea580c"
    else:
        return "#dc2626"


def _score_badge_html(score: int) -> str:
    color = _score_color(score)
    return (
        f'<div style="background:{color};color:white;padding:8px 16px;border-radius:12px;'
        f'font-size:1.3rem;font-weight:700;display:inline-block;">'
        f'Score: {score}</div>'
    )


def render_screening_table(results_df: pd.DataFrame, position_key: str,
                           division: str, escalated_identifiers: set,
                           on_escalate: Optional[Callable] = None,
                           on_reset_escalation: Optional[Callable] = None,
                           key_prefix: str = "screen") -> None:
    """
    Render screening results table with score highlighting and escalation buttons.

    Args:
        results_df: DataFrame from CV Matching (columns: Candidate Name, Match Score, etc.)
        position_key: Position identifier for escalation
        division: Division this position belongs to
        escalated_identifiers: Set of already-escalated candidate emails or names
        on_escalate: Callback(row_dict) when escalate button is clicked
        key_prefix: Unique prefix for widget keys
    """
    if results_df is None or results_df.empty:
        st.info("No screening results available for this position.")
        return

    # Sort controls
    col_sort, col_filter, col_search = st.columns([2, 2, 3])
    with col_sort:
        sort_by = st.selectbox("Sort by", ["Score ↓", "Score ↑", "Name A-Z", "Date ↓"],
                               key=f"{key_prefix}_sort")
    with col_filter:
        min_score = st.slider("Min Score", 0, 100, 0, key=f"{key_prefix}_min_score")
    with col_search:
        search = st.text_input("Search", placeholder="Search by name or email...",
                               key=f"{key_prefix}_search")

    # Apply filters
    filtered = results_df.copy()

    if "Match Score" in filtered.columns:
        filtered["Match Score"] = pd.to_numeric(filtered["Match Score"], errors="coerce").fillna(0).astype(int)
        filtered = filtered[filtered["Match Score"] >= min_score]

    if search:
        mask = pd.Series(False, index=filtered.index)
        for col in ["Candidate Name", "Candidate Email"]:
            if col in filtered.columns:
                mask |= filtered[col].astype(str).str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    # Apply sorting
    if "Match Score" in filtered.columns:
        if sort_by == "Score ↓":
            filtered = filtered.sort_values("Match Score", ascending=False)
        elif sort_by == "Score ↑":
            filtered = filtered.sort_values("Match Score", ascending=True)
    if sort_by == "Name A-Z" and "Candidate Name" in filtered.columns:
        filtered = filtered.sort_values("Candidate Name", ascending=True)
    if sort_by == "Date ↓" and "Date Applied" in filtered.columns:
        filtered = filtered.sort_values("Date Applied", ascending=False)

    # Summary
    st.markdown(f"**Showing {len(filtered)} candidate(s)**")

    # Render each candidate row (CV Matching style)
    for idx, row in filtered.iterrows():
        name = _clean(row.get("Candidate Name")) or "Unknown"
        email = _clean(row.get("Candidate Email"))
        phone = _clean(row.get("Phone"))
        score = int(row.get("Match Score", 0))
        summary = _clean(row.get("AI Summary"))
        job_title = _clean(row.get("Latest Job Title"))
        company = _clean(row.get("Latest Company"))
        education = _clean(row.get("Education"))
        university = _clean(row.get("University"))
        major = _clean(row.get("Major"))
        already_escalated = False
        if email:
            already_escalated = email.lower() in escalated_identifiers
        elif name and name != "Unknown":
            already_escalated = name.lower() in escalated_identifiers

        # Header line outside expander
        escalated_tag = " [Escalated]" if already_escalated else ""
        st.markdown(f"{name} - Score: {score}{escalated_tag}")

        with st.expander("View Details", expanded=False):
            # Score badge + contact info (like CV Matching layout)
            col_badge, col_info = st.columns([1, 4])
            with col_badge:
                st.markdown(_score_badge_html(score), unsafe_allow_html=True)
            with col_info:
                # Contact line
                contact_parts = []
                if email:
                    contact_parts.append(f"**Email:** {email}")
                if phone:
                    contact_parts.append(f"**Phone:** {phone}")
                if contact_parts:
                    st.markdown(" · ".join(contact_parts))

                # Job info
                job_parts = []
                if job_title:
                    job_parts.append(f"**Job:** {job_title}")
                if company:
                    job_parts.append(f"**Company:** {company}")
                if job_parts:
                    st.markdown(" · ".join(job_parts))

                # Education
                edu_parts = []
                if education:
                    edu_parts.append(f"**Education:** {education}")
                if university:
                    uni_str = university
                    if major:
                        uni_str += f" ({major})"
                    edu_parts.append(f"**University:** {uni_str}")
                if edu_parts:
                    st.markdown(" · ".join(edu_parts))

            # AI Summary
            if summary:
                st.markdown("---")
                st.info(summary)

            # Strengths / Weaknesses / Gaps
            strengths = [s.strip() for s in _clean(row.get("Strengths")).split(";") if s.strip()]
            weaknesses = [w.strip() for w in _clean(row.get("Weaknesses")).split(";") if w.strip()]
            gaps = [g.strip() for g in _clean(row.get("Gaps")).split(";") if g.strip()]

            if strengths or weaknesses or gaps:
                st.markdown("---")
                col_s, col_w, col_g = st.columns(3)
                with col_s:
                    st.markdown("**Strengths**")
                    for s in strengths:
                        st.markdown(f"- {s}")
                with col_w:
                    st.markdown("**Weaknesses**")
                    for w in weaknesses:
                        st.markdown(f"- {w}")
                with col_g:
                    st.markdown("**Gaps**")
                    for g in gaps:
                        st.markdown(f"- {g}")

            # Links as styled buttons
            from src.utils.resume_helpers import get_resume_display_info
            resume = _clean(row.get("Resume Link"))
            profile = _clean(row.get("Kalibrr Profile"))
            application = _clean(row.get("Application Link"))
            resume_url, resume_label, resume_expired = get_resume_display_info(
                resume, application, profile
            )

            link_buttons = []
            btn_style = (
                'display:inline-block;padding:6px 16px;border-radius:8px;'
                'font-size:0.85rem;font-weight:600;text-decoration:none;'
                'margin-right:8px;margin-bottom:4px;'
            )
            if resume_url:
                if resume_expired:
                    color = 'background:#fef3c7;color:#92400e;border:1px solid #f59e0b;'
                    label = f"⚠️ {resume_label}"
                else:
                    color = 'background:#dbeafe;color:#1e40af;border:1px solid #3b82f6;'
                    label = f"📄 {resume_label}"
                link_buttons.append(
                    f'<a href="{resume_url}" target="_blank" style="{btn_style}{color}">{label}</a>'
                )
            elif resume_expired:
                link_buttons.append(
                    f'<span style="{btn_style}background:#fee2e2;color:#991b1b;border:1px solid #ef4444;">'
                    f'⚠️ Resume (expired)</span>'
                )
            if profile:
                link_buttons.append(
                    f'<a href="{profile}" target="_blank" style="{btn_style}'
                    f'background:#e0e7ff;color:#3730a3;border:1px solid #6366f1;">👤 Profile</a>'
                )
            if application:
                link_buttons.append(
                    f'<a href="{application}" target="_blank" style="{btn_style}'
                    f'background:#d1fae5;color:#065f46;border:1px solid #10b981;">📋 Application</a>'
                )
            if link_buttons:
                st.markdown("".join(link_buttons), unsafe_allow_html=True)

            # Escalation button
            if on_escalate and not already_escalated:
                if st.button("Escalate to User Interview", key=f"{key_prefix}_escalate_{idx}",
                             use_container_width=True, type="primary"):
                    on_escalate(row.to_dict())
            elif already_escalated:
                col_status, col_reset = st.columns([3, 1])
                with col_status:
                    st.success("Already escalated to user interview")
                with col_reset:
                    if on_reset_escalation and st.button(
                        "Reset Escalation", key=f"{key_prefix}_reset_esc_{idx}",
                        use_container_width=True
                    ):
                        on_reset_escalation(email or name)
