import cv2
import time
import os
import json
import speech_recognition as sr
from utils.emotion_detector import detect_emotion
from utils.voice_assistant import speak_question
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates # adjust import if needed
from utils.question_generator import get_sample_questions  # adjust import if needed
from utils.question_generator import get_sample_questions
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Sample questions
questions = [
    {"text_en": "Tell me about your latest project.", "text_ur": "اپنے حالیہ پروجیکٹ کے بارے میں بتائیں۔"},
    {"text_en": "What are your key strengths?", "text_ur": "آپ کی اہم خوبیاں کیا ہیں؟"},
    {"text_en": "Why should we hire you?", "text_ur": "ہم آپ کو کیوں منتخب کریں؟"},
]

def choose_language_based_on_emotion(emotion):
    # Example: If confused/sad, switch to Urdu
    if emotion in ['angry', 'sad', 'fear', 'disgust']:
        return 'ur'  # Urdu
    return 'en'     # English

def get_speech_response(timeout=5):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[INFO] Listening for answer...")
        audio = recognizer.listen(source, timeout=timeout)
        try:
            text = recognizer.recognize_google(audio)
            print(f"[RESPONSE] {text}")
            return text
        except sr.UnknownValueError:
            print("[WARN] Could not understand the response.")
            return "Could not understand."
        except sr.RequestError as e:
            print(f"[ERROR] Speech recognition error: {e}")
            return "Speech recognition failed."

def run_video_interview(questions, log_path="data/interview_log.json"):
    cap = cv2.VideoCapture(0)
    question_index = 0
    interview_log = []

    print("[INFO] Starting video interview...")
    time.sleep(2)

    while cap.isOpened() and question_index < len(questions):
        ret, frame = cap.read()
        if not ret:
            break

        emotion = detect_emotion(frame)
        lang = choose_language_based_on_emotion(emotion)
        question = questions[question_index]
        question_text = question[f"text_{lang}"]

        # Speak the question
        speak_question(question_text, language=lang)

        # Show frame with info
        cv2.putText(frame, f"Emotion: {emotion}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Q: {question_text}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.imshow("Live Interview (Press Q to Quit)", frame)

        # Get answer from mic
        response = get_speech_response()

        # Save to log
        interview_log.append({
            "question_en": question["text_en"],
            "question_ur": question["text_ur"],
            "language": lang,
            "emotion": emotion,
            "response": response
        })

        question_index += 1
        time.sleep(1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Save interview log
    os.makedirs("data", exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(interview_log, f, indent=4)
    print(f"[INFO] Interview log saved to {log_path}")


@router.get("/video", response_class=HTMLResponse)
async def load_video_page(request: Request):
    return templates.TemplateResponse("video.html", {"request": request})

@router.post("/start-video")
async def start_video_interview():
    questions = get_sample_questions()
    run_video_interview(questions)
    return RedirectResponse(url="/video", status_code=303)
