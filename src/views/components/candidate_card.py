"""
Candidate card component for displaying escalated candidates.
Shows candidate info, AI analysis, score badge, and comment section.
Modern minimal card design.
"""

import streamlit as st
from src.models.candidate import Candidate


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


def _status_color(status: str) -> str:
    return {
        "Escalated": "#2563eb",
        "Interview": "#d97706",
        "Approved": "#16a34a",
        "Rejected": "#dc2626",
        "Pending": "#64748b",
        "Rekomendasi": "#16a34a",
        "Tidak Direkomendasi": "#dc2626",
        "Cadangan": "#d97706",
    }.get(status, "#64748b")


def _status_bg(status: str) -> str:
    return {
        "Escalated": "#eff6ff",
        "Interview": "#fffbeb",
        "Approved": "#f0fdf4",
        "Rejected": "#fef2f2",
        "Pending": "#f8fafc",
        "Rekomendasi": "#f0fdf4",
        "Tidak Direkomendasi": "#fef2f2",
        "Cadangan": "#fffbeb",
    }.get(status, "#f8fafc")


def render_candidate_card(candidate: Candidate, key_prefix: str,
                          show_actions: bool = False,
                          on_comment=None, on_approve=None, on_reject=None,
                          on_reset=None, on_clear_comments=None,
                          on_skill_review=None,
                          reviewer_division: str = "",
                          division_view: bool = False) -> None:
    score = candidate.match_score
    color = _score_color(score)
    label = _score_label(score)
    status_color = _status_color(candidate.status)
    status_bg = _status_bg(candidate.status)

    # Card header with name, score badge, and status pill
    st.markdown(
        f'''<div class="candidate-header">
            <span class="candidate-name">{candidate.name}</span>
            <span class="candidate-score" style="background:{color};">{score} · {label}</span>
            <span class="candidate-status-badge" style="background:{status_bg};color:{status_color};">{candidate.status}</span>
        </div>''',
        unsafe_allow_html=True
    )

    with st.expander("View Details", expanded=False):
        # Contact & job info
        info_parts = []
        if candidate.latest_job_title:
            info_parts.append(f"<span class='candidate-info-item'><strong>Role:</strong> {candidate.latest_job_title}</span>")
        if candidate.latest_company:
            info_parts.append(f"<span class='candidate-info-item'><strong>Company:</strong> {candidate.latest_company}</span>")
        if candidate.email:
            info_parts.append(f"<span class='candidate-info-item'><strong>Email:</strong> {candidate.email}</span>")
        if candidate.phone:
            info_parts.append(f"<span class='candidate-info-item'><strong>Phone:</strong> {candidate.phone}</span>")
        if info_parts:
            st.markdown(f"<div class='candidate-info-row'>{''.join(info_parts)}</div>", unsafe_allow_html=True)

        edu_parts = []
        if candidate.education:
            edu_parts.append(f"<span class='candidate-info-item'><strong>Education:</strong> {candidate.education}</span>")
        if candidate.university:
            edu_parts.append(f"<span class='candidate-info-item'><strong>University:</strong> {candidate.university}</span>")
        if edu_parts:
            st.markdown(f"<div class='candidate-info-row'>{''.join(edu_parts)}</div>", unsafe_allow_html=True)

        # Links as pills (Division view: only Resume)
        links = []
        if candidate.resume_link:
            links.append(f"<a href='{candidate.resume_link}' target='_blank' class='candidate-link-pill'>Resume</a>")
        if not division_view:
            if candidate.kalibrr_link:
                links.append(f"<a href='{candidate.kalibrr_link}' target='_blank' class='candidate-link-pill'>Kalibrr Profile</a>")
            if candidate.application_link:
                links.append(f"<a href='{candidate.application_link}' target='_blank' class='candidate-link-pill'>Application</a>")
        if links:
            st.markdown(f"<div style='display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.75rem;'>{''.join(links)}</div>", unsafe_allow_html=True)

        # AI Analysis section (hidden in division view — only resume is shown)
        if candidate.ai_summary and not division_view:
            st.markdown(
                f"<div class='ai-analysis-card'><h5>AI Summary</h5><p style='font-size:0.85rem;color:#1e293b;margin:0;line-height:1.6;'>{candidate.ai_summary}</p></div>",
                unsafe_allow_html=True
            )

        # Strengths / Weaknesses / Gaps in cards (hidden in division view)
        if not division_view:
            col_s, col_w, col_g = st.columns(3)
            with col_s:
                if candidate.strengths:
                    items = "".join(f"<li>{s}</li>" for s in candidate.strengths)
                    st.markdown(
                        f"<div class='ai-analysis-card'><h5>Strengths</h5><ul>{items}</ul></div>",
                        unsafe_allow_html=True
                    )
            with col_w:
                if candidate.weaknesses:
                    items = "".join(f"<li>{w}</li>" for w in candidate.weaknesses)
                    st.markdown(
                        f"<div class='ai-analysis-card'><h5>Weaknesses</h5><ul>{items}</ul></div>",
                        unsafe_allow_html=True
                    )
            with col_g:
                if candidate.gaps:
                    items = "".join(f"<li>{g}</li>" for g in candidate.gaps)
                    st.markdown(
                        f"<div class='ai-analysis-card'><h5>Gaps</h5><ul>{items}</ul></div>",
                        unsafe_allow_html=True
                    )

        # Division skill reviews (visible to HR / Superadmin)
        if candidate.skill_ratings and not division_view:
            st.markdown("---")
            st.markdown(
                f"<p style='font-size:0.9rem;font-weight:600;color:#0f172a;margin:0 0 0.5rem 0;'>Skill Reviews ({len(candidate.skill_ratings)})</p>",
                unsafe_allow_html=True,
            )
            for div_name, entry in candidate.skill_ratings.items():
                dec = entry.get("decision", "")
                dec_color = _status_color(dec)
                dec_bg = _status_bg(dec)
                note_html = (
                    f"<div style='font-size:0.82rem;color:#334155;margin-top:0.4rem;'>"
                    f"<strong>Catatan:</strong> {entry.get('note','')}</div>"
                ) if entry.get("note") else ""
                st.markdown(
                    f"""<div class='comment-card'>
                        <div class='comment-header'>
                            <span><span class='comment-author'>{div_name}</span>
                            <span class='comment-action-badge' style='background:{dec_bg};color:{dec_color};'>{dec}</span></span>
                            <span class='comment-time'>{entry.get('submitted_at','')}</span>
                        </div>
                        <div class='comment-text'>
                            Soft Skill: <strong>{entry.get('soft_skill','-')}/4</strong> ·
                            Value KG: <strong>{entry.get('value_kg','-')}/4</strong> ·
                            Technical Skill: <strong>{entry.get('technical_skill','-')}/4</strong>
                        </div>
                        {note_html}
                    </div>""",
                    unsafe_allow_html=True,
                )

        # Comments section
        if candidate.comments:
            st.markdown("---")
            col_title, col_clear = st.columns([4, 1])
            with col_title:
                st.markdown(f"<p style='font-size:0.9rem;font-weight:600;color:#0f172a;margin:0;'>Comments ({len(candidate.comments)})</p>", unsafe_allow_html=True)
            with col_clear:
                if on_clear_comments and st.button(
                    "Clear", key=f"{key_prefix}_btn_clear_comments",
                    use_container_width=True
                ):
                    on_clear_comments(candidate.id)

            for c in candidate.comments:
                action_badge = ""
                if c.action == "approve":
                    action_badge = "<span class='comment-action-badge approved'>Approved</span>"
                elif c.action == "reject":
                    action_badge = "<span class='comment-action-badge rejected'>Rejected</span>"

                if c.author == c.division:
                    author_display = c.division
                else:
                    author_display = f"{c.author} ({c.division})"

                st.markdown(
                    f"""<div class="comment-card">
                        <div class="comment-header">
                            <span><span class="comment-author">{author_display}</span>{action_badge}</span>
                            <span class="comment-time">{c.timestamp}</span>
                        </div>
                        <div class="comment-text">{c.text}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

        # Action buttons
        actioned = candidate.status in Candidate.ACTIONED_STATUSES

        if show_actions and division_view and on_skill_review:
            # Division reviewer flow: 3 ratings (1-4) + note + 3 decision buttons
            st.markdown("---")

            # Show this division's previous review (if any) so the reviewer
            # sees what was last submitted before re-rating.
            existing = candidate.skill_ratings.get(reviewer_division) if reviewer_division else None

            default_soft = int(existing.get("soft_skill", 1)) if existing else 1
            default_value = int(existing.get("value_kg", 1)) if existing else 1
            default_tech = int(existing.get("technical_skill", 1)) if existing else 1
            default_note = existing.get("note", "") if existing else ""

            st.markdown(
                "<p style='font-size:0.9rem;font-weight:600;color:#0f172a;margin:0 0 0.25rem 0;'>Penilaian (skala 1–4)</p>",
                unsafe_allow_html=True,
            )

            r1, r2, r3 = st.columns(3)
            with r1:
                soft_skill = st.slider(
                    "Soft Skill", min_value=1, max_value=4, step=1,
                    value=default_soft, key=f"{key_prefix}_rate_soft",
                )
            with r2:
                value_kg = st.slider(
                    "Value KG", min_value=1, max_value=4, step=1,
                    value=default_value, key=f"{key_prefix}_rate_value",
                )
            with r3:
                technical_skill = st.slider(
                    "Technical Skill", min_value=1, max_value=4, step=1,
                    value=default_tech, key=f"{key_prefix}_rate_tech",
                )

            note_text = st.text_area(
                "Catatan",
                value=default_note,
                key=f"{key_prefix}_rate_note",
                placeholder="Tambahkan catatan untuk kandidat ini...",
                height=80,
            )

            ratings = {
                "soft_skill": soft_skill,
                "value_kg": value_kg,
                "technical_skill": technical_skill,
            }

            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("Rekomendasi", key=f"{key_prefix}_btn_rec",
                             use_container_width=True, type="primary"):
                    on_skill_review(candidate.id, ratings, note_text,
                                    Candidate.STATUS_RECOMMENDED)
            with b2:
                if st.button("Tidak Direkomendasi", key=f"{key_prefix}_btn_notrec",
                             use_container_width=True):
                    on_skill_review(candidate.id, ratings, note_text,
                                    Candidate.STATUS_NOT_RECOMMENDED)
            with b3:
                if st.button("Cadangan", key=f"{key_prefix}_btn_reserve",
                             use_container_width=True):
                    on_skill_review(candidate.id, ratings, note_text,
                                    Candidate.STATUS_RESERVE)

        elif show_actions and not division_view and not actioned:
            # Legacy HR flow (kept for backwards compatibility)
            st.markdown("---")
            comment_text = st.text_area(
                "Your feedback on this candidate",
                key=f"{key_prefix}_comment_text",
                placeholder="Add your comments here (optional for approve, required for reject)...",
                height=80
            )

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Approve", key=f"{key_prefix}_btn_approve", use_container_width=True, type="primary"):
                    if on_approve:
                        on_approve(candidate.id, comment_text or "Approved")
            with btn_col2:
                if st.button("Reject", key=f"{key_prefix}_btn_reject", use_container_width=True):
                    if comment_text and on_reject:
                        on_reject(candidate.id, comment_text)
                    elif on_reject:
                        st.warning("Please provide a reason for rejection")

        # Reset button for already-actioned candidates
        if show_actions and on_reset and actioned:
            st.markdown("---")
            if st.button(f"Reset Status (currently {candidate.status})",
                         key=f"{key_prefix}_btn_reset", use_container_width=True):
                on_reset(candidate.id)

        # Metadata footer
        st.caption(f"Escalated by {candidate.escalated_by} on {candidate.escalated_at}")
        if candidate.date_applied:
            st.caption(f"Applied: {candidate.date_applied}")
