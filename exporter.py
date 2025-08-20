import json
from fpdf import FPDF
import os

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_to_json(candidate_name, data):
    path = os.path.join(EXPORT_DIR, f"{candidate_name}_summary.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    return path

def export_to_pdf(candidate_name, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Interview Summary - {candidate_name}", ln=True, align="C")
    pdf.ln(10)

    for item in data.get("responses", []):
        pdf.multi_cell(0, 10, f"Q: {item['question']}")
        pdf.multi_cell(0, 10, f"A: {item['answer']}")
        pdf.ln(5)

    if "feedback" in data:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Feedback:", ln=True)
        pdf.set_font("Arial", size=12)
        for point in data["feedback"]:
            pdf.multi_cell(0, 10, f"- {point}")

    if "recommendation" in data:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Recommended Role: {data['recommendation']}", ln=True)

    path = os.path.join(EXPORT_DIR, f"{candidate_name}_summary.pdf")
    pdf.output(path)
    return path
