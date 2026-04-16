"""
Candidate card component for displaying escalated candidates.
Shows candidate info, AI analysis, score badge, and comment section.
"""

import streamlit as st
from typing import List
from models.candidate import Candidate


def _score_color(score: int) -> str:
    if score >= 85:
        return "#16a34a"  # green
    elif score >= 70:
        return "#2563eb"  # blue
    elif score >= 55:
        return "#d97706"  # amber
    elif score >= 30:
        return "#ea580c"  # orange
    else:
        return "#dc2626"  # red


def _score_label(score: int) -> str:
    if score >= 85:
        return "Very Strong"
    elif score >= 70:
        return "Strong"
    elif score >= 55:
        return "Moderate"
    elif score >= 30:
        return "Weak"
    else:
        return "Not a Fit"


def _status_badge(status: str) -> str:
    colors = {
        "Escalated": "#2563eb",
        "Interview": "#d97706",
        "Approved": "#16a34a",
        "Rejected": "#dc2626",
        "Pending": "#64748b",
    }
    color = colors.get(status, "#64748b")
    return f'<span style="background:{color};color:white;padding:2px 10px;border-radius:12px;font-size:0.8rem;font-weight:600;">{status}</span>'


def render_candidate_card(candidate: Candidate, key_prefix: str,
                          show_actions: bool = False,
                          on_comment=None, on_approve=None, on_reject=None) -> None:
    """
    Render a single candidate card with AI analysis and optional action buttons.

    Args:
        candidate: Candidate object
        key_prefix: Unique key prefix for Streamlit widgets
        show_actions: Whether to show comment/approve/reject actions
        on_comment: Callback(candidate_id, text) for comment submission
        on_approve: Callback(candidate_id, text) for approval
        on_reject: Callback(candidate_id, text) for rejection
    """
    score = candidate.match_score
    color = _score_color(score)
    label = _score_label(score)

    with st.expander(
        f"**{candidate.name}** — Score: {score} ({label}) {_status_badge(candidate.status)}",
        expanded=False
    ):
        # Score badge
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">'
            f'<div style="background:{color};color:white;padding:8px 16px;border-radius:12px;'
            f'font-size:1.5rem;font-weight:700;min-width:60px;text-align:center;">{score}</div>'
            f'<div><strong>{label} Fit</strong><br>'
            f'<span style="color:#64748b;font-size:0.85rem;">{candidate.latest_job_title} at {candidate.latest_company}</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Contact info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"📧 **Email:** {candidate.email or 'N/A'}")
        with col2:
            st.markdown(f"📱 **Phone:** {candidate.phone or 'N/A'}")
        with col3:
            st.markdown(f"🎓 **{candidate.education}** — {candidate.university}")

        # Links
        links = []
        if candidate.resume_link:
            links.append(f"[📄 Resume]({candidate.resume_link})")
        if candidate.kalibrr_link:
            links.append(f"[👤 Kalibrr Profile]({candidate.kalibrr_link})")
        if candidate.application_link:
            links.append(f"[📋 Application]({candidate.application_link})")
        if links:
            st.markdown(" • ".join(links))

        st.markdown("---")

        # AI Summary
        st.markdown("#### 🤖 AI Analysis")
        st.info(candidate.ai_summary)

        col_s, col_w, col_g = st.columns(3)
        with col_s:
            st.markdown("**✅ Strengths**")
            for s in candidate.strengths:
                st.markdown(f"- {s}")
        with col_w:
            st.markdown("**⚠️ Weaknesses**")
            for w in candidate.weaknesses:
                st.markdown(f"- {w}")
        with col_g:
            st.markdown("**❌ Gaps**")
            for g in candidate.gaps:
                st.markdown(f"- {g}")

        # Comments history
        if candidate.comments:
            st.markdown("---")
            st.markdown("#### 💬 Comments")
            for c in candidate.comments:
                action_icon = {"comment": "💬", "approve": "✅", "reject": "❌"}.get(c.action, "💬")
                st.markdown(
                    f"**{action_icon} {c.author}** ({c.division}) — {c.timestamp}\n\n{c.text}"
                )

        # Action buttons
        if show_actions and candidate.status not in [Candidate.STATUS_APPROVED, Candidate.STATUS_REJECTED]:
            st.markdown("---")
            st.markdown("#### ✍️ Add Feedback")
            comment_text = st.text_area(
                "Your feedback on this candidate",
                key=f"{key_prefix}_comment_text",
                placeholder="What do you think about this candidate? Strengths, concerns, fit for the role...",
                height=100
            )

            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                if st.button("💬 Comment", key=f"{key_prefix}_btn_comment", use_container_width=True):
                    if comment_text and on_comment:
                        on_comment(candidate.id, comment_text)
            with btn_col2:
                if st.button("✅ Approve", key=f"{key_prefix}_btn_approve", use_container_width=True, type="primary"):
                    if on_approve:
                        on_approve(candidate.id, comment_text or "Approved by user")
            with btn_col3:
                if st.button("❌ Reject", key=f"{key_prefix}_btn_reject", use_container_width=True):
                    if comment_text and on_reject:
                        on_reject(candidate.id, comment_text)
                    elif on_reject:
                        st.warning("Please provide a reason for rejection")

        # Metadata
        st.caption(f"Escalated by {candidate.escalated_by} on {candidate.escalated_at}")
        if candidate.date_applied:
            st.caption(f"Applied: {candidate.date_applied}")
