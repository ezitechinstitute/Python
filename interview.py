import os
import json
from datetime import datetime
from fastapi import APIRouter, Query, UploadFile, File, HTTPException, Body
from pydantic import BaseModel
from typing import List
import pdfplumber
from utils import resume_parser
from utils.question_generator import generate_questions_from_resume
from utils.voice_tts import speak_text
from utils.gemini_api import generate_interview_questions, get_feedback
from utils.interview_questions import get_questions_for_job

router = APIRouter()

# Global state for interview session
current_interview = {
    "questions": [],
    "current_index": 0,
    "resume_text": "",
    "candidate_name": "",
    "job_title": ""
}

# ==================== MODELS ====================
class QAItem(BaseModel):
    question: str
    answer: str

class InterviewLog(BaseModel):
    candidate_name: str
    job_title: str
    responses: List[QAItem]
    emotion_scores: List[dict] = []

# ==================== UTILITY FUNCTIONS ====================
def save_interview_log(log_data: dict):
    """Save interview log to JSON file"""
    os.makedirs("logs", exist_ok=True)
    log_file = "logs/interview_logs.json"
    
    try:
        existing_logs = []
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                existing_logs = json.load(f)
                
        existing_logs.append(log_data)
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(existing_logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to save log: {e}")
        raise

# ==================== API ENDPOINTS ====================
@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    candidate_name: str = Body(...),
    job_title: str = Body(...)
):
    """Process uploaded resume and initialize interview"""
    global current_interview
    
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(400, "Only PDF/DOCX files allowed")
    
    os.makedirs("temp_files", exist_ok=True)
    temp_path = f"temp_files/{file.filename}"
    
    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        if file.filename.lower().endswith('.pdf'):
            resume_text = resume_parser.extract_text_from_pdf(temp_path)
        else:
            resume_text = resume_parser.extract_text_from_docx(temp_path)
            
        if not resume_text.strip():
            raise HTTPException(400, "No text could be extracted")
            
        current_interview = {
            "questions": [],
            "current_index": 0,
            "resume_text": resume_text,
            "candidate_name": candidate_name,
            "job_title": job_title
        }
        
        return {"status": "resume_processed"}
        
    except Exception as e:
        raise HTTPException(500, f"Resume processing failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/interview/start")
async def start_interview(
    language: str = Query("en"),
    question_count: int = Query(5)
):
    """Generate and start interview"""
    global current_interview
    
    if not current_interview.get("resume_text"):
        raise HTTPException(400, "No resume processed yet")
    
    try:
        questions = generate_questions_from_resume(
            resume_text=current_interview["resume_text"],
            job_title=current_interview["job_title"],
            language=language,
            count=question_count
        )
        
        if not questions:
            raise HTTPException(400, "Failed to generate questions")
            
        current_interview["questions"] = questions
        current_interview["current_index"] = 0
        
        return {
            "total_questions": len(questions),
            "current_question": questions[0],
            "question_number": 1
        }
        
    except Exception as e:
        raise HTTPException(500, f"Interview start failed: {str(e)}")

@router.get("/get-questions-from-backend")
async def get_questions_from_backend(job_title: str = Query(...)):
    """Get questions from local database"""
    try:
        questions = get_questions_for_job(job_title)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(500, f"Failed to get questions: {str(e)}")

# [Rest of your existing endpoints remain unchanged...]

@router.get("/interview/next")
async def next_question():
    """Get next interview question"""
    global current_interview
    
    questions = current_interview.get("questions", [])
    current_idx = current_interview.get("current_index", 0)
    
    if current_idx >= len(questions) - 1:
        return {"status": "interview_completed"}
    
    current_interview["current_index"] += 1
    
    return {
        "current_question": questions[current_interview["current_index"]],
        "question_number": current_interview["current_index"] + 1,
        "total_questions": len(questions)
    }

@router.post("/interview/speak")
async def speak_question(
    question: str = Body(..., embed=True),
    language: str = Body("en", embed=True)
):
    """Text-to-speech for questions"""
    try:
        if not question.strip():
            raise ValueError("Empty question text")
        
        speak_text(question, lang=language)
        return {"status": "spoken"}
    except Exception as e:
        raise HTTPException(500, f"TTS failed: {str(e)}")

@router.get("/test/voice")
async def test_voice(text: str = Query("Test voice")):
    """Test endpoint for voice functionality"""
    try:
        speak_text(text)
        return {"status": "success"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@router.post("/interview/submit_answer")
async def submit_answer(
    answer: str = Body(...),
    emotion: str = Body(None)
):
    """Save candidate's answer"""
    global current_interview
    
    try:
        current_idx = current_interview["current_index"]
        question = current_interview["questions"][current_idx]
        
        # Save to session
        if "responses" not in current_interview:
            current_interview["responses"] = []
            
        current_interview["responses"].append({
            "question": question,
            "answer": answer,
            "emotion": emotion
        })
        print("[DEBUG] Current interview responses:", current_interview["responses"])  # <-- Add this
        return {"status": "answer_saved"}
    except Exception as e:
        raise HTTPException(500, f"Failed to save answer: {str(e)}")

@router.post("/interview/complete")
async def complete_interview():
    """Finalize and save interview log"""
    global current_interview
    
    try:
        print("[DEBUG] Completing interview. Responses:", current_interview.get("responses"))  # <-- Add this
        if not current_interview.get("responses"):
            raise HTTPException(400, "No interview data to save")
            
        log_data = {
            "candidate_name": current_interview["candidate_name"],
            "job_title": current_interview["job_title"],
            "date": datetime.utcnow().isoformat(),
            "responses": current_interview["responses"]
        }
        
        save_interview_log(log_data)
        return {"status": "interview_saved"}
        
    except Exception as e:
        raise HTTPException(500, f"Failed to complete interview: {str(e)}")

@router.get("/interview/feedback")
async def get_answer_feedback(
    answer: str = Query(...),
    question: str = Query(...)
):
    """Get AI feedback on answer"""
    try:
        feedback = get_feedback(question, answer)
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(500, f"Failed to get feedback: {str(e)}")

# ==================== GEMINI ENDPOINTS ====================
@router.get("/gemini/questions")
def get_gemini_questions(
    job_title: str = Query(...),
    language: str = Query("en")
):
    """Get questions from Gemini"""
    try:
        questions = generate_interview_questions(job_title, language)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(500, str(e))

# ==================== LOGS ====================
@router.get("/interview/logs")
async def get_interview_logs():
    """Get all interview logs"""
    log_file = "logs/interview_logs.json"
    if not os.path.exists(log_file):
        return []
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(500, f"Failed to load logs: {str(e)}")

@router.post("/questions/generate")
async def generate_questions(job_title: str = Body(...), language: str = Body("en")):
    questions = generate_interview_questions(job_title, language)
    return {"questions": questions}