import os
import requests
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

headers = {
    "Authorization": f"token {os.environ.get('GITHUB_TOKEN')}",
    "Accept": "application/vnd.github.v3.raw"
}
raw_url = "https://raw.githubusercontent.com/netrialiarahmi/cv-matching-auto/main/data/job_positions.csv"
response = requests.get(raw_url, headers=headers)
if response.status_code == 200:
    df = pd.read_csv(StringIO(response.text))
    
    for _, row in df.iterrows():
        if "VCBL" in row['Job Position']:
            print(f"Position: {row['Job Position']}")
            print(f"Description: {repr(row['Job Description'])}")
            print("---")
            
