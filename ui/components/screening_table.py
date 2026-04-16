"""
Screening results table component.
Displays CV Matching screening results with sortable columns and escalation buttons.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Callable


def _score_badge_html(score) -> str:
    try:
        score = int(score)
    except (ValueError, TypeError):
        score = 0

    if score >= 85:
        bg, label = "#16a34a", "Very Strong"
    elif score >= 70:
        bg, label = "#2563eb", "Strong"
    elif score >= 55:
        bg, label = "#d97706", "Moderate"
    elif score >= 30:
        bg, label = "#ea580c", "Weak"
    else:
        bg, label = "#dc2626", "Not a Fit"

    return (
        f'<span style="background:{bg};color:white;padding:2px 8px;border-radius:8px;'
        f'font-weight:600;font-size:0.85rem;">{score} — {label}</span>'
    )


def render_screening_table(results_df: pd.DataFrame, position_key: str,
                           division: str, escalated_emails: set,
                           on_escalate: Optional[Callable] = None,
                           key_prefix: str = "screen") -> None:
    """
    Render screening results table with score highlighting and escalation buttons.

    Args:
        results_df: DataFrame from CV Matching (columns: Candidate Name, Match Score, etc.)
        position_key: Position identifier for escalation
        division: Division this position belongs to
        escalated_emails: Set of already-escalated candidate emails
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

    # Summary stats
    if "Match Score" in filtered.columns and len(filtered) > 0:
        avg_score = filtered["Match Score"].mean()
        top_score = filtered["Match Score"].max()
        st.markdown(
            f"**{len(filtered)}** candidates | Avg Score: **{avg_score:.0f}** | Top Score: **{top_score}**"
        )

    st.markdown("---")

    # Render each candidate row
    for idx, row in filtered.iterrows():
        name = str(row.get("Candidate Name", "Unknown"))
        email = str(row.get("Candidate Email", "")).strip()
        score = int(row.get("Match Score", 0))
        summary = str(row.get("AI Summary", ""))
        already_escalated = email.lower() in {e.lower() for e in escalated_emails} if email else False

        with st.expander(
            f"{'✅ ' if already_escalated else ''}{name} — {_score_badge_html(score)}",
            expanded=False
        ):
            st.markdown(_score_badge_html(score), unsafe_allow_html=True)
            st.markdown(f"**{name}** | {email}")
            st.markdown(f"📋 {row.get('Latest Job Title', '')} at {row.get('Latest Company', '')}")
            st.markdown(f"🎓 {row.get('Education', '')} — {row.get('University', '')} ({row.get('Major', '')})")

            if summary:
                st.info(summary)

            # Strengths / Weaknesses / Gaps
            col_s, col_w, col_g = st.columns(3)
            with col_s:
                st.markdown("**Strengths**")
                for s in str(row.get("Strengths", "")).split(";"):
                    if s.strip():
                        st.markdown(f"- {s.strip()}")
            with col_w:
                st.markdown("**Weaknesses**")
                for w in str(row.get("Weaknesses", "")).split(";"):
                    if w.strip():
                        st.markdown(f"- {w.strip()}")
            with col_g:
                st.markdown("**Gaps**")
                for g in str(row.get("Gaps", "")).split(";"):
                    if g.strip():
                        st.markdown(f"- {g.strip()}")

            # Links
            links = []
            if row.get("Resume Link"):
                links.append(f"[📄 Resume]({row['Resume Link']})")
            if row.get("Kalibrr Profile"):
                links.append(f"[👤 Profile]({row['Kalibrr Profile']})")
            if row.get("Application Link"):
                links.append(f"[📋 Application]({row['Application Link']})")
            if links:
                st.markdown(" • ".join(links))

            # Escalation button
            if on_escalate and not already_escalated:
                if st.button(f"🚀 Escalate to User Interview", key=f"{key_prefix}_escalate_{idx}",
                             use_container_width=True, type="primary"):
                    on_escalate(row.to_dict())
            elif already_escalated:
                st.success("✅ Already escalated to user interview")
