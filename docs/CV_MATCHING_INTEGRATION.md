# CV Matching Integration — Feedback Loop

## Overview
The Hiring Tracker V3 pushes user interview feedback to the `cv-matching-auto` repo
via GitHub API, writing JSON files to `feedback/{position_name}.json`.

## What `auto_screen.py` needs to read

Before screening each position, check for a feedback file:

```python
# In screen_position(), after loading job_description:
import json

feedback_path = os.path.join(PROJECT_ROOT, 'feedback', f'{safe_name}.json')
adjusted_description = job_description

# Try local file first, then GitHub
if os.path.isfile(feedback_path):
    with open(feedback_path) as f:
        feedback_data = json.load(f)
    if feedback_data.get('adjusted_requirements'):
        adjusted_description = feedback_data['adjusted_requirements']
        print(f"   📝 Using adjusted requirements (based on {len(feedback_data.get('user_feedback', []))} feedback entries)")
else:
    # Try fetching from GitHub
    try:
        feedback_url = f"https://raw.githubusercontent.com/{repo}/{branch}/feedback/{safe_name}.json"
        resp = requests.get(feedback_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            feedback_data = resp.json()
            if feedback_data.get('adjusted_requirements'):
                adjusted_description = feedback_data['adjusted_requirements']
                print(f"   📝 Using adjusted requirements from GitHub feedback")
    except Exception:
        pass

# Then pass adjusted_description instead of job_description to score_candidate_pipeline()
```

## Feedback JSON format

```json
{
    "position_name": "Account Executive VCBL",
    "division": "Sales Division",
    "original_requirements": "Original job description text...",
    "user_feedback": [
        {
            "author": "Sales Division",
            "division": "Sales Division",
            "candidate_name": "John Doe",
            "action": "reject",
            "text": "Lacks B2B sales experience, only has retail background",
            "timestamp": "2026-04-16 10:30:00"
        },
        {
            "author": "Sales Division",
            "division": "Sales Division",
            "candidate_name": "Jane Smith",
            "action": "approve",
            "text": "Strong digital media sales background, good cultural fit",
            "timestamp": "2026-04-16 11:00:00"
        }
    ],
    "adjusted_requirements": "Original job description...\n\n--- USER INTERVIEW FEEDBACK (Rejection Reasons) ---\nPrevious candidates were rejected for: ...\n\n--- USER INTERVIEW FEEDBACK (Approved Qualities) ---\nPrioritize candidates with: ...",
    "last_updated": "2026-04-16 11:00:00"
}
```

## How adjusted_requirements works

The `adjusted_requirements` field concatenates:
1. Original job description (unchanged)
2. Rejection reasons — "Deprioritize candidates with similar issues"
3. Approved qualities — "Prioritize candidates with similar attributes"
4. General comments — additional hiring manager notes

This gets passed to the Gemini scoring prompt instead of the plain job description,
so the AI naturally adjusts its scoring based on real hiring manager feedback.
