import re

jd_vcbl = """MUST 1–3 years of experience as an Account Executive, preferably from Online Media/know basic programmatic
Experience in seek new prospective clients
Have good networking track with direct client/advertising agency is a plus
Have great communication, interpersonal & presentation skills
Understand the newest advertising industry, digital programmatic ads & digital media trends
Candidates with knowledge or experience in programmatic ads and programmatic sales are preferred."""

jd_pasangiklan = """Minimum Qualifications
1. TOTAL EXPERIENCE less then 2 year is A MUST, excluding internship.
2. MUST 1-2 year experience as sales/Account Executive because the higher exprience, higher their cost. 
3. Bachelor's degree from any discipline
4. MUST have experience in canvassing
5. Have achieved sales target beyond 90%
6. Having the capability to build good networking
7. Ability to multitask and work efficiently and effectively to meet required deadlines
7.  Acquiring and managing accounts

Job Description:
- Canvasing for SME clients & maintain existing clients
- Making strategy to achieve revenue target
- Doing coordination for client's ad & events
- Reporting for client's campaign
- Weekly reporting for sales pipeline & target"""

def extract_tech_skills(jd_text):
    if not jd_text:
        return []
    
    # Split by newlines
    lines = jd_text.split('\n')
    skills = []
    
    # Look for bullet points or numbered lists or just plain lines
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Skip headers
        if "Minimum Qualifications" in line or "Job Description:" in line or "Requirements" in line or "Role Expectations" in line:
            continue
            
        # Clean up bullet points, numbers, and dashes
        line = re.sub(r'^(\d+\.|-|\u2022|\*)\s*', '', line).strip()
        
        if not line: continue
        
        lower = line.lower()
        
        # Exclude patterns
        if "year" in lower and "experience" in lower: continue
        if "degree" in lower: continue
        if "internship" in lower: continue
        if "month" in lower and "experience" in lower: continue
        
        # Clean up trailing periods
        line = line.rstrip('.').strip()
        
        # Capitalize first letter
        if line:
            line = line[0].upper() + line[1:]
            skills.append(line)
            
    # Remove duplicates preserving order, limit to 10
    return list(dict.fromkeys(skills))[:15]

print("VCBL:")
for s in extract_tech_skills(jd_vcbl): print("-", s)

print("\nPasangiklan:")
for s in extract_tech_skills(jd_pasangiklan): print("-", s)
