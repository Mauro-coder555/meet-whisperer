# utils/extractor.py
import re, spacy
from collections import defaultdict

_nlp = spacy.load("es_core_news_md")

TODO_PATTERNS = [
    r"\b(?:hacer|realizar|crear|enviar|preparar|terminar|resolver)\b[^.]{0,80}",
    r"\b(?:next step|próximo paso|tarea pendiente)\b[^.]{0,80}",
]

def extract_entities(text: str):
    doc = _nlp(text)
    return {
        "PERSON": [ent.text for ent in doc.ents if ent.label_ == "PER"],
        "ORG":    [ent.text for ent in doc.ents if ent.label_ == "ORG"],
        "DATE":   [ent.text for ent in doc.ents if ent.label_ == "DATE"],
    }

def extract_todos(text: str):
    todos = []
    for pat in TODO_PATTERNS:
        todos.extend(re.findall(pat, text, flags=re.IGNORECASE))
    return [t.strip() for t in todos]

def analyze(text: str) -> dict:
    return {
        "entities": extract_entities(text),
        "tasks": extract_todos(text),
    }
