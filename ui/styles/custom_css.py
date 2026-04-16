"""
Custom CSS styles for the Hiring Tracker application.
Provides consistent styling across all pages and components.
"""

import streamlit as st


def inject_custom_css() -> None:
    """
    Inject custom CSS styles into the Streamlit application.
    """
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

:root {
    --brand-navy: #0f172a;
    --brand-navy-soft: #1d2b44;
    --brand-primary: #2563eb;
    --brand-primary-dark: #1e3a8a;
    --brand-accent: #22d3ee;
    --brand-background: #f5f7fb;
    --card-background: rgba(255, 255, 255, 0.95);
    --card-border: rgba(15, 23, 42, 0.08);
    --text-muted: #64748b;
    --text-dark: #1e293b;
}

* {
    font-family: 'DM Sans', 'Inter', sans-serif;
}

body {
    background: radial-gradient(circle at top, rgba(34, 211, 238, 0.15), transparent 45%),
                radial-gradient(circle at 20% 20%, rgba(37, 99, 235, 0.12), transparent 30%),
                linear-gradient(180deg, #eff4ff 0%, #f8fafc 60%, #edf2fb 100%);
    color: var(--text-dark);
}

/* --- GLOBAL --- */
#MainMenu, footer { visibility: hidden; }
.main { background-color: transparent; }
.block-container {
    padding: 2rem 4rem;
    max-width: 1600px;
    background: transparent;
}

/* --- HEADER / MASTHEAD --- */
.masthead-card {
    background: var(--card-background);
    padding: 1.5rem 2rem;
    border-radius: 16px;
    border: 1px solid var(--card-border);
    box-shadow: 0 12px 45px rgba(15,23,42,0.08);
    position: relative;
    overflow: hidden;
}
.masthead-card::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg, rgba(37, 99, 235, 0.12), transparent 55%);
    pointer-events: none;
}
.masthead-card > * {
    position: relative;
    z-index: 1;
}
.masthead-logout-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
}
.masthead,
.main-header {
    background: var(--card-background);
    padding: 1.5rem 2rem;
    border-radius: 16px;
    border: 1px solid var(--card-border);
    margin-bottom: 2rem;
    box-shadow: 0 12px 45px rgba(15,23,42,0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1.5rem;
    position: relative;
    overflow: hidden;
}
.masthead::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg, rgba(37, 99, 235, 0.12), transparent 55%);
    pointer-events: none;
}
.masthead > * {
    position: relative;
    z-index: 1;
}
.masthead-brand {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}
.masthead-logo {
    width: 110px;
    height: auto;
}
.masthead-copy h1,
.main-header h1 {
    margin: 0;
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--text-dark);
}
.masthead-subtitle {
    margin: 0.25rem 0 0;
    font-size: 1rem;
    color: var(--text-muted);
}
.masthead-kicker {
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.3rem;
    color: var(--brand-primary);
    font-weight: 600;
}
.masthead-meta {
    margin-top: 0.35rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    font-size: 0.9rem;
    color: var(--text-muted);
}
.masthead-meta strong {
    color: var(--brand-navy);
}
.masthead-role {
    color: var(--brand-primary);
    font-weight: 600;
}
.masthead-actions {
    min-width: 160px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.5rem;
}
.masthead-back-slot .stButton>button {
    background-color: transparent !important;
    border: 1px solid rgba(15, 23, 42, 0.2) !important;
    color: var(--text-dark) !important;
    font-weight: 500 !important;
    padding: 0.3rem 0.85rem !important;
    border-radius: 999px !important;
    font-size: 0.78rem !important;
}
.masthead-back-slot .stButton>button:hover:not(:disabled) {
    border-color: var(--brand-primary) !important;
    color: var(--brand-primary) !important;
}

/* --- CONTENT CARDS --- */
.content-card {
    background: var(--card-background);
    padding: 1.75rem;
    border-radius: 16px;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
    margin-bottom: 1.5rem;
    border: 1px solid var(--card-border);
    backdrop-filter: blur(10px);
}
.content-card h3 {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-dark);
    margin-bottom: 1rem;
}

/* --- METRICS --- */
div[data-testid="stMetricValue"] {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--brand-primary);
}
div[data-testid="stMetricLabel"] {
    font-size: 0.85rem;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 0.4px;
}
.metric-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    width: 100%;
}
.metric-card {
    background: linear-gradient(135deg, rgba(37,99,235,0.08), rgba(37,99,235,0.02));
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 16px;
    padding: 1.2rem;
    aspect-ratio: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}
.metric-card-label {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.08rem;
    color: var(--text-muted);
    margin-bottom: 0.45rem;
}
.metric-card-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--brand-primary);
}
/* Interactive metric card buttons */
/* Default state (secondary) - Blue */
div[data-testid="column"] .stButton>button[kind="secondary"] {
    background: linear-gradient(135deg, rgba(37,99,235,0.12), rgba(37,99,235,0.05)) !important;
    border: 2px solid rgba(37,99,235,0.3) !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    min-height: 150px !important;
    color: #2563eb !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    text-align: center !important;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.15) !important;
    white-space: pre-wrap !important;
    line-height: 1.4 !important;
}
/* Active state (primary) - Red */
div[data-testid="column"] .stButton>button[kind="primary"] {
    background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.08)) !important;
    border: 2px solid #ef4444 !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    min-height: 150px !important;
    color: #dc2626 !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    text-align: center !important;
    box-shadow: 0 8px 20px rgba(239, 68, 68, 0.25) !important;
    white-space: pre-wrap !important;
    line-height: 1.4 !important;
}
div[data-testid="column"] .stButton>button[kind="secondary"]:hover:not(:disabled) {
    border-color: #2563eb !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 25px rgba(37, 99, 235, 0.2) !important;
}
div[data-testid="column"] .stButton>button[kind="primary"]:hover:not(:disabled) {
    border-color: #dc2626 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 25px rgba(239, 68, 68, 0.3) !important;
}
div[data-testid="column"] .stButton>button:disabled {
    opacity: 0.6 !important;
    cursor: not-allowed !important;
}
/* Pagination buttons styling */
button[data-testid*="baseButton-secondary"][aria-label="Previous"],
button[data-testid*="baseButton-secondary"][aria-label="Next"] {
    background: linear-gradient(135deg, rgba(37,99,235,0.12), rgba(37,99,235,0.05)) !important;
    border: 2px solid rgba(37,99,235,0.3) !important;
    color: #2563eb !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}
button[data-testid*="baseButton-secondary"][aria-label="Previous"]:hover:not(:disabled),
button[data-testid*="baseButton-secondary"][aria-label="Next"]:hover:not(:disabled) {
    border-color: #2563eb !important;
    background: linear-gradient(135deg, rgba(37,99,235,0.18), rgba(37,99,235,0.08)) !important;
}
.metric-groups {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
}
.metric-group {
    border: 1px solid rgba(37, 99, 235, 0.15);
    border-radius: 14px;
    padding: 1rem;
    background: rgba(255,255,255,0.9);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
}
.metric-group h4 {
    margin: 0 0 0.35rem;
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.08rem;
    color: var(--text-muted);
}
.metric-stack {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
}
.metric-pill {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 0.55rem 0.75rem;
    border-radius: 12px;
    background: rgba(226, 232, 240, 0.6);
    font-size: 0.85rem;
    color: var(--text-dark);
}
.metric-pill strong {
    font-size: 1.1rem;
    color: var(--brand-navy);
}
.metric-pill--alert {
    background: rgba(248, 113, 113, 0.15);
    color: #991b1b;
}
.metric-pill--alert strong {
    color: #b91c1c;
}

/* --- BUTTONS --- */
.stButton > button {
    background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-dark));
    color: white;
    border: none;
    padding: 0.65rem 1.6rem;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.3px;
    box-shadow: 0 12px 20px rgba(37, 99, 235, 0.25);
    transition: 0.2s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    background: linear-gradient(135deg, var(--brand-primary-dark), #172554);
}
.stButton > button[kind="secondary"] {
    background: #ef4444;
}
.stButton > button[kind="secondary"]:hover {
    background: #dc2626;
}

/* --- EXPANDER --- */
.streamlit-expanderHeader {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 0.9rem 1rem;
    font-weight: 500;
    font-size: 0.9rem;
    color: #1e293b;
}
.streamlit-expanderHeader:hover {
    background-color: #f3f4f6;
}
.block-container > div:has(.streamlit-expanderHeader) {
    margin-bottom: 1rem;
}

/* --- BADGES --- */
.progress-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.badge-low { background: #fee2e2; color: #991b1b; }
.badge-medium { background: #fef3c7; color: #92400e; }
.badge-high { background: #dbeafe; color: #1e40af; }
.badge-complete { background: #d1fae5; color: #065f46; }

/* --- TABLES --- */
.stDataFrame table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.875rem;
    border-radius: 8px;
    overflow: hidden;
}
thead tr {
    background: rgba(37, 99, 235, 0.08) !important;
    color: var(--brand-navy);
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
tbody tr:hover {
    background-color: #f9fafb !important;
}
th, td {
    padding: 0.65rem 0.75rem !important;
    border-bottom: 1px solid rgba(15, 23, 42, 0.07) !important;
}
.stDataFrame {
    border-radius: 12px;
    box-shadow: 0 14px 30px rgba(15,23,42,0.07);
}

/* --- ALERT / INFO BOX --- */
.stAlert {
    border-radius: 8px;
    font-size: 0.9rem;
}
.stAlert div {
    font-weight: 500;
}

/* --- LOGIN CARD --- */
.login-container {
    max-width: 420px;
    margin: 5rem auto;
    background: var(--card-background);
    padding: 2.5rem;
    border-radius: 12px;
    box-shadow: 0 18px 35px rgba(15,23,42,0.12);
    border-top: 5px solid var(--brand-primary);
    text-align: center;
}
.login-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.5rem;
}
.login-subtitle {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 2rem;
}

/* --- LOGOUT BUTTON --- */
.logout-btn button {
    background: #ef4444 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.1rem !important;
    font-size: 0.85rem !important;
}
.logout-btn button:hover {
    background-color: #dc2626 !important;
}

.logout-button button {
    background-color: rgba(239, 68, 68, 0.12) !important;
    color: #b91c1c !important;
    border: 1px solid rgba(239, 68, 68, 0.45) !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    padding: 0.35rem 0.9rem !important;
    font-size: 0.8rem !important;
    width: auto !important;
    min-width: 0 !important;
    box-shadow: none !important;
}
.logout-button button:hover {
    background-color: rgba(248, 113, 113, 0.2) !important;
}
.section-heading {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}
.section-heading h3 {
    margin: 0;
    font-size: 1.25rem;
}
.section-heading span {
    font-size: 0.85rem;
    color: var(--text-muted);
}

/* --- EDITORIAL PANELS --- */
.status-panel {
    border-radius: 14px;
    padding: 1.1rem;
    border: 1px solid rgba(15, 23, 42, 0.08);
    background: rgba(255,255,255,0.9);
    box-shadow: 0 15px 30px rgba(15,23,42,0.06);
}
.status-panel h4 {
    margin: 0 0 0.5rem;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.08rem;
}
.status-panel--alert {
    background: linear-gradient(135deg, rgba(248, 113, 113, 0.15), rgba(248, 113, 113, 0.05));
    border-color: rgba(248, 113, 113, 0.4);
}
.status-panel--updates {
    background: linear-gradient(135deg, rgba(191, 219, 254, 0.3), rgba(191, 219, 254, 0.05));
    border-color: rgba(59, 130, 246, 0.25);
}
.status-item {
    margin-bottom: 0.65rem;
    padding-bottom: 0.45rem;
    border-bottom: 1px dashed rgba(15,23,42,0.08);
    font-size: 0.9rem;
}
.status-item:last-child {
    border-bottom: none;
    margin-bottom: 0;
}
.status-item strong {
    color: var(--brand-navy);
}

/* --- SUMMARY TABLE --- */
.summary-table h4 {
    margin-bottom: 0.35rem;
}
.summary-table-caption {
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
}
.summary-table .stDataFrame table {
    font-size: 0.78rem;
}
.summary-table thead tr {
    font-size: 0.7rem;
    letter-spacing: 0.08rem;
}
.summary-table tbody tr td {
    padding: 0.4rem 0.5rem !important;
}

/* --- PAGINATION --- */
.pagination-center {
    display: flex;
    justify-content: center;
    margin-top: 0.75rem;
}
.pagination-center .stButton>button {
    font-size: 0.85rem !important;
    border-radius: 8px !important;
}
.pagination-ellipsis {
    text-align: center;
    padding: 6px 0;
    color: #6b7280;
    font-weight: 500;
}

/* --- PROGRESS STEPPER --- */
.progress-stepper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 1rem;
    margin: 1rem 0 2rem 0;
    overflow-x: auto;
    gap: 0.75rem;
}

.step-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    flex: 0 0 auto;
    transition: all 0.3s ease;
    cursor: pointer;
}

.step-indicator.selected {
    transform: scale(1.08);
}

.step-indicator.selected .step-indicator-circle {
    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.25) !important;
}

.step-indicator-circle {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    border: 3px solid transparent;
}

.step-indicator-circle.completed {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border-color: #10b981;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.step-indicator-circle.active {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    color: white;
    border-color: #2563eb;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    animation: pulse 2s infinite;
}

.step-indicator-circle.upcoming {
    background: #f1f5f9;
    color: #94a3b8;
    border-color: #e2e8f0;
}

@keyframes pulse {
    0%, 100% {
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    50% {
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.6);
    }
}

.step-indicator-label {
    text-align: center;
    max-width: 120px;
}

.step-indicator-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-dark);
    margin-bottom: 0.15rem;
}

.step-indicator.upcoming .step-indicator-title {
    color: #94a3b8;
}

.step-indicator-subtitle {
    font-size: 0.7rem;
    color: var(--text-muted);
}

.step-indicator.upcoming .step-indicator-subtitle {
    color: #cbd5e1;
}

.step-connector {
    flex: 1 1 auto;
    height: 3px;
    background: #e2e8f0;
    position: relative;
    margin: 0 0.5rem;
    min-width: 30px;
}

.step-connector.completed {
    background: linear-gradient(90deg, #10b981 0%, #059669 100%);
}

.step-indicator-count {
    position: absolute;
    top: -8px;
    right: -8px;
    background: #ef4444;
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 999px;
    min-width: 20px;
    text-align: center;
}

/* --- RESPONSIVE --- */
@media (max-width: 768px) {
    .block-container { padding: 1rem; }
    .content-card { padding: 1.2rem; border-radius: 12px; }
    .masthead,
    .main-header { flex-direction: column; align-items: flex-start; }
    .masthead h1,
    .main-header h1 { font-size: 1.35rem; }
    .masthead-meta { gap: 0.45rem; }
    .stButton > button { width: 100%; }
    .stDataFrame { overflow-x: auto; }
    [data-testid="metric-container"] {
        flex: 1 1 50% !important;
        margin-bottom: 0.5rem !important;
    }
}
</style>
""", unsafe_allow_html=True)
