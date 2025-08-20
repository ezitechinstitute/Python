from fastapi import FastAPI, Request, Form, Response, status, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from routes.resume import router as resume_router
from routes.interview import router as interview_router
from routes.video_emotion import router as video_emotion_router
from routes.video_interview import router as video_router
from routes import feedback
from routes.admin import router as admin_router
from routes import contact
from routes import admin_logs
from routes.voice import router as voice_router
import fitz  # PyMuPDF
import uuid
import os
import csv
from io import StringIO
import shutil
from utils.auth import verify_login
from utils.resume_parser import extract_text_from_pdf, parse_resume, extract_text_from_docx
from utils.gemini_utils import generate_questions_with_gemini
from utils.question_generator import generate_questions_from_resume

# Create DB tables after import
router = APIRouter()

app = FastAPI(title="Smart Interview Bot")
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

# Enable CORS for frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Basic routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/resume", response_class=HTMLResponse)
async def resume(request: Request):
    return templates.TemplateResponse("resume.html", {"request": request})

@app.get("/questions", response_class=HTMLResponse)
async def questions(request: Request):
    return templates.TemplateResponse("questions.html", {"request": request})

@app.get("/emotion", response_class=HTMLResponse)
async def emotion(request: Request):
    return templates.TemplateResponse("emotion.html", {"request": request})

# Register your routes
app.include_router(resume_router, prefix="/resume", tags=["Resume"])
app.include_router(interview_router, prefix="/interview", tags=["Interview"])
app.include_router(video_emotion_router, prefix="/emotion")
app.include_router(video_router)
app.include_router(feedback.router)
app.include_router(admin_router)
app.include_router(contact.router)
app.include_router(voice_router, prefix="/voice")
app.include_router(admin_logs.router)

# Include the local router that defines /questions/generate and /resume/upload
app.include_router(router)

# Resume processing endpoints
@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="Only PDF/DOCX files are allowed.")
        
        os.makedirs("uploads", exist_ok=True)
        file_location = f"uploads/{file.filename}"
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"message": "Resume uploaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload resume: {str(e)}")

# Question generation endpoints@router.post("/questions/generate")
async def generate_questions_from_resume_endpoint(
    resume: UploadFile = File(None),  # Make resume optional
    job_title: str = Form(...),
    language: str = Form("en"),
    experience_level: str = Form("mid"),
    count: int = Form(10)
):
    try:
        # If no resume uploaded, generate generic questions
        if not resume:
            questions = generate_questions_from_resume(
                job_title=job_title,
                language=language,
                experience_level=experience_level,
                count=count
            )
            return {"questions": questions}
        
        # Save temporary file
        os.makedirs("temp_files", exist_ok=True)
        temp_path = f"temp_files/{resume.filename}"
        with open(temp_path, "wb") as f:
            f.write(await resume.read())
        
        # Extract text based on file type
        if resume.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(temp_path)
        elif resume.filename.lower().endswith('.docx'):
            text = extract_text_from_docx(temp_path)
        else:
            raise HTTPException(400, "Only PDF/DOCX files supported")
        
        # Generate questions
        questions = generate_questions_from_resume(
            job_title=job_title,
            language=language,
            experience_level=experience_level,
            count=count
        )
        
        # Clean up
        os.remove(temp_path)
        
        return {"questions": questions}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to generate questions: {str(e)}")

@router.get("/interview/questions")
async def get_interview_questions(
    job_title: str,
    language: str = "en",
    experience_level: str = "mid",
    count: int = 10
):
    try:
        questions = generate_questions_from_resume(
            job_title=job_title,
            language=language,
            experience_level=experience_level,
            count=count
        )
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(500, f"Failed to generate questions: {str(e)}")

# Admin routes
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_form(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})

@app.post("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if verify_login(username, password):
        request.session["is_admin"] = True
        return RedirectResponse("/admin", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("admin_login.html", {
        "request": request, "error": "Invalid credentials"
    })

@app.get("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=status.HTTP_302_FOUND)

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    # Dummy chart values (replace with DB queries as needed)
    resume_counts = {"uploaded": 15, "not_uploaded": 5}
    interview_counts = {"taken": 10, "pending": 10}
    emotion_counts = {
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "values": [3, 4, 5, 2, 6]
    }

    users = [
        {"name": "Ali", "email": "ali@example.com", "resume": "Yes", "interview": "Yes", "last_active": "2025-06-13"},
        {"name": "Sara", "email": "sara@example.com", "resume": "No", "interview": "No", "last_active": "2025-06-12"},
    ]

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "users": users,
        "resume_counts": resume_counts,
        "interview_counts": interview_counts,
        "emotion_counts": emotion_counts
    })

@router.get("/admin/download-csv")
def download_csv():
    data = [
        {"Name": "Ali", "Email": "ali@example.com", "Resume": "Yes", "Interview": "Yes", "Last Active": "2025-06-13"},
        {"Name": "Sara", "Email": "sara@example.com", "Resume": "No", "Interview": "No", "Last Active": "2025-06-12"},
    ]

    def generate_csv():
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        output.seek(0)
        return output

    return StreamingResponse(generate_csv(), media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=admin_data.csv"
    })

# Additional routes
@app.get("/live", response_class=HTMLResponse)
async def live_interview_page(request: Request):
    return templates.TemplateResponse("live_interview.html", {"request": request})


@router.get("/questions")
async def get_questions(job_title: str):
    questions = generate_questions_with_gemini(job_title)
    return {"questions": questions}

# Register the local APIRouter for extra endpoints at the bottom
app.include_router(router)

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@router.get("/admin/login", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Define admin credentials (replace with secure method in production)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

@router.post("/admin/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin/dashboard", status_code=302)
        response.set_cookie(key="admin_logged_in", value="true")
        return response
    return RedirectResponse(url="/admin/login", status_code=302)

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    if request.cookies.get("admin_logged_in") != "true":
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/admin/logout")
async def logout():
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("admin_logged_in")
    return response

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

from fastapi import APIRouter, UploadFile, File
import os

router = APIRouter()

UPLOAD_DIR = "temp_files"  # Make sure this folder exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        if file.filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(file_location)
        else:
            return {"error": "Only PDF files supported currently."}

        parsed = parse_resume(resume_text)
        return {
            "message": "Resume parsed successfully.",
            "data": parsed
        }

    except Exception as e:
        return {"error": str(e)}

from routes import resume  # if file is routes/resume.py

app.include_router(resume.router)
from routes import interview

app.include_router(interview.router)
@app.get("/live", response_class=HTMLResponse)
async def live_interview_page(request: Request):
    return templates.TemplateResponse("live_interview.html", {"request": request})
@app.get("/questions")
async def get_questions(job_title: str):
    questions = generate_questions_with_gemini(job_title)
    return {"questions": questions}
# Add this to your main.py
INTERNSHIP_FIELDS = {
    "AI/ML Engineer": {
        "description": "Artificial Intelligence and Machine Learning",
        "experience_levels": ["entry", "mid", "senior"],
        "skills": ["Python", "TensorFlow", "PyTorch", "scikit-learn", "NLP", "Computer Vision"]
    },
    "Web Development": {
        "description": "Frontend and Backend Web Development",
        "experience_levels": ["entry", "mid"],
        "skills": ["HTML/CSS", "JavaScript", "React", "Node.js", "Django", "Flask"]
    },
    "Mobile App Development": {
        "description": "iOS and Android App Development",
        "experience_levels": ["entry", "mid"],
        "skills": ["Flutter", "React Native", "Swift", "Kotlin", "Android Studio", "Xcode"]
    },
    "DevOps Engineering": {
        "description": "CI/CD Pipelines and Cloud Infrastructure",
        "experience_levels": ["mid", "senior"],
        "skills": ["Docker", "Kubernetes", "AWS", "Azure", "Terraform", "Jenkins"]
    },
    "Data Science": {
        "description": "Data Analysis and Predictive Modeling",
        "experience_levels": ["entry", "mid", "senior"],
        "skills": ["Python", "Pandas", "NumPy", "SQL", "Tableau", "Power BI"]
    },
    "Blockchain Development": {
        "description": "Smart Contracts and DApps",
        "experience_levels": ["entry", "mid"],
        "skills": ["Solidity", "Ethereum", "Web3.js", "Smart Contracts", "Truffle"]
    },
    "UI/UX Design": {
        "description": "User Interface and Experience Design",
        "experience_levels": ["entry", "mid"],
        "skills": ["Figma", "Adobe XD", "Sketch", "User Research", "Wireframing", "Prototyping"]
    },
    "Quality Assurance": {
        "description": "Software Testing and Quality Control",
        "experience_levels": ["entry", "mid"],
        "skills": ["Selenium", "JUnit", "TestNG", "Cypress", "JMeter", "Postman"]
    },
    "Cloud Computing": {
        "description": "Cloud Infrastructure and Services",
        "experience_levels": ["entry", "mid", "senior"],
        "skills": ["AWS", "Azure", "GCP", "Serverless", "Lambda", "EC2"]
    },
    "Cyber Security": {
        "description": "Information Security and Ethical Hacking",
        "experience_levels": ["mid", "senior"],
        "skills": ["Penetration Testing", "OWASP", "Kali Linux", "SIEM", "Firewalls", "Encryption"]
    }
}

@router.get("/internship/fields")
async def get_internship_fields():
    return {
        "fields": list(INTERNSHIP_FIELDS.keys()),
        "descriptions": {k: v["description"] for k, v in INTERNSHIP_FIELDS.items()}
    }