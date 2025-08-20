INTERVIEW_QUESTIONS = {
    "AI/ML Engineer": [
        "What is the difference between supervised and unsupervised learning?",
        "Explain how backpropagation works in neural networks.",
        "What are activation functions, and why are they important?",
        "How would you handle missing data in a dataset?",
        "Explain the bias-variance tradeoff."
    ],
    "Product Manager": [
        "How do you prioritize features in a product roadmap?",
        "Describe a time you had to say no to a feature request.",
        "How do you measure product success?",
        "Explain your approach to user research.",
        "How do you handle conflicts between engineering and design teams?"
    ],
    "Software Engineer": [
        "Explain the SOLID principles of object-oriented design.",
        "How would you optimize a slow-performing database query?",
        "Describe your experience with version control systems.",
        "What's your approach to debugging complex issues?",
        "How do you ensure code quality in your projects?"
    ],
    "Data Scientist": [
        "How would you explain a linear regression model to a non-technical stakeholder?",
        "What's your approach to feature selection for a new project?",
        "How do you evaluate model performance beyond accuracy?",
        "Describe your experience with A/B testing.",
        "How would you handle an imbalanced dataset?"
    ],
    "UI/UX Designer": [
        "Walk us through your design process from start to finish.",
        "How do you approach user research and testing?",
        "What tools do you use for prototyping and why?",
        "How do you measure the success of a design?",
        "How do you handle feedback from stakeholders that contradicts user research?"
    ]
}

def get_questions_for_job(job_title):
    """Get questions for specific job title with fallback"""
    default_questions = [
        "Tell me about yourself",
        "What interests you about this position?",
        "What are your strengths and weaknesses?",
        "Describe a challenging project you worked on",
        "Where do you see yourself in 5 years?"
    ]
    
    return INTERVIEW_QUESTIONS.get(job_title, default_questions)