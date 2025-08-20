# utils/voice_tts.py
from gtts import gTTS
import os
import uuid
from playsound import playsound

def speak_text(text, lang='en'):
    try:
        filename = f"temp_audio_{uuid.uuid4()}.mp3"
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"[ERROR] TTS failed: {e}")
