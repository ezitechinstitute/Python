# utils/emotion_recognizer.py

from deepface import DeepFace
import cv2
import datetime

def detect_emotion_live():
    cap = cv2.VideoCapture(0)  # 0 is your default webcam
    emotion_log = []

    print("[INFO] Starting video stream. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            dominant_emotion = result[0]['dominant_emotion']
            timestamp = datetime.datetime.now().isoformat()

            emotion_log.append({
                "emotion": dominant_emotion,
                "timestamp": timestamp
            })

            # Display emotion on frame
            cv2.putText(frame, f"Emotion: {dominant_emotion}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        except Exception as e:
            print(f"[WARN] Emotion detection failed: {e}")
            continue

        cv2.imshow("Live Emotion Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return emotion_log
