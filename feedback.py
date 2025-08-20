# routes/feedback.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from utils.feedback_generator import generate_feedback
from utils.parser import parsed_resume_data
from utils.exporter import export_to_json, export_to_pdf
import json
import os

router = APIRouter()

@router.get("/feedback/generate")
def generate_candidate_feedback(candidate_name: str):
    try:
        # Load latest logs
        logs_path = "logs"
        files = sorted(os.listdir(logs_path), reverse=True)

        # Get latest QA log and emotion log
        qa_file = next((f for f in files if f.startswith(f"qa_{candidate_name.replace(' ', '_')}")), None)
        emotion_file = next((f for f in files if f.startswith(f"emotions_{candidate_name.replace(' ', '_')}")), None)

        if not qa_file or not emotion_file:
            raise Exception("Missing logs.")

        with open(os.path.join(logs_path, qa_file)) as f1, open(os.path.join(logs_path, emotion_file)) as f2:
            qa_log = json.load(f1)["qa"]
            emotion_log = json.load(f2)["emotions"]

        result = generate_feedback(parsed_resume_data.get("text", ""), qa_log, emotion_log)

        return {
            "candidate": candidate_name,
            "recommendation": result["recommendation"],
            "feedback": result["feedback"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/export")
def export_summary(candidate_name: str, format: str = "pdf"):
    try:
        from utils.interview_logger import load_log
        data = load_log(candidate_name)
        
        # Assume you already added recommendation and feedback to this log
        if format == "pdf":
            file_path = export_to_pdf(candidate_name, data)
        elif format == "json":
            file_path = export_to_json(candidate_name, data)
        else:
            raise HTTPException(status_code=400, detail="Invalid format")

        return FileResponse(file_path, filename=os.path.basename(file_path))

    except Exception as e:
        print(f"[ERROR] Export failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to export summary.")
