import cv2
from deepface import DeepFace

def stream_camera():
    cap = cv2.VideoCapture(0)  # 0 = default webcam
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield frame
    cap.release()

def analyze_emotion(frame):
    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
    return result[0]['dominant_emotion']
