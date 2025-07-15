import os
import json
import logging
from llama_cpp import Llama
from datetime import datetime
from rapidfuzz import process
import re

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Ruta del modelo LLaMA local
MODEL_PATH = "./models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"

# Inicializar modelo con manejo de errores
try:
    llm = Llama(model_path=MODEL_PATH, n_ctx=16384, verbose=False)
    logging.info("Modelo cargado exitosamente.")
except Exception as e:
    logging.error(f"Error al cargar el modelo: {e}")
    raise

# Cargar glosario técnico
try:
    with open("procesador/glosario_tecnico.json", "r", encoding="utf-8") as f:
        GLOSARIO = json.load(f)
    logging.info("Glosario cargado exitosamente.")
except Exception as e:
    logging.error(f"Error al cargar el glosario: {e}")
    GLOSARIO = {}

# Preprocesamiento de texto
def preprocesar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto)
    texto = texto.strip()
    return texto

def corregir_errores(texto, glosario, umbral=90):
    palabras = re.findall(r'\w+|\S', texto)
    corregidas = []

    for i, palabra in enumerate(palabras):
        palabra_limpia = palabra.lower()

        if palabra_limpia in glosario:
            corregido = glosario[palabra_limpia]
            if palabra_limpia != corregido.lower():
                palabras[i] = corregido
                corregidas.append((palabra_limpia, corregido))
        else:
            match, score, _ = process.extractOne(palabra_limpia, glosario.keys())
            if score > umbral:
                corregido = glosario[match]
                if palabra_limpia != corregido.lower():
                    palabras[i] = corregido
                    corregidas.append((palabra_limpia, corregido))

    return " ".join(palabras), corregidas

def generar_prompt(texto):
    prompt = (
        "Actúas como un asistente experto en reuniones IT. Tu tarea es procesar transcripciones desordenadas "
        "y generar un informe claro y útil. No inventes información ni asumas responsables si no están explícitamente dichos.\n\n"
        "Dado el texto a continuación, realizá lo siguiente:\n"
        "1. Extraé y listá los puntos clave discutidos.\n"
        "2. Identificá todas las tareas mencionadas.\n"
        "   - Si hay responsable y fecha claros, marcá como tarea confirmada.\n"
        "   - Si se menciona la tarea pero el responsable o la fecha son inciertos, marcala como tarea sugerida.\n"
        "   - Solo clasificala como confirmada si en el texto se nombra explícitamente quién la hará y cuándo.\n"
        "3. Listá decisiones tomadas o postergadas explícitamente.\n"
        "4. Incluí una sección final con ambigüedades, dudas abiertas o cosas no resueltas.\n\n"
        "Generá el informe con esta estructura en Markdown:\n"
        "## Resumen Ejecutivo\n"
        "(Síntesis de los temas clave)\n\n"
        "## Tareas Confirmadas\n"
        "| Tarea | Responsable | Fecha |\n"
        "|-------|-------------|-------|\n"
        "| ...   | ...         | ...   |\n\n"
        "## Tareas Sugeridas (no confirmadas)\n"
        "| Tarea | Responsable posible | Comentario |\n"
        "|-------|----------------------|------------|\n"
        "| ...   | ...                  | ...        |\n\n"
        "## Decisiones\n"
        "- ...\n\n"
        "## Ambigüedades y Temas No Resueltos\n"
        "- ...\n\n"
        "Texto original:\n\"\"\"\n"
        f"{texto}\n"
        "\"\"\"\n"
    )
    return prompt

def procesar_transcripcion(path_archivo):
    nombre = os.path.basename(path_archivo)
    logging.info(f"Procesando archivo: {nombre}")

    try:
        with open(path_archivo, "r", encoding="utf-8") as f:
            texto = f.read()
    except Exception as e:
        logging.error(f"Error al leer el archivo {nombre}: {e}")
        return

    texto = preprocesar_texto(texto)
    texto_corregido, errores = corregir_errores(texto, GLOSARIO)
    prompt = generar_prompt(texto_corregido)

    try:
        respuesta = llm(prompt=prompt, max_tokens=2048, stop=["</s>"])
        if not respuesta or "choices" not in respuesta or not respuesta["choices"]:
            raise ValueError("La respuesta del modelo está vacía o mal formada.")
        contenido = respuesta["choices"][0]["text"].strip()
    except Exception as e:
        logging.error(f"Error durante la inferencia del modelo: {e}")
        return

    nombre_base = os.path.splitext(nombre)[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"output/{nombre_base}_resumen_{timestamp}.md"

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Resumen de la reunión\n\n")
            f.write(f"**Archivo procesado**: {nombre}\n\n")
            f.write(f"**Fecha de procesamiento**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(contenido)
            f.write("\n\n---\n")
            f.write("### Correcciones automáticas detectadas:\n")
            for original, corregido in errores:
                f.write(f"- **{original}** → **{corregido}**\n")
        logging.info(f"Resumen generado exitosamente en: {output_path}")
    except Exception as e:
        logging.error(f"Error al escribir el resumen: {e}")
