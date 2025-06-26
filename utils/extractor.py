import re
import spacy
from collections import defaultdict

# Cargamos modelo de lenguaje en español
_nlp = spacy.load("es_core_news_md")

# Verbos comunes para detectar acciones / tareas
VERBOS_ACCION = [
    "hacer", "realizar", "crear", "enviar", "preparar", "terminar",
    "resolver", "coordinar", "consolidar", "asistir", "completar",
    "cargar", "armar", "presentar", "revisar", "entregar", "validar",
    "reportar", "encargará", "asegurar", "usar"
]

# Función para extraer entidades básicas
def extract_entities(text: str):
    doc = _nlp(text)

    people = set(ent.text for ent in doc.ents if ent.label_ == "PER")
    orgs = set(ent.text for ent in doc.ents if ent.label_ == "ORG")
    dates = set(ent.text for ent in doc.ents if ent.label_ == "DATE")

    # Extra fechas tipo "jueves 4"
    extra_dates = re.findall(r"\b(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo)\s+\d{1,2}\b", text, re.IGNORECASE)
    dates.update(extra_dates)

    return {
        "PERSON": sorted(people),
        "ORG": sorted(orgs),
        "DATE": sorted(dates),
    }

# Función para buscar la fecha más cercana mencionada en la oración
def detectar_fecha(oracion: str, fechas: set) -> str:
    for fecha in fechas:
        if fecha.lower() in oracion.lower():
            return fecha
    return "Sin fecha"

# Función para detectar tareas con persona y fecha asociada
def extract_tasks_with_persons(text: str):
    doc = _nlp(text)
    tasks = []

    entidades = extract_entities(text)
    personas_conocidas = set(entidades["PERSON"])
    fechas_detectadas = set(entidades["DATE"])

    for sent in doc.sents:
        sent_text = sent.text.strip()
        sent_doc = _nlp(sent_text)

        verbos = [token.lemma_ for token in sent_doc if token.pos_ == "VERB"]
        if not any(v in VERBOS_ACCION for v in verbos):
            continue  # Si no hay verbo de acción, no es tarea

        sujeto = None

        # 1. Buscar sujeto explícito con función gramatical
        for token in sent_doc:
            if token.dep_ in ("nsubj", "nsubj:pass"):
                if token.text in personas_conocidas:
                    sujeto = token.text
                    break

        # 2. Buscar por expresiones de responsabilidad comunes
        if not sujeto:
            patrones = [
                r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s+(se encargará|debe|tiene que|coordina|coordinará|hará|realizará)",
            ]
            for patron in patrones:
                match = re.search(patron, sent_text)
                if match:
                    candidato = match.group(1)
                    if candidato in personas_conocidas:
                        sujeto = candidato
                        break

        # 3. Buscar entidad tipo PERSON en la oración
        if not sujeto:
            for ent in sent_doc.ents:
                if ent.label_ == "PER" and ent.text in personas_conocidas:
                    sujeto = ent.text
                    break

        # Detectar fecha en esta oración
        fecha = detectar_fecha(sent_text, fechas_detectadas)

        tasks.append({
            "description": sent_text,
            "person": sujeto or "No asignado",
            "date": fecha
        })

    return tasks

# Función principal
def analyze(text: str) -> dict:
    return {
        "entities": extract_entities(text),
        "tasks": extract_tasks_with_persons(text),
    }
