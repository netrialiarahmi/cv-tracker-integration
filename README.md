# Kompas.com Hiring Tracker

A modern, modular hiring management system built with Streamlit. Track hiring progress across multiple divisions with role-based access control.

## Features

- 🔐 **Multi-role Authentication**: Superadmin, Admin, and Division user roles
- 📊 **Dynamic Hiring Pipeline**: Customizable stages with skill test toggle
- 👥 **User Management**: Full CRUD operations for divisions (Superadmin)
- 📈 **Progress Tracking**: Real-time progress calculations and metrics
- 📎 **File Attachments**: Upload and manage documents for positions
- 🔍 **Search & Filter**: Find positions quickly across all data
- 💾 **Data Persistence**: JSON-based storage with GitHub fallback
- 🔄 **Auto-sync with Planner**: Automated sync from Microsoft Planner every 10 minutes
- 🎨 **Modern UI**: Responsive design with custom styling

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/netrialiarahmi/ht-2-.git
cd ht-2-
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
ht-2-/
├── app.py                 # Main application entry point
├── config/                # Configuration and constants
├── core/                  # Core business logic
├── models/                # Data models
├── services/              # Business services
├── ui/                    # User interface components and pages
├── utils/                 # Utility functions
├── scripts/               # Automation scripts (Planner sync)
├── data/                  # Data files (hiring-data.json)
├── .github/workflows/     # GitHub Actions (auto-sync)
└── requirements.txt       # Python dependencies
```

## Microsoft Planner Sync

The system automatically syncs hiring data from Microsoft Planner every 10 minutes using GitHub Actions.

**Quick Links:**
- 📖 [Quick Start Guide](QUICKSTART.md)
- 📚 [Full Documentation](PLANNER_SYNC_README.md)

**Features:**
- Automated sync every 10 minutes
- Smart data mapping (buckets → stages, labels → divisions)
- Data preservation (Job Description, Attachments)
- Merge by Job Position (no data loss)

**Setup:**
GitHub Secrets required (already configured):
- `MICROSOFT_EMAIL`
- `MICROSOFT_PASSWORD`
- `PLANNER_URL`

## Configuration

### HR Roles
Configure HR credentials in one of these locations (in priority order):
1. `.streamlit/secrets.toml`
2. Streamlit Cloud secrets
3. `hr_roles.json`

### Data Files
- `credentials.json`: Division user credentials
- `data/hiring-data.json`: Hiring positions data (auto-synced from Planner)

These files are auto-created with defaults on first run.

## User Roles

### HR Superadmin
- Full system access
- User management (create, edit, delete divisions)
- Hiring pipeline management (all divisions)
- PIC assignment
- Skill test toggle

### HR Admin
- View assigned positions (filtered by PIC)
- Edit hiring stages for assigned positions
- Add notes and attachments
- Update job descriptions

### Division User
- Read-only access to own division's positions
- View hiring progress
- Search positions
- View summary tables

## Development

### Module Structure

- **config/**: Global settings and constants
- **core/**: Authentication, data management, session handling
- **models/**: User and hiring data models
- **services/**: Business logic shared across pages
- **ui/**: Components and page modules
  - `components/`: Reusable UI elements
  - `pages/`: Full page implementations
  - `styles/`: CSS styling
- **utils/**: Helper functions, validators, formatters

### Adding New Features

1. **New Dashboard Type**: Create a new file in `ui/pages/`
2. **New Component**: Add to `ui/components/`
3. **New Business Logic**: Add to `services/`
4. **New Data Model**: Add to `models/`
5. **New Configuration**: Update `config/settings.py`

### Code Style

- Follow PEP 8 naming conventions
- Add type hints to all functions
- Include docstrings for modules and functions
- Keep functions small and single-purpose
- Use constants from `config.settings`

## Hiring Pipeline Stages

Default stages:
1. Initial Interview (HR)
2. HR & User Interview (Stage 1)
3. Skill Test (optional)
4. Final Interview
5. Offering
6. Contract Sign
7. On Boarding

The Skill Test stage can be toggled per position by Superadmin.

## Data Backup

The application supports GitHub fallback for `hiring_data.json`. Configure in `config/settings.py`:
```python
GITHUB_REPO = "netrialiarahmi/hiring-tracker"
GITHUB_BRANCHES = ["main", "master"]
```

## Troubleshooting

### Data not persisting
- Check write permissions for `credentials.json` and `hiring_data.json`
- Ensure the files are not corrupted (valid JSON)

### Session not persisting
- Ensure query parameters are enabled in browser
- Check browser console for errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- Open an issue on GitHub
- Contact: [Add contact information]

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [Pillow](https://python-pillow.org/) - Image processing

---

© 2025 Kompas.com — Human Resource Division
