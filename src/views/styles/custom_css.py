"""
Custom CSS styles for the Hiring Tracker application.
Provides consistent styling across all pages and components.
Modern minimal design with blue theme.
"""

import streamlit as st


def inject_custom_css() -> None:
    """
    Inject custom CSS styles into the Streamlit application.
    """
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --brand-navy: #0f172a;
    --brand-navy-soft: #1d2b44;
    --brand-primary: #2563eb;
    --brand-primary-light: #3b82f6;
    --brand-primary-dark: #1e3a8a;
    --brand-primary-bg: rgba(37, 99, 235, 0.06);
    --brand-accent: #22d3ee;
    --brand-red: #ef4444;
    --brand-red-dark: #dc2626;
    --brand-green: #10b981;
    --brand-amber: #f59e0b;
    --brand-background: #f8fafc;
    --card-background: #ffffff;
    --card-border: rgba(15, 23, 42, 0.06);
    --card-shadow: 0 1px 3px rgba(15, 23, 42, 0.06), 0 4px 12px rgba(15, 23, 42, 0.04);
    --card-shadow-hover: 0 4px 12px rgba(15, 23, 42, 0.08), 0 8px 24px rgba(15, 23, 42, 0.06);
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --text-dark: #1e293b;
    --border-light: #e2e8f0;
    --border-default: #cbd5e1;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --transition-fast: 0.15s ease;
    --transition-normal: 0.2s ease;
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body {
    background: var(--brand-background);
    color: var(--text-primary);
}

/* --- GLOBAL --- */
#MainMenu, footer { visibility: hidden; }
.main { background-color: transparent; }
.block-container {
    padding: 1.5rem 3rem 2rem;
    max-width: 1400px;
    background: transparent;
}

/* --- HEADER / MASTHEAD --- */
.masthead-card {
    background: var(--card-background);
    padding: 1.25rem 1.75rem;
    border-radius: var(--radius-lg);
    border: 1px solid var(--card-border);
    box-shadow: var(--card-shadow);
    position: relative;
    overflow: hidden;
}
.masthead-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--brand-primary), var(--brand-accent));
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
.masthead-brand {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}
.masthead-logo {
    width: 90px;
    height: auto;
    opacity: 0.9;
}
.masthead-copy h1 {
    margin: 0;
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1.3;
}
.masthead-subtitle {
    margin: 0.15rem 0 0;
    font-size: 0.875rem;
    color: var(--text-secondary);
    font-weight: 400;
}
.masthead-kicker {
    text-transform: uppercase;
    font-size: 0.65rem;
    letter-spacing: 0.2rem;
    color: var(--brand-primary);
    font-weight: 600;
    display: inline-block;
    margin-bottom: 0.15rem;
}
.masthead-meta {
    margin-top: 0.5rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    font-size: 0.8rem;
    color: var(--text-secondary);
    align-items: center;
}
.masthead-meta strong {
    color: var(--text-primary);
    font-weight: 600;
}
.masthead-role {
    color: var(--brand-primary);
    font-weight: 600;
}
.masthead-role-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: var(--brand-primary-bg);
    color: var(--brand-primary);
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* --- CONTENT CARDS --- */
.content-card {
    background: var(--card-background);
    padding: 1.5rem;
    border-radius: var(--radius-lg);
    box-shadow: var(--card-shadow);
    margin-bottom: 1.25rem;
    border: 1px solid var(--card-border);
}
.content-card h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    letter-spacing: -0.01em;
}

/* --- METRICS --- */
div[data-testid="stMetricValue"] {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--brand-primary);
}
div[data-testid="stMetricLabel"] {
    font-size: 0.8rem;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 0.04em;
}
.metric-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.75rem;
    width: 100%;
}
.metric-card {
    background: var(--card-background);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-md);
    padding: 1.25rem 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    box-shadow: var(--card-shadow);
    transition: var(--transition-normal);
}
.metric-card:hover {
    box-shadow: var(--card-shadow-hover);
}
.metric-card-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 0.35rem;
    font-weight: 500;
}
.metric-card-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--brand-primary);
    line-height: 1.2;
}

/* Interactive metric card buttons */
/* Default state (secondary) */
div[data-testid="column"] .stButton>button[kind="secondary"] {
    background: var(--card-background) !important;
    border: 1.5px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem !important;
    min-height: 120px !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    text-align: center !important;
    box-shadow: var(--card-shadow) !important;
    white-space: pre-wrap !important;
    line-height: 1.5 !important;
    transition: all var(--transition-normal) !important;
}
/* Active state (primary) */
div[data-testid="column"] .stButton>button[kind="primary"] {
    background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-dark)) !important;
    border: 1.5px solid var(--brand-primary) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem !important;
    min-height: 120px !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    text-align: center !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
    white-space: pre-wrap !important;
    line-height: 1.5 !important;
    transition: all var(--transition-normal) !important;
}
div[data-testid="column"] .stButton>button[kind="secondary"]:hover:not(:disabled) {
    border-color: var(--brand-primary) !important;
    transform: translateY(-1px) !important;
    box-shadow: var(--card-shadow-hover) !important;
    color: var(--brand-primary) !important;
}
div[data-testid="column"] .stButton>button[kind="primary"]:hover:not(:disabled) {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3) !important;
}
div[data-testid="column"] .stButton>button:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
}

/* --- BUTTONS --- */
.stButton > button {
    background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-dark));
    color: white;
    border: none;
    padding: 0.55rem 1.4rem;
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.01em;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
    transition: all var(--transition-normal);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}
.stButton > button[kind="secondary"] {
    background: var(--brand-red);
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.2);
}
.stButton > button[kind="secondary"]:hover {
    background: var(--brand-red-dark);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

/* --- EXPANDER --- */
.streamlit-expanderHeader {
    background-color: var(--card-background);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-sm);
    padding: 0.5rem 0.75rem;
    font-weight: 500;
    font-size: 0.8rem;
    color: var(--text-primary);
    transition: all var(--transition-fast);
}
.streamlit-expanderHeader:hover {
    background-color: #f8fafc;
    border-color: var(--border-default);
}
/* Compact expander spacing */
div[data-testid="stExpander"] {
    margin-bottom: 0.3rem !important;
}
div[data-testid="stExpander"] details {
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-sm) !important;
}
div[data-testid="stExpander"] summary {
    padding: 0.45rem 0.75rem !important;
    font-size: 0.8rem !important;
    line-height: 1.4 !important;
}

/* --- BADGES --- */
.progress-badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.badge-low { background: #fef2f2; color: #991b1b; }
.badge-medium { background: #fffbeb; color: #92400e; }
.badge-high { background: #eff6ff; color: #1e40af; }
.badge-complete { background: #f0fdf4; color: #166534; }

/* --- TABLES --- */
.stDataFrame table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.825rem;
    border-radius: var(--radius-sm);
    overflow: hidden;
}
thead tr {
    background: #f8fafc !important;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-size: 0.75rem;
}
tbody tr {
    transition: background var(--transition-fast);
}
tbody tr:hover {
    background-color: #f8fafc !important;
}
th, td {
    padding: 0.6rem 0.75rem !important;
    border-bottom: 1px solid var(--border-light) !important;
}
.stDataFrame {
    border-radius: var(--radius-md);
    border: 1px solid var(--card-border);
    overflow: hidden;
}

/* --- ALERT / INFO BOX --- */
.stAlert {
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    border: none;
}

/* --- LOGIN CARD --- */
.login-container {
    max-width: 420px;
    margin: 3rem auto;
    background: var(--card-background);
    padding: 2.5rem 2.5rem 2rem;
    border-radius: var(--radius-xl);
    box-shadow: 0 8px 30px rgba(15,23,42,0.08);
    border: 1px solid var(--card-border);
    position: relative;
    overflow: hidden;
}
.login-container::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--brand-primary), var(--brand-accent));
}
.login-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
}
.login-logo img {
    width: 48px;
    height: auto;
    border-radius: 10px;
}
.login-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.2;
    letter-spacing: -0.02em;
}
.login-subtitle {
    text-align: center;
    font-size: 0.825rem;
    color: var(--text-secondary);
    margin: 0.25rem 0 1.5rem;
}
.login-footer {
    text-align: center;
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-light);
}
.login-form input[type="text"],
.login-form input[type="password"] {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid var(--border-light) !important;
    padding: 0.65rem 0.9rem !important;
    font-size: 0.9rem !important;
    transition: all var(--transition-fast) !important;
    background: #f8fafc !important;
}
.login-form input[type="text"]:focus,
.login-form input[type="password"]:focus {
    border-color: var(--brand-primary) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.08) !important;
    background: var(--card-background) !important;
}
.login-form .stButton > button {
    width: 100%;
    margin-top: 0.5rem;
    padding: 0.7rem !important;
    font-size: 0.95rem !important;
    border-radius: var(--radius-sm) !important;
}

/* --- LOGOUT BUTTON --- */
.logout-btn button,
.logout-button button {
    background-color: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    padding: 0.4rem 1rem !important;
    font-size: 0.8rem !important;
    box-shadow: none !important;
    transition: all var(--transition-fast) !important;
}
.logout-btn button:hover,
.logout-button button:hover {
    background-color: #fef2f2 !important;
    color: var(--brand-red) !important;
    border-color: rgba(239, 68, 68, 0.3) !important;
}

/* --- SECTION HEADING --- */
.section-heading {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}
.section-heading h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: -0.01em;
}
.section-heading span {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

/* --- STATUS PANELS --- */
.status-panel {
    border-radius: var(--radius-md);
    padding: 1rem;
    border: 1px solid var(--card-border);
    background: var(--card-background);
    box-shadow: var(--card-shadow);
}
.status-panel h4 {
    margin: 0 0 0.5rem;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-secondary);
}
.status-panel--alert {
    background: #fef2f2;
    border-color: rgba(239, 68, 68, 0.15);
}
.status-panel--updates {
    background: #eff6ff;
    border-color: rgba(37, 99, 235, 0.15);
}
.status-item {
    margin-bottom: 0.5rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border-light);
    font-size: 0.85rem;
}
.status-item:last-child {
    border-bottom: none;
    margin-bottom: 0;
}
.status-item strong {
    color: var(--text-primary);
}

/* --- METRIC GROUPS --- */
.metric-groups {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 0.75rem;
}
.metric-group {
    border: 1px solid var(--card-border);
    border-radius: var(--radius-md);
    padding: 1rem;
    background: var(--card-background);
    box-shadow: var(--card-shadow);
}
.metric-group h4 {
    margin: 0 0 0.35rem;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
}
.metric-stack {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
}
.metric-pill {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 0.45rem 0.65rem;
    border-radius: var(--radius-sm);
    background: #f8fafc;
    font-size: 0.825rem;
    color: var(--text-primary);
}
.metric-pill strong {
    font-size: 1rem;
    color: var(--text-primary);
    font-weight: 700;
}
.metric-pill--alert {
    background: #fef2f2;
    color: #991b1b;
}
.metric-pill--alert strong {
    color: #b91c1c;
}

/* --- SUMMARY TABLE --- */
.summary-table h4 {
    margin-bottom: 0.35rem;
}
.summary-table-caption {
    color: var(--text-secondary);
    font-size: 0.825rem;
    margin-bottom: 0.5rem;
}
.summary-table .stDataFrame table {
    font-size: 0.75rem;
}
.summary-table thead tr {
    font-size: 0.65rem;
    letter-spacing: 0.06em;
}
.summary-table tbody tr td {
    padding: 0.35rem 0.5rem !important;
}

/* --- PAGINATION --- */
.pagination-center {
    display: flex;
    justify-content: center;
    margin-top: 0.5rem;
}
.pagination-center .stButton>button {
    font-size: 0.8rem !important;
    border-radius: var(--radius-sm) !important;
}
.pagination-ellipsis {
    text-align: center;
    padding: 6px 0;
    color: var(--text-muted);
    font-weight: 500;
}

/* --- PROGRESS STEPPER (column-based) --- */
.step-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 0.75rem 0.25rem 0.25rem;
    border-radius: var(--radius-md);
    transition: background var(--transition-normal);
    cursor: default;
}
.step-col:hover {
    background: rgba(37, 99, 235, 0.04);
}
.step-col.selected {
    background: rgba(37, 99, 235, 0.08);
    border-radius: var(--radius-md);
}
.step-circle {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.85rem;
    position: relative;
    margin-bottom: 0.4rem;
    transition: all var(--transition-normal);
}
.step-circle.completed {
    background: var(--brand-green);
    color: white;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25);
}
.step-circle.active {
    background: var(--brand-primary);
    color: white;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
}
.step-circle.upcoming {
    background: #f1f5f9;
    color: var(--text-muted);
    border: 2px solid var(--border-light);
}
.step-badge {
    position: absolute;
    top: -5px;
    right: -5px;
    background: var(--brand-red);
    color: white;
    font-size: 0.58rem;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 999px;
    min-width: 16px;
    text-align: center;
    line-height: 1.4;
    z-index: 3;
}
.step-title {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.3;
    margin-bottom: 1px;
}
.step-sub {
    font-size: 0.62rem;
    color: var(--text-secondary);
    line-height: 1.3;
}
.step-col .step-circle.upcoming ~ .step-title,
.step-col .step-circle.upcoming ~ .step-sub {
    color: var(--text-muted);
}
/* Make stepper buttons small & subtle */
[data-testid="stVerticalBlock"] .step-col + div button {
    padding: 0.15rem 0 !important;
    font-size: 0.65rem !important;
    min-height: 0 !important;
    height: auto !important;
    background: transparent !important;
    border: 1px solid var(--border-light) !important;
    color: var(--text-secondary) !important;
    box-shadow: none !important;
    border-radius: var(--radius-sm) !important;
}
[data-testid="stVerticalBlock"] .step-col + div button:hover {
    background: rgba(37, 99, 235, 0.06) !important;
    color: var(--brand-primary) !important;
    border-color: var(--brand-primary) !important;
}

/* --- MULTISELECT TAG STYLING --- */
div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-dark)) !important;
    color: white !important;
    border-radius: 999px !important;
    padding: 0.15rem 0.5rem !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    border: none !important;
}
div[data-testid="stMultiSelect"] span[data-baseweb="tag"] span[role="presentation"] {
    color: rgba(255,255,255,0.8) !important;
}
div[data-testid="stMultiSelect"] span[data-baseweb="tag"]:hover span[role="presentation"] {
    color: white !important;
}

/* --- CANDIDATE CARD --- */
.candidate-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
}
.candidate-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}
.candidate-score {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    color: white;
}
.candidate-status-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.candidate-info-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    font-size: 0.825rem;
    color: var(--text-secondary);
}
.candidate-info-item {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
}
.candidate-info-item strong {
    color: var(--text-primary);
    font-weight: 500;
}
.candidate-link-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 500;
    background: #eff6ff;
    color: var(--brand-primary);
    text-decoration: none;
    transition: all var(--transition-fast);
    border: 1px solid rgba(37, 99, 235, 0.15);
}
.candidate-link-pill:hover {
    background: #dbeafe;
    border-color: rgba(37, 99, 235, 0.3);
}
.candidate-link-pill.link-expired-fallback {
    background: #fffbeb;
    color: #92400e;
    border-color: rgba(217, 119, 6, 0.2);
}
.candidate-link-pill.link-expired-fallback:hover {
    background: #fef3c7;
    border-color: rgba(217, 119, 6, 0.4);
}
.candidate-link-pill.link-expired {
    background: #fef2f2;
    color: #991b1b;
    border-color: rgba(239, 68, 68, 0.15);
    cursor: default;
}
.ai-analysis-card {
    background: #f8fafc;
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    padding: 1rem;
    margin-bottom: 0.75rem;
}
.ai-analysis-card h5 {
    margin: 0 0 0.5rem;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-secondary);
}
.ai-analysis-card ul {
    margin: 0;
    padding-left: 1.25rem;
    font-size: 0.825rem;
    color: var(--text-primary);
}
.ai-analysis-card li {
    margin-bottom: 0.2rem;
    line-height: 1.5;
}
.comment-card {
    background: #f8fafc;
    border: 1px solid var(--border-light);
    border-radius: var(--radius-sm);
    padding: 0.75rem;
    margin-bottom: 0.5rem;
}
.comment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.35rem;
    font-size: 0.8rem;
}
.comment-author {
    font-weight: 600;
    color: var(--text-primary);
}
.comment-time {
    color: var(--text-muted);
    font-size: 0.7rem;
}
.comment-action-badge {
    display: inline-flex;
    padding: 0.1rem 0.45rem;
    border-radius: 999px;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-left: 0.35rem;
}
.comment-action-badge.approved {
    background: #f0fdf4;
    color: #166534;
}
.comment-action-badge.rejected {
    background: #fef2f2;
    color: #991b1b;
}
.comment-text {
    font-size: 0.825rem;
    color: var(--text-primary);
    line-height: 1.5;
}

/* --- OPTION MENU OVERRIDE --- */
div[data-testid="stHorizontalBlock"] .nav-link {
    font-family: 'Inter', sans-serif !important;
}

/* --- RESPONSIVE --- */
@media (max-width: 768px) {
    .block-container { padding: 1rem; }
    .content-card { padding: 1rem; border-radius: var(--radius-md); }
    .masthead-card { padding: 1rem; }
    .masthead-brand { flex-direction: column; align-items: flex-start; }
    .masthead-copy h1 { font-size: 1.2rem; }
    .masthead-meta { gap: 0.3rem; }
    .stButton > button { width: 100%; }
    .stDataFrame { overflow-x: auto; }
    .metric-card-grid { grid-template-columns: repeat(2, 1fr); }
    div[data-testid="column"] .stButton>button[kind="secondary"],
    div[data-testid="column"] .stButton>button[kind="primary"] {
        min-height: 90px !important;
        padding: 0.75rem !important;
    }
}
</style>
""", unsafe_allow_html=True)
