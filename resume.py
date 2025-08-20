import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.resume_parser import extract_text_from_pdf, parse_resume

router = APIRouter()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_location = os.path.join("uploads", unique_filename)

        # Save the file temporarily
        with open(file_location, "wb") as f:
            f.write(await file.read())

        try:
            # Process the resume
            text = extract_text_from_pdf(file_location)
            parsed_data = parse_resume(text)
            
            return {
                "message": "Resume parsed successfully",
                "data": parsed_data,
                "filename": file.filename
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists(file_location):
                os.remove(file_location)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")