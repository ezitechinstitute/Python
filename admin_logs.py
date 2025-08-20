import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from io import StringIO

router = APIRouter()
templates = Jinja2Templates(directory="templates")

LOG_DIR = "interview_logs"

@router.get("/admin/logs", response_class=HTMLResponse)
async def show_logs(request: Request):
    logs = []
    if os.path.exists(LOG_DIR):
        for filename in os.listdir(LOG_DIR):
            if filename.endswith(".txt"):
                with open(os.path.join(LOG_DIR, filename), "r", encoding="utf-8") as f:
                    logs.append({
                        "filename": filename,
                        "content": f.read()
                    })
    return templates.TemplateResponse("admin_logs.html", {"request": request, "logs": logs})


@router.get("/admin/logs/download/{filename}")
def download_log(filename: str):
    file_path = os.path.join(LOG_DIR, filename)
    if not os.path.exists(file_path):
        return HTMLResponse("File not found", status_code=404)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Convert to CSV
    output = StringIO()
    output.write("Question,Answer\n")
    lines = content.strip().split("\n")
    for i in range(0, len(lines), 2):
        question = lines[i].replace("Q: ", "")
        answer = lines[i + 1].replace("A: ", "") if i + 1 < len(lines) else ""
        output.write(f"\"{question}\",\"{answer}\"\n")
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={filename.replace('.txt', '.csv')}"
    })
