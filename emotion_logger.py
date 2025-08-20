# utils/emotion_logger.py

import os
import json
from datetime import datetime

def save_emotion_log(candidate_name, emotion_data):
    os.makedirs("logs", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/emotions_{candidate_name.replace(' ', '_')}_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump({
            "candidate": candidate_name,
            "timestamp": timestamp,
            "emotions": emotion_data
        }, f, indent=4)

    print(f"[INFO] Emotion log saved to {filename}")
    return filename
