import re

jd = """Minimum Qualifications
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
    
    lines = jd_text.split('\n')
    skills = []
    
    # Simple heuristics
    for line in lines:
        line = line.strip()
        if not line: continue
        
        lower = line.lower()
        if "experience in" in lower:
            skill = lower.split("experience in")[1].strip().strip(".-;")
            if skill: skills.append(skill.title())
        elif "capability to" in lower:
            skill = lower.split("capability to")[1].strip().strip(".-;")
            if skill: skills.append(skill.title())
        elif "achieved" in lower or "achieve" in lower:
            if "target" in lower:
                skills.append("Sales Target Achievement")
        elif "canvassing" in lower or "canvasing" in lower:
            if "Canvassing" not in skills:
                skills.append("Canvassing")
        elif "networking" in lower:
            skills.append("Networking")
        
    return list(dict.fromkeys(skills))[:4] # Unique and max 4

print(extract_tech_skills(jd))
