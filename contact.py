from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import json
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/contact/submit")
async def submit_contact(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    try:
        contact_data = {
            "name": name,
            "email": email,
            "message": message
        }

        os.makedirs("data", exist_ok=True)
        file_path = "data/contact_messages.json"

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                messages = json.load(f)
        else:
            messages = []

        messages.append(contact_data)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)

        return {"success": True}
    except Exception as e:
        print(f"[ERROR] Contact form submission failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit message.")

@router.get("/contact/messages")
async def get_all_contact_messages():
    try:
        file_path = "data/contact_messages.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                messages = json.load(f)
        else:
            messages = []

        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to read messages.")

@router.get("/contact", response_class=HTMLResponse)
async def get_contact_form(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@router.get("/admin/contact", response_class=HTMLResponse)
async def show_contact_messages(request: Request):
    try:
        file_path = "data/contact_messages.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                messages = json.load(f)
        else:
            messages = []

        return templates.TemplateResponse("admin_contacts.html", {"request": request, "messages": messages})
    except Exception as e:
        print(f"[ERROR] Failed to load contact messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to load contact messages.")