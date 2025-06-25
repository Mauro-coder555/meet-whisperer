#!/usr/bin/env python
"""
MeetWhisperer CLI
Ejemplo:
    python main.py audio/mi_reunion.wav --model small
"""
import argparse, json
from pathlib import Path

from utils.transcriber import transcribe_audio
from utils.summarizer   import summarize
from utils.extractor    import analyze

OUT_DIR = Path("output")
OUT_DIR.mkdir(exist_ok=True)

def _save(txt: str, fname: str):
    (OUT_DIR / fname).write_text(txt, encoding="utf-8")
    print(f"📝 {fname} guardado en {OUT_DIR}/")

def main():
    ap = argparse.ArgumentParser(description="Transcribe & resume Google-Meet audios")
    ap.add_argument("audio", help="Ruta al archivo .wav/.mp3")
    ap.add_argument("--model", default="base", help="Tamaño de modelo Whisper (tiny/base/small/medium/large)")
    args = ap.parse_args()

    print("🎧 Transcribiendo…")
    transcript = transcribe_audio(args.audio, model_size=args.model)
    _save(transcript, "transcripcion.txt")

    print("📝 Resumiendo…")
    summary = summarize(transcript)
    _save(summary, "resumen.txt")

    print("📋 Extrayendo tareas y entidades…")
    analysis = analyze(transcript)
    _save(json.dumps(analysis, indent=2, ensure_ascii=False), "tareas_entidades.json")

    print("\n✅ Listo. Archivos disponibles en:", OUT_DIR)

if __name__ == "__main__":
    main()
