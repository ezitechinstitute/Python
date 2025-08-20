def recommend_roles(projects):
    roles = []
    for project in projects:
        if "AI" in project:
            roles.append("AI Intern")
        elif "Data" in project:
            roles.append("Data Science Intern")
    return list(set(roles))  # Unique