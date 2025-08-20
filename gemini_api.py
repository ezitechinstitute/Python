import requests

API_KEY = "AIzaSyC_tnA1s6YN7KWASylLWXzeU9PCFuGiVcE"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

headers = {
    "Content-Type": "application/json"
}

def generate_interview_questions(job_title: str, language: str = "en") -> list:
    if language == "ur":
        prompt = f"برائے مہربانی {job_title} کے انٹرویو کے لئے 5 سوالات اردو میں فراہم کریں۔"
    else:
        prompt = f"Please generate 5 interview questions for the job title: {job_title} in English."

    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    response = requests.post(f"{BASE_URL}?key={API_KEY}", headers=headers, json=data)

    try:
        result = response.json()
        text_output = result['candidates'][0]['content']['parts'][0]['text']
        # Split by line and keep only lines that look like questions
        questions = [q.strip("-•1234567890. ").strip() for q in text_output.split("\n") if q.strip() and "?" in q]
        if not questions:
            # fallback: just split all lines
            questions = [q.strip() for q in text_output.split("\n") if q.strip()]
        return questions
    except Exception as e:
        print(f"[Gemini Error - Questions] {e}")
        return ["Error generating questions. Please try again later."]

def get_feedback(answer: str, language: str = "en") -> str:
    if language == "ur":
        prompt = f"مندرجہ ذیل جواب پر اردو میں فیڈبیک فراہم کریں:\n\n{answer}"
    else:
        prompt = f"Please provide feedback in English on the following answer:\n\n{answer}"

    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    response = requests.post(f"{BASE_URL}?key={API_KEY}", headers=headers, json=data)

    try:
        result = response.json()
        feedback = result['candidates'][0]['content']['parts'][0]['text']
        return feedback.strip()
    except Exception as e:
        print(f"[Gemini Error - Feedback] {e}")
        return "Error generating feedback. Please try again later."