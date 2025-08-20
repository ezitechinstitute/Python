import fitz  # PyMuPDF

def parse_cv(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    # Very basic extraction - you can improve
    return {
        "name": text.split("\n")[0],
        "email": next((line for line in text.split("\n") if "@" in line), None),
        "skills": [word.strip() for word in text.split() if word.lower() in ["python", "ml", "ai", "data", "sql"]]
    }

# Install PyMuPDF using pip
# !pip install PyMuPDF

