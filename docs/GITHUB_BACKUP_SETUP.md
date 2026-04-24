# GitHub Auto-Backup Setup Guide

This document explains how to set up the GitHub auto-backup feature for the Hiring Tracker application.

## Overview

The application automatically backs up `hiring_data.json` to your GitHub repository whenever changes are saved. This provides redundancy and allows you to track the history of your hiring data.

## Prerequisites

1. A GitHub account
2. A GitHub Personal Access Token with repository write permissions

## Creating a GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token" → "Generate new token (classic)"
3. Give your token a descriptive name (e.g., "Hiring Tracker Backup")
4. Set expiration (recommended: 90 days or "No expiration" for production)
5. Select the following scopes:
   - ✅ `repo` (Full control of private repositories)
6. Click "Generate token"
7. **Important**: Copy your token immediately! You won't be able to see it again.

## Setting Up the Token

### For Local Development

Set the token as an environment variable:

**Linux/Mac:**
```bash
export GITHUB_TOKEN=your_token_here
```

**Windows (CMD):**
```cmd
set GITHUB_TOKEN=your_token_here
```

**Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN="your_token_here"
```

### For Streamlit Cloud

1. Go to your app settings in Streamlit Cloud
2. Navigate to "Secrets"
3. Add the following to your secrets:
```toml
GITHUB_TOKEN = "your_token_here"
```

### For Other Deployment Platforms

#### Heroku
```bash
heroku config:set GITHUB_TOKEN=your_token_here
```

#### Railway
Add environment variable in the Variables section of your project settings.

#### Docker
```dockerfile
ENV GITHUB_TOKEN=your_token_here
```

Or pass it when running the container:
```bash
docker run -e GITHUB_TOKEN=your_token_here your-image
```

## Configuration

The backup feature can be configured in `config/settings.py`:

```python
# GitHub repository settings for auto-backup
GITHUB_BACKUP_REPO = "netrialiarahmi/hiring-tracker-v2"  # Your repository
GITHUB_BACKUP_BRANCH = "main"                             # Target branch
GITHUB_BACKUP_ENABLED = True                              # Enable/disable
```

### To Disable Auto-Backup

Set `GITHUB_BACKUP_ENABLED = False` in `config/settings.py`:

```python
GITHUB_BACKUP_ENABLED = False  # Disable GitHub auto-backup
```

## How It Works

When you save changes to hiring data:

1. The data is saved locally to `hiring_data.json`
2. If `GITHUB_TOKEN` is available and backup is enabled:
   - The data is encoded and prepared for GitHub API
   - The function checks if the file already exists in the repository
   - A commit is created with a timestamp (e.g., "Auto-backup: Update hiring_data.json - 2025-11-11 17:30:00")
   - The file is pushed to your GitHub repository

## Troubleshooting

### "GitHub token not found in environment variables"
- Make sure you've set the `GITHUB_TOKEN` environment variable correctly
- Restart your application after setting the environment variable

### "Failed to backup to GitHub: 401"
- Your token may be invalid or expired
- Generate a new token and update the environment variable

### "Failed to backup to GitHub: 403"
- Your token doesn't have the required permissions
- Generate a new token with `repo` scope

### "Failed to backup to GitHub: 404"
- Check that `GITHUB_BACKUP_REPO` in `config/settings.py` is correct
- Ensure the repository exists and you have access to it

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit your token to the repository**
   - Always use environment variables
   - Keep tokens out of configuration files

2. **Use tokens with minimal required permissions**
   - Only grant `repo` scope for private repositories
   - For public repos, `public_repo` scope is sufficient

3. **Rotate tokens regularly**
   - Set expiration dates on tokens
   - Update tokens periodically

4. **Revoke compromised tokens immediately**
   - Go to GitHub Settings → Personal access tokens
   - Click "Revoke" on the compromised token
   - Generate a new one

## Verifying the Setup

To verify that auto-backup is working:

1. Start the application
2. Make a change to hiring data (e.g., add a note to a position)
3. Save the changes
4. Check your GitHub repository for a new commit with message "Auto-backup: Update hiring_data.json - [timestamp]"

If you don't see the commit:
- Check the application logs for error messages
- Verify your token has the correct permissions
- Ensure `GITHUB_BACKUP_ENABLED = True` in settings

## Manual Backup

If you prefer not to use auto-backup, you can manually commit `hiring_data.json` to your repository:

```bash
git add hiring_data.json
git commit -m "Manual backup of hiring data"
git push
```

Note: By default, `hiring_data.json` is in `.gitignore`, so you'll need to force add it:
```bash
git add -f hiring_data.json
```
