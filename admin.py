from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, HTTPException
import os
import json

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/admin/feedback", response_class=HTMLResponse)
def show_feedback_page(request: Request):
    return templates.TemplateResponse("admin/feedback.html", {"request": request})

@router.get("/admin/resumes", response_class=HTMLResponse)
async def show_uploaded_resumes(request: Request):
    try:
        uploads_file = "data/resume_uploads.json"
        if os.path.exists(uploads_file):
            with open(uploads_file, "r") as f:
                uploads = json.load(f)
        else:
            uploads = []

        return templates.TemplateResponse("admin_resumes.html", {
            "request": request,
            "uploads": uploads
        })

    except Exception as e:
        print(f"[ERROR] Failed to load resume uploads: {e}")
        raise HTTPException(status_code=500, detail="Could not load resume uploads")

