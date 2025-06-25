# utils/transcriber.py
from pathlib import Path
import whisper

def transcribe_audio(path: str | Path, model_size: str = "base") -> str:
    """
    Devuelve la transcripción completa del audio.
    """
    model = whisper.load_model(model_size)
    result = model.transcribe(str(path), fp16=False)  # fp16=False en CPU
    return result["text"].strip()
