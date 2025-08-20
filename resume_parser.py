import re
import pytesseract
from PIL import Image
import os
from langdetect import detect
from docx import Document

# Configure tesseract cmd path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path):
    text = ""
    print(f"[DEBUG] Will try to open: {pdf_path}")
    try:
        # Try PyMuPDF first
        import fitz  # PyMuPDF
        with fitz.open(pdf_path) as doc:
            for page in doc:
                page_text = page.get_text()
                print(f"[DEBUG] PyMuPDF page text length: {len(page_text)}")
                text += page_text
        print(f"[DEBUG] Text after PyMuPDF: {len(text)} chars")

        # If no text, try pdfplumber
        if not text.strip():
            print("[INFO] No text found with PyMuPDF, trying pdfplumber...")
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        print(f"[DEBUG] pdfplumber page text length: {len(page_text)}")
                        text += page_text
            print(f"[DEBUG] Text after pdfplumber: {len(text)} chars")

        # If still no text, try OCR
        if not text.strip():
            print("[INFO] No text found, trying OCR...")
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path)
            print(f"[DEBUG] Number of images from PDF: {len(images)}")
            for img in images:
                ocr_text = pytesseract.image_to_string(img)
                print(f"[DEBUG] OCR text length: {len(ocr_text)}")
                text += ocr_text
    except Exception as e:
        import traceback
        print(f"[ERROR] Failed to extract text: {e}")
        traceback.print_exc()
    print(f"[DEBUG] Extracted text length: {len(text)}")
    return text

def parse_resume(text):
    # Basic patterns
    email = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone = re.findall(r"\+?\d[\d\-\(\) ]{8,}\d", text)
    linkedin = re.findall(r"(https?://[^\s]+linkedin\.com[^\s]*)", text, re.I)
    github = re.findall(r"(https?://[^\s]+github\.com[^\s]*)", text, re.I)
    name = text.split('\n')[0] if text else "Name Not Found"

    # Skills & Projects (improved extraction)
    skills_keywords = [
        # AI/ML
        'python', 'tensorflow', 'pytorch', 'scikit-learn', 'nlp', 'computer vision',
        # Web Dev
        'html', 'css', 'javascript', 'react', 'node', 'django', 'flask',
        # Mobile
        'flutter', 'react native', 'swift', 'kotlin', 'android studio', 'xcode',
        # DevOps
        'docker', 'kubernetes', 'aws', 'azure', 'terraform', 'jenkins',
        # Data Science
        'pandas', 'numpy', 'sql', 'tableau', 'power bi',
        # Blockchain
        'solidity', 'ethereum', 'web3', 'smart contracts', 'truffle',
        # UI/UX
        'figma', 'adobe xd', 'sketch', 'user research', 'wireframing',
        # QA
        'selenium', 'junit', 'testng', 'cypress', 'jmeter',
        # Cloud
        'gcp', 'serverless', 'lambda', 'ec2',
        # Cyber Security
        'penetration testing', 'owasp', 'kali linux', 'siem'
    ]
    skills_found = [skill for skill in skills_keywords if skill.lower() in text.lower()]

    projects = re.findall(r'(?i)project[:\-]?\s*(.*)', text)

    return {
        "name": name.strip(),
        "email": email[0] if email else "Not found",
        "phone": phone[0] if phone else "Not found",
        "linkedin": linkedin[0] if linkedin else "Not found",
        "github": github[0] if github else "Not found",
        "skills": skills_found,
        "projects": projects[:3] if projects else []
    }

def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"[ERROR] Failed to extract text from DOCX: {e}")
    return text

def extract_text_from_image(image_path):
    text = ""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
    except Exception as e:
        print(f"[ERROR] Failed to extract text from image: {e}")
    return text

def detect_language(text):
    try:
        lang = detect(text)
        print(f"[DEBUG] Detected language: {lang}")
        return lang
    except Exception as e:
        print(f"[ERROR] Language detection failed: {e}")
        return "unknown"