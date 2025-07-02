# transcriber.py
from transcriber import transcribe_audio
from pathlib import Path
import sys

audio_path = sys.argv[1]
model_size = sys.argv[2] if len(sys.argv) > 2 else "base"

text = transcribe_audio(audio_path, model_size)
Path("output").mkdir(exist_ok=True)
Path("output/transcripcion.txt").write_text(text, encoding="utf-8")
print("✅ Transcripción guardada en output/transcripcion.txt")