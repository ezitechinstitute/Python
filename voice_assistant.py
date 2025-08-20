import os
import pyttsx3
from gtts import gTTS
import tempfile
import playsound

def speak_question(text, language='en'):
    """
    Speaks a given question using TTS (Text-to-Speech).
    
    Parameters:
    - text (str): The question to be spoken.
    - language (str): 'en' for English (offline using pyttsx3), 
                      'ur' for Urdu (online using gTTS).
    """
    if language == 'en':
        try:
            # Use pyttsx3 for offline English TTS
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # speaking speed
            engine.setProperty('volume', 1.0)  # max volume
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[ERROR] English TTS failed: {e}")

    elif language == 'ur':
        try:
            # Use gTTS for Urdu (requires internet)
            tts = gTTS(text=text, lang='ur')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                playsound.playsound(fp.name)
                os.remove(fp.name)
        except Exception as e:
            print(f"[ERROR] Urdu TTS failed: {e}")

    else:
        print(f"[ERROR] Unsupported language '{language}'. Use 'en' or 'ur'.")
