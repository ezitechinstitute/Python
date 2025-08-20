import cv2
from deepface import DeepFace
import numpy as np
import random

def detect_emotion_frame(frame):
    try:
        analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        dominant_emotion = analysis[0]['dominant_emotion']
        cv2.putText(frame, dominant_emotion, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    except Exception as e:
        cv2.putText(frame, "Error", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return frame

def detect_emotion(frame):
    emotions = ['happy', 'sad', 'neutral', 'angry', 'surprised']
    return random.choice(emotions)  # Replace with ML prediction later
