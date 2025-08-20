def analyze_projects(parsed_cv):
    # Dummy: Real case would use NLP
    projects = []
    if "ai" in parsed_cv.get("skills", []):
        projects.append("AI-based Project Detection")
    if "data" in parsed_cv.get("skills", []):
        projects.append("Data Analysis Tool")
    return projects
