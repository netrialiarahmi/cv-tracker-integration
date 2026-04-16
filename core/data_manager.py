"""
Data persistence management for credentials and hiring data.
Handles loading, saving, and GitHub fallback for data files.
"""

import json
import os
import pandas as pd
import requests
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
from config.settings import (
    CREDENTIALS_FILE, HIRING_DATA_FILE, DEFAULT_CREDENTIALS,
    BASE_STAGES,
    GITHUB_BACKUP_REPO, GITHUB_BACKUP_BRANCH, GITHUB_BACKUP_ENABLED
)


def backup_credentials_to_github(credentials: Dict[str, str]) -> bool:
    """
    Backup credentials.json to GitHub repository using GitHub API.
    Requires GITHUB_TOKEN environment variable to be set.
    
    Args:
        credentials: Dictionary mapping division names to passwords to backup
        
    Returns:
        True if backup succeeded, False otherwise
    """
    if not GITHUB_BACKUP_ENABLED:
        return False
    
    try:
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("GitHub token not found in environment variables")
            return False
        
        # Prepare the file content
        file_content = json.dumps(credentials, indent=4)
        encoded_content = base64.b64encode(file_content.encode()).decode()
        
        # Get current file SHA if it exists
        api_url = f"https://api.github.com/repos/{GITHUB_BACKUP_REPO}/contents/{CREDENTIALS_FILE}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Try to get existing file SHA
        sha = None
        try:
            response = requests.get(api_url, headers=headers, params={"ref": GITHUB_BACKUP_BRANCH}, timeout=10)
            if response.status_code == 200:
                sha = response.json().get('sha')
        except Exception:
            pass  # File might not exist yet
        
        # Prepare commit data
        commit_data = {
            "message": f"Auto-backup: Update credentials.json - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "content": encoded_content,
            "branch": GITHUB_BACKUP_BRANCH
        }
        
        if sha:
            commit_data["sha"] = sha
        
        # Push to GitHub
        response = requests.put(api_url, headers=headers, json=commit_data, timeout=30)
        
        if response.status_code in [200, 201]:
            print(f"Successfully backed up credentials.json to GitHub")
            return True
        else:
            print(f"Failed to backup credentials to GitHub: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error backing up credentials to GitHub: {e}")
        return False


def save_credentials(credentials: Dict[str, str]) -> None:
    """
    Save credentials to JSON file and backup to GitHub.
    
    Args:
        credentials: Dictionary mapping division names to passwords
    """
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f, indent=4)
    
    # Auto-backup to GitHub if enabled
    backup_credentials_to_github(credentials)


def load_credentials() -> Dict[str, str]:
    """
    Load credentials from JSON file or return defaults.
    
    Returns:
        Dictionary mapping division names to passwords
    """
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    else:
        save_credentials(DEFAULT_CREDENTIALS)
        return DEFAULT_CREDENTIALS


def load_hiring_data_from_github() -> List[Dict[str, Any]]:
    """
    Fetch hiring_data.json from GitHub repository as fallback.
    Uses the backup repository and branch configured for data backup.
    
    Returns:
        List of hiring data dictionaries, or empty list if fetch fails
    """
    try:
        github_url = f"https://raw.githubusercontent.com/{GITHUB_BACKUP_REPO}/{GITHUB_BACKUP_BRANCH}/{HIRING_DATA_FILE}"
        response = requests.get(github_url, timeout=10)
        
        if response.status_code == 200:
            data_dict = json.loads(response.text)
            if data_dict:  # Make sure we got actual data
                print(f"Successfully fetched hiring data from GitHub repo: {GITHUB_BACKUP_REPO}")
                return data_dict
        
        print(f"Could not fetch hiring data from GitHub repo: {GITHUB_BACKUP_REPO}")
        return []
    except Exception as e:
        print(f"Failed to fetch from GitHub: {e}")
        return []


def backup_hiring_data_to_github(data_dict: List[Dict[str, Any]]) -> bool:
    """
    Backup hiring_data.json to GitHub repository using GitHub API.
    Requires GITHUB_TOKEN environment variable to be set.
    
    Args:
        data_dict: List of hiring data dictionaries to backup
        
    Returns:
        True if backup succeeded, False otherwise
    """
    if not GITHUB_BACKUP_ENABLED:
        return False
    
    try:
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("GitHub token not found in environment variables")
            return False
        
        # Prepare the file content
        file_content = json.dumps(data_dict, indent=4)
        encoded_content = base64.b64encode(file_content.encode()).decode()
        
        # Get current file SHA if it exists
        api_url = f"https://api.github.com/repos/{GITHUB_BACKUP_REPO}/contents/{HIRING_DATA_FILE}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Try to get existing file SHA
        sha = None
        try:
            response = requests.get(api_url, headers=headers, params={"ref": GITHUB_BACKUP_BRANCH}, timeout=10)
            if response.status_code == 200:
                sha = response.json().get('sha')
        except Exception:
            pass  # File might not exist yet
        
        # Prepare commit data
        commit_data = {
            "message": f"Auto-backup: Update hiring_data.json - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "content": encoded_content,
            "branch": GITHUB_BACKUP_BRANCH
        }
        
        if sha:
            commit_data["sha"] = sha
        
        # Push to GitHub
        response = requests.put(api_url, headers=headers, json=commit_data, timeout=30)
        
        if response.status_code in [200, 201]:
            print(f"Successfully backed up hiring_data.json to GitHub")
            return True
        else:
            print(f"Failed to backup to GitHub: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error backing up to GitHub: {e}")
        return False


def save_hiring_data(data: pd.DataFrame) -> None:
    """
    Save hiring data DataFrame to JSON file and backup to GitHub.
    Maintains backward compatibility by converting column names back to original format.
    
    Args:
        data: DataFrame containing hiring data
    """
    # Make a copy to avoid modifying the original DataFrame
    data_copy = data.copy()
    
    if "PIC" not in data_copy.columns:
        data_copy["PIC"] = ""
    if "Freeze" not in data_copy.columns:
        data_copy["Freeze"] = False
    
    # Reverse the migration: convert "Initial Interview (HR)" back to "Initial screening"
    # for backward compatibility with existing data format
    if "Initial Interview (HR)" in data_copy.columns:
        data_copy.rename(columns={"Initial Interview (HR)": "Initial screening"}, inplace=True)
    
    data_dict = data_copy.to_dict('records')
    with open(HIRING_DATA_FILE, "w") as f:
        json.dump(data_dict, f, indent=4)
    
    # Auto-backup to GitHub if enabled
    backup_hiring_data_to_github(data_dict)


def load_hiring_data() -> pd.DataFrame:
    """
    Load hiring data from JSON file with GitHub fallback.
    Performs data migration and ensures all required columns exist.
    
    Returns:
        DataFrame containing hiring data with all required columns
    """
    if os.path.exists(HIRING_DATA_FILE):
        try:
            with open(HIRING_DATA_FILE, "r") as f:
                content = f.read().strip()
                # Handle empty file - try to fetch from GitHub
                if not content:
                    print("Local hiring_data.json is empty, fetching from GitHub...")
                    data_dict = load_hiring_data_from_github()
                    if data_dict:
                        # Save the fetched data locally for future use
                        with open(HIRING_DATA_FILE, "w") as f:
                            json.dump(data_dict, f, indent=4)
                else:
                    data_dict = json.loads(content)
                
                df = pd.DataFrame(data_dict)
                
                # Data migration: rename "Initial screening" to "Initial Interview (HR)"
                if "Initial screening" in df.columns and "Initial Interview (HR)" not in df.columns:
                    df.rename(columns={"Initial screening": "Initial Interview (HR)"}, inplace=True)
                
                if "PIC" not in df.columns:
                    df["PIC"] = ""
                if "Last Updated" not in df.columns:
                    df["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                expected_columns = [
                    "Division", "Job Position", "Initial Interview (HR)",
                    "HR & User Interview (Stage 1)", "Skill Test", "Final Interview",
                    "Offering", "Contract Sign", "On Boarding",
                    "PIC", "Notes", "Last Updated", "Has Skill Test",
                    "Hire Type", "Replacement For", "Job Description", "Freeze",
                    "CV Matching Position"
                ]
                for col in expected_columns:
                    if col not in df.columns:
                        if col in ["Initial Interview (HR)", "HR & User Interview (Stage 1)", 
                                  "Skill Test", "Final Interview", "Offering", 
                                  "Contract Sign", "On Boarding", "Has Skill Test", "Freeze"]:
                            df[col] = False  # Boolean for checkbox stages
                        else:
                            df[col] = ""
                
                # Ensure Attachments column exists (as list for each entry)
                if "Attachments" not in df.columns:
                    df["Attachments"] = [[] for _ in range(len(df))]
                return df
        except (json.JSONDecodeError, ValueError) as e:
            # If JSON is invalid or empty, try fetching from GitHub
            print(f"Error parsing local file: {e}, fetching from GitHub...")
            data_dict = load_hiring_data_from_github()
            if data_dict:
                df = pd.DataFrame(data_dict)
                # Save the fetched data locally for future use
                try:
                    with open(HIRING_DATA_FILE, "w") as f:
                        json.dump(data_dict, f, indent=4)
                except Exception:
                    pass  # If we can't write, continue anyway
                # Add any missing columns
                if "Hire Type" not in df.columns:
                    df["Hire Type"] = "Additional"
                if "Replacement For" not in df.columns:
                    df["Replacement For"] = ""
                if "Job Description" not in df.columns:
                    df["Job Description"] = ""
                if "Freeze" not in df.columns:
                    df["Freeze"] = False
                if "Attachments" not in df.columns:
                    df["Attachments"] = [[] for _ in range(len(df))]
                return df
    else:
        # File doesn't exist, try fetching from GitHub
        print("hiring_data.json not found locally, fetching from GitHub...")
        data_dict = load_hiring_data_from_github()
        if data_dict:
            # Try to save locally
            try:
                with open(HIRING_DATA_FILE, "w") as f:
                    json.dump(data_dict, f, indent=4)
            except Exception:
                pass  # If we can't write, continue anyway
            df = pd.DataFrame(data_dict)
            # Add any missing columns
            if "PIC" not in df.columns:
                df["PIC"] = ""
            if "Last Updated" not in df.columns:
                df["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if "Hire Type" not in df.columns:
                df["Hire Type"] = "Additional"
            if "Replacement For" not in df.columns:
                df["Replacement For"] = ""
            if "Job Description" not in df.columns:
                df["Job Description"] = ""
            if "Freeze" not in df.columns:
                df["Freeze"] = False
            if "Freeze" not in df.columns:
                df["Freeze"] = False
            if "Attachments" not in df.columns:
                df["Attachments"] = [[] for _ in range(len(df))]
            return df
    
    # Return empty DataFrame if all else fails
    return pd.DataFrame({
        "Division": [], "Job Position": [], "Initial Interview (HR)": [],
        "HR & User Interview (Stage 1)": [], 
        "Skill Test": [], "Final Interview": [],
        "Offering": [], "Contract Sign": [], "On Boarding": [],
        "PIC": [], "Notes": [], "Last Updated": [], "Has Skill Test": [],
        "Hire Type": [], "Replacement For": [], "Job Description": [], "Freeze": [],
        "Attachments": [], "CV Matching Position": []
    })
