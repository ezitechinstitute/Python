import spacy
import random
from typing import List, Dict, Optional
from utils import resume_parser
import logging

nlp = spacy.load("en_core_web_sm")  # Make sure it's installed!

# Constants for question types
TECHNICAL = "technical"
BEHAVIORAL = "behavioral"
SCENARIO = "scenario"

def extract_keywords(text: str) -> List[str]:
    """Extract relevant keywords from text using NLP"""
    doc = nlp(text)
    keywords = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 2:
            keywords.append(token.text.lower())
    return list(set(keywords))

def generate_questions_from_resume(
    resume_text: Optional[str] = None,
    job_title: str = "",
    language: str = "en",
    experience_level: str = "mid",
    count: int = 10,
    include_technical: bool = True,
    include_behavioral: bool = True,
    include_scenarios: bool = True
) -> List[str]:
    """
    Generate interview questions based on resume content and job requirements
    Supports both resume-based and field-specific question generation
    """
    questions = []
    
    # Common questions for all roles
    common_questions = get_common_questions(language)
    
    # Resume-specific questions if resume provided
    if resume_text:
        questions.extend(generate_resume_specific_questions(resume_text, language))
    
    # Field-specific questions
    field_questions = get_field_specific_questions(
        job_title,
        language,
        include_technical,
        include_behavioral,
        include_scenarios
    )
    
    # Combine and filter questions
    all_questions = common_questions + field_questions
    questions.extend(filter_questions_by_level(all_questions, experience_level))
    
    # Ensure we return the requested number of unique questions
    return list(set(questions))[:count]  # Remove duplicates and limit count

def get_common_questions(language: str) -> List[str]:
    """Get common interview questions for all roles"""
    return {
        "en": [
            "Tell me about yourself",
            "Why are you interested in this position?",
            "What are your strengths and weaknesses?",
            "Where do you see yourself in 5 years?",
            "Describe a challenging project you worked on"
        ],
        "ur": [
            "اپنے بارے میں بتائیں",
            "آپ کو اس پوزیشن میں دلچسپی کیوں ہے؟",
            "آپ کی خوبیاں اور خامیاں کیا ہیں؟",
            "آپ اپنے آپ کو 5 سال میں کہاں دیکھتے ہیں؟",
            "کسی مشکل منصوبے کے بارے میں بتائیں جس پر آپ نے کام کیا ہو"
        ]
    }.get(language, [])

def generate_resume_specific_questions(resume_text: str, language: str) -> List[str]:
    """Generate questions based on resume content"""
    parsed = resume_parser.parse_resume(resume_text)
    questions = []
    
    if language == "ur":
        if parsed.get('name'):
            questions.append(f"آپ کا نام {parsed['name']} ہے؟ براہ کرم اپنا تعارف کروائیں۔")
        if parsed.get('skills'):
            questions.append(f"آپ کی مہارتیں: {', '.join(parsed['skills'])}. ان میں سے سب سے اہم کون سی ہے؟")
        if parsed.get('projects'):
            questions.append(f"اپنے پراجیکٹ '{parsed['projects'][0]}' کے بارے میں بتائیں۔")
        questions.append("آپ اس جاب میں کیوں دلچسپی رکھتے ہیں؟")
    else:
        if parsed.get('name'):
            questions.append(f"Is your name {parsed['name']}? Please introduce yourself.")
        if parsed.get('skills'):
            questions.append(f"Your skills include: {', '.join(parsed['skills'])}. Which is your strongest?")
        if parsed.get('projects'):
            questions.append(f"Tell me about your project '{parsed['projects'][0]}'.")
        questions.append("Why are you interested in this job?")
    
    return questions

def get_field_specific_questions(
    job_title: str,
    language: str,
    include_technical: bool,
    include_behavioral: bool,
    include_scenarios: bool
) -> List[str]:
    """Get questions specific to the job field"""
    field_questions = {
        "AI/ML Engineer": {
            "technical": [
                "Explain the difference between CNN and RNN",
                "How would you handle imbalanced datasets?",
                "Describe your experience with TensorFlow/PyTorch",
                "What evaluation metrics would you use for classification?",
                "How do you prevent model overfitting?"
            ],
            "behavioral": [
                "Describe a time you had to explain ML concepts to non-technical people",
                "How do you stay updated with AI research?",
                "Tell me about a failed ML project and what you learned"
            ],
            "scenario": [
                "How would you build a recommendation system with limited data?",
                "Walk me through your approach to a new NLP problem",
                "What would you do if your model performs well in training but poorly in production?"
            ]
        },
        "Web Development": {
            "technical": [
                "Explain REST vs GraphQL",
                "How do you optimize website performance?",
                "Describe your experience with React/Vue/Angular",
                "What security measures do you implement?",
                "How do you handle state management?"
            ],
            "behavioral": [
                "Describe a challenging bug you fixed",
                "How do you collaborate with designers?",
                "Tell me about a project where you improved user experience"
            ],
            "scenario": [
                "How would you redesign a slow legacy system?",
                "What would you do if a client wants features that hurt performance?",
                "How would you handle a major production outage?"
            ]
        },
        # Add all other fields with the same structure
        "Mobile App Development": {
            "technical": [
                "Compare native vs hybrid development",
                "How do you handle different screen sizes?",
                "Describe your approach to mobile security",
                "What tools do you use for debugging?",
                "How do you optimize app performance?"
            ],
            "behavioral": [
                "Describe a challenging UI implementation",
                "How do you handle platform-specific requirements?",
                "Tell me about an app you're particularly proud of"
            ],
            "scenario": [
                "How would you reduce app size significantly?",
                "What would you do if an app update gets rejected?",
                "How would you handle a critical crash in production?"
            ]
        },
        "Data Science": {
            "technical": [
                "Explain your data cleaning process",
                "How do you handle missing data?",
                "Describe your experience with Pandas/SQL",
                "What visualization tools do you prefer?",
                "How do you validate your models?"
            ],
            "behavioral": [
                "Describe a time you found unexpected insights",
                "How do you communicate findings to stakeholders?",
                "Tell me about a project where data quality was poor"
            ],
            "scenario": [
                "How would you approach a problem with messy, unstructured data?",
                "What would you do if stakeholders disagree with your analysis?",
                "How would you explain a complex model to non-technical executives?"
            ]
        }
        # Add remaining fields following the same pattern
    }
    
    questions = []
    field_data = field_questions.get(job_title, {})
    
    if include_technical:
        questions.extend(field_data.get(TECHNICAL, []))
    if include_behavioral:
        questions.extend(field_data.get(BEHAVIORAL, []))
    if include_scenarios:
        questions.extend(field_data.get(SCENARIO, []))
    
    return questions

def filter_questions_by_level(questions: List[str], level: str) -> List[str]:
    """Filter questions based on experience level"""
    if level == "entry":
        return [q for q in questions if not any(w in q.lower() for w in ["senior", "complex", "lead"])]
    elif level == "senior":
        return [q.replace("basic", "advanced") for q in questions]
    return questions

# Legacy functions (maintained for compatibility)
def generate_questions(num: int = 5) -> List[str]:
    """Legacy function - generates generic questions"""
    sample = [
        "Tell me about yourself.",
        "Why should we hire you?",
        "Describe a challenge you've overcome.",
        "Where do you see yourself in 5 years?",
        "What is your greatest strength?",
    ]
    return sample[:num]

def get_sample_questions() -> List[Dict[str, str]]:
    """Legacy function - returns sample questions in both languages"""
    return [
        {"text_en": "Tell me about your latest project.", "text_ur": "اپنے حالیہ پروجیکٹ کے بارے میں بتائیں۔"},
        {"text_en": "What are your key strengths?", "text_ur": "آپ کی اہم خوبیاں کیا ہیں؟"},
        {"text_en": "Why should we hire you?", "text_ur": "ہم آپ کو کیوں منتخب کریں؟"},
    ]
    