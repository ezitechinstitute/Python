# routes/voice.py
from fastapi import APIRouter, Query, HTTPException
from utils.voice_assistant import speak_question

router = APIRouter()

@router.get("/speak")
async def speak_api(question: str = Query(...), lang: str = Query("en")):
    try:
        speak_question(question, language=lang)
        return {"message": "Question spoken successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to speak: {e}")

def speak_question(text, language="en"):
    if language == "ur":
        from gtts import gTTS
        import tempfile
        import os
        import playsound
        tts = gTTS(text, lang="ur")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            playsound.playsound(fp.name)
            os.remove(fp.name)
    else:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
