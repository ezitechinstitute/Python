# utils/feedback_generator.py

def generate_feedback(resume_text, responses, emotions):
    feedback = []
    job_recommendation = "General Internship"

    # Resume Analysis
    if 'machine learning' in resume_text.lower():
        job_recommendation = "ML Intern"
    elif 'data analysis' in resume_text.lower():
        job_recommendation = "Data Analyst"
    elif 'web development' in resume_text.lower():
        job_recommendation = "Frontend Developer Intern"
    
    # Confidence from emotions
    neutral_count = sum(1 for e in emotions if e['emotion'] == 'neutral')
    happy_count = sum(1 for e in emotions if e['emotion'] == 'happy')
    sad_count = sum(1 for e in emotions if e['emotion'] == 'sad')

    if sad_count > happy_count:
        feedback.append("Try to stay more confident during the interview.")
    elif happy_count > sad_count:
        feedback.append("Great job staying positive and confident.")

    if neutral_count > len(emotions) * 0.7:
        feedback.append("You maintained calm and focus throughout.")

    # Answer Analysis (basic)
    for item in responses:
        if len(item['answer'].split()) < 5:
            feedback.append(f"Your answer to '{item['question']}' was too short. Try elaborating more.")

    return {
        "recommendation": job_recommendation,
        "feedback": feedback
    }
 