# Kompas.com Hiring Desk — System Flow

## Arsitektur Sistem

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  Microsoft Planner  │     │  CV Matching Auto     │     │  Hiring Tracker v2  │
│  (Source of Truth)   │     │  (AI Screening)       │     │  (Backup Repo)      │
│                     │     │                      │     │                     │
│  netrialiarahmi/    │     │  netrialiarahmi/     │     │  netrialiarahmi/    │
│  hiring-tracker     │     │  cv-matching-auto    │     │  hiring-tracker-v2  │
└────────┬────────────┘     └──────┬───────────────┘     └──────▲──────────────┘
         │                         │                            │
         │ GitHub Actions          │ GitHub API (read)          │ GitHub API (write)
         │ Daily 07:00 WIB         │ raw.githubusercontent      │ Auto-backup
         │                         │                            │
         ▼                         ▼                            │
┌────────────────────────────────────────────────────────────────┤
│                     HIRING DESK APP                           │
│                     (Streamlit)                               │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Hiring Data  │  │ Screening    │  │ Candidates           │ │
│  │ Pipeline     │  │ Results      │  │ & Feedback           │ │
│  │              │  │              │  │                      │ │
│  │ hiring-      │  │ Fetched from │  │ candidates.json      │ │
│  │ data.json    │  │ cv-matching  │  │ feedback.json        │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

---

## Repository yang Terlibat

| Repo | Fungsi | URL |
|------|--------|-----|
| `netrialiarahmi/hiring-tracker` | Main repo — kode app + GitHub Actions sync | Tempat deploy |
| `netrialiarahmi/cv-matching-auto` | AI screening engine — hasilkan CSV screening per posisi | Sumber data screening |
| `netrialiarahmi/hiring-tracker-v2` | Backup repo — auto-backup data JSON via API | Disaster recovery |

---

## Data Flow Detail

### 1. Microsoft Planner → hiring-data.json (GitHub Actions)

```
Microsoft Planner Board
        │
        │  GitHub Actions: sync-planner.yml
        │  Schedule: Daily 07:00 WIB (cron: '0 0 * * *')
        │  Trigger: Manual (workflow_dispatch) juga bisa
        │
        ▼
┌─────────────────────────────┐
│  sync-planner.js            │
│                             │
│  1. Launch Chromium          │
│     (Playwright headless)   │
│  2. Login Microsoft 365     │
│     (MICROSOFT_EMAIL/PASS)  │
│  3. Open Planner Board URL  │
│  4. Export ke Excel/CSV     │
│  5. Parse & transform data  │
│  6. Save hiring-data.json   │
│  7. git commit & push       │
└─────────────────────────────┘
        │
        ▼
  data/hiring-data.json (updated)
  → Otomatis ke-deploy di app
```

**Environment Secrets (GitHub Actions):**
- `MICROSOFT_EMAIL` — Email login Microsoft 365
- `MICROSOFT_PASSWORD` — Password Microsoft 365
- `PLANNER_URL` — URL board Planner yang di-scrape

---

### 2. CV Matching Auto → Screening Results (GitHub API Read)

```
cv-matching-auto repo
├── data/job_positions.csv          ← Daftar posisi + JD
├── data/processed/
│   ├── results_Software_Engineer.csv
│   ├── results_Reporter_Megapolitan.csv
│   ├── results_Account_Executive_VCBL.csv
│   └── ...                         ← 1 CSV per posisi
└── feedback/
    ├── Software_Engineer.json       ← Feedback dari hiring manager
    └── Reporter_Megapolitan.json

        │
        │  raw.githubusercontent.com (read)
        │  GITHUB_TOKEN required
        │
        ▼

Hiring Desk App
├── fetch_screening_results(position_name)
│   → GET results_{safe_name}.csv
│   → Parse ke DataFrame
│   → Display di Screening Tab
│
└── fetch_job_positions_from_cv_matching()
    → GET data/job_positions.csv
    → List posisi yang tersedia
```

**Position Linking:**  
Posisi di Planner dan di CV Matching bisa beda nama.  
Mapping disimpan di `data/position-links.json`:

```json
{
  "Mobile Apps iOS Engineer": "iOS Engineer",
  "Account Executive Kompas.com (Brand)": "Account Executive KOMPAS.com",
  "Reporter Megapolitan": "Reporter Megapolitan"
}
```
Key = nama di Planner, Value = nama di CV Matching.

---

### 3. Escalation & Candidate Flow

```
Screening Results (CSV from cv-matching-auto)
        │
        │ HR klik "Escalate to User Interview"
        │
        ▼
┌────────────────────────┐
│  candidates.json       │ ← Saved locally
│                        │ ← Auto-backup ke hiring-tracker-v2
│  Status: "Escalated"   │
└────────┬───────────────┘
         │
         │ Division user login → lihat candidate card
         │
         ▼
┌──────────────────────────────────────┐
│  Division Dashboard — Candidates Tab │
│                                      │
│  [Approve] → Status: "Approved"      │
│  [Reject]  → Status: "Rejected"      │
│  [Reset]   → Status: "Escalated"     │
│  [Clear Comments]                    │
└────────┬─────────────────────────────┘
         │
         │ On approve/reject:
         │
         ▼
┌────────────────────────────────────────┐
│  Feedback Loop                         │
│                                        │
│  1. Comment saved to candidates.json   │
│  2. Backup candidates.json → GitHub    │
│  3. feedback.json updated locally      │
│  4. feedback/{position}.json → pushed  │
│     to cv-matching-auto repo           │
│  5. cv-matching AI reads feedback      │
│     → adjusts scoring prompt           │
│     → next screening run more accurate │
└────────────────────────────────────────┘
```

---

### 4. Auto-Backup Flow (Setiap Save)

```
Any data change (escalate, comment, approve, reject, reset)
        │
        ▼
save_candidates(candidates)
        │
        ├── 1. Write data/candidates.json (local)
        │
        └── 2. _backup_candidates_to_github()
                │
                ├── GET existing file SHA dari hiring-tracker-v2
                └── PUT updated content (base64) ke hiring-tracker-v2
                    Commit: "Auto-backup: Update candidates.json - 2026-04-16 13:22:58"
```

Yang di-backup ke `hiring-tracker-v2`:
- `data/candidates.json` — Candidate data + comments
- `data/hiring-data.json` — Pipeline data
- `credentials.json` — Division passwords

---

## Login Flow

```
┌──────────────────────┐
│   Login Page          │
│                      │
│   [Username] [Pass]  │
│   [Sign In]          │
└──────────┬───────────┘
           │
           ▼
    authenticate_user(username, password)
           │
           ├── 1. Check: Superadmin?
           │       username == "hrsuper" && password match
           │       → role: "HR Superadmin"
           │       → Superadmin Dashboard (full access)
           │
           ├── 2. Check: HR Admin?
           │       username in admins dict && password match
           │       → role: "HR Admin"
           │       → Admin Dashboard (PIC-filtered)
           │
           └── 3. Check: Division user?
                   username in DIVISION_USERNAMES && password match
                   → role: "Division"
                   → Division Dashboard (read-only + candidates)
```

**Credential Sources (priority order):**
1. `.streamlit/secrets.toml` — Manual override
2. `st.secrets` — Streamlit Cloud managed
3. `hr_roles.json` — Runtime managed (jika ada)
4. `settings.py DEFAULT_HR_ROLES` — Fallback default
5. `credentials.json` — Division passwords

---

## User Roles & Access

| Role | Dashboard | Bisa Apa |
|------|-----------|----------|
| **HR Superadmin** | Superadmin Dashboard | Lihat semua posisi, screening results, escalate candidates, reset escalation/status |
| **HR Admin** | Admin Dashboard | Lihat posisi assigned (by PIC), screening results, escalate, reset |
| **Division** | Division Dashboard | Lihat pipeline divisi sendiri, review candidates, approve/reject/reset/clear comments |

---

## GitHub Actions Summary

### `sync-planner.yml`
- **Trigger:** Daily 07:00 WIB + manual
- **Apa yang dilakukan:**
  1. Checkout repo
  2. Setup Node.js 20 + install deps
  3. Install Playwright Chromium
  4. Login ke Microsoft 365 via Playwright
  5. Scrape Planner board → export data
  6. Parse Excel → transform → save `hiring-data.json`
  7. If data changed → commit & push
- **Secrets diperlukan:**
  - `MICROSOFT_EMAIL`
  - `MICROSOFT_PASSWORD`
  - `PLANNER_URL`

---

## File Penting

```
cv-tracker-integration/
├── app.py                          # Entry point Streamlit
├── .env                            # GITHUB_TOKEN, MS credentials (gitignored)
├── credentials.json                # Division passwords (gitignored)
├── .github/workflows/
│   └── sync-planner.yml            # GitHub Actions: daily Planner sync
├── data/
│   ├── hiring-data.json            # Pipeline data (from Planner)
│   ├── candidates.json             # Escalated candidates + comments
│   ├── feedback.json               # Division feedback on candidates
│   └── position-links.json         # Mapping: Planner position → CV Matching position
├── scripts/
│   ├── sync-planner.js             # Playwright scraper for Planner
│   ├── excel-parser.js             # Parse exported Excel/CSV
│   └── data-transformer.js         # Transform raw data to app format
└── src/
    ├── config/settings.py          # All repo URLs, credentials config
    ├── controllers/
    │   ├── auth.py                 # Unified authenticate_user()
    │   └── session_manager.py      # Session state + query param persistence
    ├── services/
    │   ├── candidate_service.py    # Escalate, comment, backup to GitHub
    │   ├── feedback_service.py     # Feedback aggregation, sync to cv-matching
    │   └── linking_service.py      # Position link mapping
    └── views/pages/
        ├── login.py                # Unified username+password login
        ├── superadmin_dashboard.py # Full access dashboard
        ├── admin_dashboard.py      # PIC-filtered dashboard
        └── division_dashboard.py   # Division read-only + candidates
```

---

## Feedback Loop (Closed Loop dengan CV Matching)

```
                    ┌──────────────────────────┐
                    │  CV Matching Auto         │
                    │                          │
          ┌────────│  AI Screen CVs            │◄─────────┐
          │        │  → results_{pos}.csv      │          │
          │        └──────────────────────────┘          │
          │                                              │
          │  Fetch screening results                     │  Push feedback JSON
          │  (raw.githubusercontent.com)                 │  (GitHub API PUT)
          │                                              │
          ▼                                              │
┌──────────────────────────────────────────────┐         │
│  Hiring Desk App                              │         │
│                                              │         │
│  HR reviews screening → escalates candidate  │         │
│  Division approves/rejects with comment      │─────────┘
│  → feedback saved to feedback.json           │
│  → synced to cv-matching-auto/feedback/      │
│                                              │
│  Next screening run reads feedback           │
│  → AI adjusts scoring criteria               │
│  → Better candidate matches over time        │
└──────────────────────────────────────────────┘
```

Feedback yang dikirim ke `cv-matching-auto` berisi:
- Siapa yang approve/reject
- Alasan (comment text)
- Candidate name & position
- Timestamp

CV Matching AI membaca feedback ini untuk menyesuaikan prompt screening → semakin akurat seiring waktu.
