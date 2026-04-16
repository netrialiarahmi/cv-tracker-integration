# Microsoft Planner Sync

Automated synchronization of hiring data from Microsoft Planner to the Hiring Tracker using Playwright.

## Overview

This system automatically syncs hiring data from Microsoft Planner to the hiring tracker every 10 minutes using GitHub Actions. It uses Playwright to:
1. Login to Microsoft
2. Navigate to the Planner board
3. Export plan data to Excel (.xlsx format)
4. Transform and merge the data with existing records
5. Update the hiring tracker database

## Features

- ✅ **Automated Sync**: Runs every 10 minutes via GitHub Actions
- ✅ **Data Preservation**: Preserves existing fields (Job Description, Attachments)
- ✅ **Smart Merging**: Merges by Job Position, doesn't replace everything
- ✅ **Stage Mapping**: Maps Planner buckets to hiring stages
- ✅ **Division Detection**: Extracts division from labels
- ✅ **PIC Assignment**: Maps assigned users to PICs
- ✅ **Freeze Status**: Handles HOLD and CANCELED tasks
- ✅ **Error Handling**: Graceful degradation and detailed logging

## Setup

### Prerequisites

- Node.js 20 or higher
- Microsoft account with access to the Planner board
- GitHub repository with Actions enabled

### Local Development

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Install Playwright browsers**:
   ```bash
   npx playwright install chromium
   ```

3. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

4. **Configure environment variables** in `.env`:
   ```env
   MICROSOFT_EMAIL=your-email@example.com
   MICROSOFT_PASSWORD=your-password
   PLANNER_URL=https://tasks.office.com/...
   DATA_FILE=data/hiring-data.json
   TIMEZONE=Asia/Jakarta
   ```

5. **Run sync manually**:
   ```bash
   npm run sync
   ```

### GitHub Actions Setup

1. **Add repository secrets** in GitHub:
   - Go to repository Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `MICROSOFT_EMAIL`: Microsoft account email
     - `MICROSOFT_PASSWORD`: Microsoft account password
     - `PLANNER_URL`: Full URL to the Planner board

2. **Enable GitHub Actions**:
   - The workflow is in `.github/workflows/sync-planner.yml`
   - It runs automatically every 10 minutes
   - Can also be triggered manually from the Actions tab

3. **Verify workflow**:
   - Go to Actions tab in GitHub
   - Look for "Sync Microsoft Planner Data" workflow
   - Check run logs for any errors

## Data Mapping

### Bucket to Stages

| Planner Bucket | Hiring Tracker Stages |
|----------------|----------------------|
| Backlog (Employee Req Form) | All stages: false |
| Approval Circular & Review | Initial screening: true, rest: false |
| HR & User Interview + Skill Test | Initial + Interview: true, rest: false |
| Offering | Through Offering: true, rest: false |
| Order for Contract Sign | Through Contract Sign: true, Onboarding: false |
| Sudah Sign Contract | All stages: true |
| HOLD / CANCELED | Preserve existing stages, set Freeze: true |

**Special**: If Progress = "Completed", all stages become true.

### Division Mapping

Labels in Planner are mapped to divisions:

- `Technology` → Technology Engineering Division
- `Redaksi Teks` → Kompas.com News - Text Department
- `Redaksi Video` → Kompas.com News - Video & Social Media Department
- `Integrated Marketing` → Lative Ads Department
- `Marcomm Kompascom` → Marketing Communication Kompas.com
- `VCBL` → VCBL & Pasangiklan
- `Kompascom Sales` → Sales

### PIC Mapping

Assigned To field is mapped to PIC:

- `Adelia Galuh H` → adelia
- `Rizky Pangestu` → rizky
- `Novinda Riski` → vania
- `Member` → adelia (default)

### Hire Type

Extracted from Labels:
- `Additional` label → Hire Type: Additional
- `Replacement` label → Hire Type: Replacement

### Replacement For

Extracted from Description field by looking for keywords:
- "replace", "pengganti", "replacement"
- Extracts the name that follows

## File Structure

```
.
├── .github/
│   └── workflows/
│       └── sync-planner.yml      # GitHub Actions workflow
├── scripts/
│   ├── config.js                 # Configuration & mappings
│   ├── excel-parser.js           # Excel and CSV parser
│   ├── data-transformer.js       # Data transformation logic
│   └── sync-planner.js           # Main Playwright script
├── data/
│   └── hiring-data.json          # Target data file
├── downloads/                     # Temporary download folder
├── package.json                  # Node.js dependencies
├── playwright.config.js          # Playwright configuration
└── .env.example                  # Environment template
```

## Data Preservation

The sync system **preserves** the following fields from existing data:
- Job Description (not in Planner)
- Attachments (not in Planner)
- Custom notes that aren't from Planner

It **updates** these fields from Planner:
- Stage checkboxes
- PIC
- Notes (merged with existing)
- Last Updated
- Freeze status

## Troubleshooting

### Login fails
- Check MICROSOFT_EMAIL and MICROSOFT_PASSWORD are correct
- Check if 2FA is enabled (may need app password)
- Check browser logs in failed workflow

### Export button not found
- Verify PLANNER_URL is correct
- Check if Planner interface changed
- Update selectors in sync-planner.js

### File parsing errors
- Planner exports .xlsx files by default, which are now supported
- CSV format is also supported for backward compatibility
- Check if Planner export format changed
- Verify semicolon delimiter is used for CSV files
- Check config.js column names

### Data not updating
- Check GitHub Actions logs
- Verify secrets are set correctly
- Check file permissions

### Missing divisions or PICs
- Update mapping in config.js
- Add new labels or users to mapping tables

## Manual Testing

To test the transformation logic without running Playwright:

1. Export Excel manually from Planner
2. Save as `test-export.csv` in downloads folder
3. Run transformer test:
   ```bash
   node scripts/test-transformer.js
   ```

## Logs

The sync process logs:
- Login status
- Export progress
- File parsing results
- Transformation details (added/updated/preserved)
- File save status

Check GitHub Actions logs for detailed output.

## Maintenance

### Updating Mappings

Edit `scripts/config.js` to update:
- Division mappings
- PIC mappings
- Bucket stage mappings
- Special handling rules

### Updating Selectors

If Planner interface changes, update selectors in `scripts/sync-planner.js`:
- Export button selectors
- Login field selectors

### Changing Schedule

Edit `.github/workflows/sync-planner.yml`:
```yaml
schedule:
  - cron: '*/10 * * * *'  # Every 10 minutes
```

## Security

- Never commit `.env` file with credentials
- Use GitHub Secrets for sensitive data
- Credentials are not logged
- Downloaded files are cleaned up after processing

## License

MIT
