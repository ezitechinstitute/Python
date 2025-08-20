from fastapi import APIRouter, Query
import cv2
import base64
import numpy as np
from utils.emotion_detector import detect_emotion_frame
from utils.emotion_recognizer import detect_emotion_live
from utils.emotion_logger import save_emotion_log

router = APIRouter()

@router.get("/video-feed")
def video_feed():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return {"error": "Could not access camera"}

    result_frame = detect_emotion_frame(frame)
    _, buffer = cv2.imencode('.jpg', result_frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return {"frame": jpg_as_text}

@router.get("/emotion/start")
def start_emotion_detection(candidate_name: str = Query(..., description="Candidate's full name")):
    try:
        log = detect_emotion_live()
        path = save_emotion_log(candidate_name, log)
        return {"message": "Emotion log completed", "log_path": path}
    except Exception as e:
        return {"error": str(e)}
