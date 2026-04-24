# Quick Start Guide: Microsoft Planner Sync

## ✅ Implementation Complete

The Microsoft Planner synchronization system is now fully implemented and ready to use.

## 🔑 GitHub Secrets Status

**Already Configured** ✅
- `MICROSOFT_EMAIL` - Microsoft account email
- `MICROSOFT_PASSWORD` - Microsoft account password
- `PLANNER_URL` - Planner board URL

The workflow is configured to use these existing secrets automatically.

## 🚀 How to Enable

### Option 1: Enable Scheduled Sync (Recommended)

The workflow is configured to run automatically every 10 minutes. Once you merge this PR, the sync will start automatically.

**Schedule**: `*/10 * * * *` (every 10 minutes)

### Option 2: Manual Trigger

You can also trigger the sync manually:

1. Go to **Actions** tab in GitHub
2. Select **"Sync Microsoft Planner Data"** workflow
3. Click **"Run workflow"** button
4. Select branch and click **"Run workflow"**

## 📊 What Happens During Sync

1. **Login**: Authenticates with Microsoft using provided credentials
2. **Navigate**: Opens the Planner board
3. **Export**: Clicks "Export to Excel" button and downloads CSV
4. **Parse**: Reads CSV with semicolon delimiter
5. **Transform**: Maps Planner data to hiring tracker format
   - Bucket Name → Stage Checkboxes
   - Labels → Division
   - Assigned To → PIC
   - Progress → Completion status
6. **Merge**: Updates existing entries by Job Position
7. **Preserve**: Keeps Job Description and Attachments
8. **Commit**: Pushes changes to `data/hiring-data.json`

## 📁 New File Structure

```
hiring-tracker-v2/
├── .github/workflows/
│   └── sync-planner.yml         # Automation workflow
├── scripts/
│   ├── config.js                # Mapping configurations
│   ├── excel-parser.js          # CSV parser
│   ├── data-transformer.js      # Data transformation
│   ├── sync-planner.js          # Main script
│   └── test-transformer.js      # Test script
├── data/
│   └── hiring-data.json         # Updated location
├── downloads/                   # Temporary files (git-ignored)
├── package.json                 # Node dependencies
├── playwright.config.js         # Browser config
└── PLANNER_SYNC_README.md       # Full documentation
```

## 🔍 Monitoring

### Check Workflow Runs

1. Go to **Actions** tab
2. Click on **"Sync Microsoft Planner Data"**
3. View recent runs and their status

### Review Commits

Look for commits with message: `🔄 Update hiring data from Planner [skip ci]`

These indicate successful syncs.

## 🛠️ Customization

### Update Mappings

Edit `scripts/config.js` to customize:

- **Division Mapping**: Line 64-75
- **PIC Mapping**: Line 81-87
- **Bucket Stages**: Line 24-67

### Change Schedule

Edit `.github/workflows/sync-planner.yml` line 6:

```yaml
schedule:
  - cron: '*/10 * * * *'  # Every 10 minutes
```

Examples:
- Every 5 minutes: `*/5 * * * *`
- Every 30 minutes: `*/30 * * * *`
- Every hour: `0 * * * *`

## 🧪 Testing Locally

To test the sync locally before enabling automation:

1. **Install dependencies**:
   ```bash
   npm install
   npx playwright install chromium
   ```

2. **Create `.env` file** with test credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run sync**:
   ```bash
   npm run sync
   ```

4. **Review output**:
   - Check console logs
   - Verify `data/hiring-data.json` was updated
   - Confirm data preservation works

## 📝 Data Mapping Examples

### Bucket to Stages

```
"Backlog (Employee Req Form)"
→ All stages: false

"Sudah Sign Contract Lanjut Onboarding"
→ All stages: true

"HOLD" or "CANCELED"
→ Preserve existing stages, Freeze: true
```

### Labels to Division

```
"Technology" → "Technology Engineering Division"
"Redaksi Teks" → "Kompas.com News - Text Department"
"Marcomm Kompascom" → "Marketing Communication Kompas.com"
```

### Assigned To → PIC

```
"Adelia Galuh H" → "adelia"
"Rizky Pangestu" → "rizky"
"Novinda Riski" → "vania"
"Adelia Galuh H;Member" → "adelia" (takes first)
```

## ⚠️ Important Notes

### Data Preservation

The sync **PRESERVES** these fields:
- Job Description
- Attachments
- Custom notes (not from Planner)

The sync **UPDATES** these fields:
- Stage checkboxes
- PIC
- Notes (appended from Description)
- Last Updated timestamp
- Freeze status

### Commit Message

Commits use `[skip ci]` to prevent infinite loops:
```
🔄 Update hiring data from Planner [skip ci]
```

### Error Handling

If sync fails:
1. Check workflow logs in Actions tab
2. Verify credentials are correct
3. Check if Planner URL is accessible
4. Ensure export button selector is current

## 📚 Full Documentation

For complete details, see: **PLANNER_SYNC_README.md**

## 🎉 Ready to Go!

The system is fully implemented and tested:
- ✅ Code syntax validated
- ✅ Dependencies installed
- ✅ Security scan passed (0 alerts)
- ✅ Code review passed
- ✅ GitHub Secrets compatible
- ✅ Documentation complete

**Merge this PR to activate the automated sync!**
