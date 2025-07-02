from llama_cpp import Llama
import os
import re

# --- Configuración del Modelo y Archivos ---
MODEL_PATH = "./models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
TRANSCRIPTION_FILE = "output/transcripcion.txt"
OUTPUT_FILE = "resumen_y_sugerencias_reunion.txt" # Unificamos la salida

# --- Cargar el Modelo Llama ---
if not os.path.exists(MODEL_PATH):
    print(f"Error: El archivo del modelo no se encuentra en '{MODEL_PATH}'")
    print("Por favor, verifica la ruta y asegúrate de que el modelo esté descargado.")
    exit()

if not os.path.exists(TRANSCRIPTION_FILE):
    print(f"Error: El archivo de transcripción no se encuentra en '{TRANSCRIPTION_FILE}'")
    print("Asegúrate de que el archivo exista y esté en la misma carpeta o especifica la ruta correcta.")
    exit()

print(f"Cargando el modelo Llama CPP desde: {MODEL_PATH}...")
try:
    llm = Llama(model_path=MODEL_PATH, n_ctx=8192, n_gpu_layers=-1, verbose=False)
    print("Modelo cargado exitosamente.")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    print("Asegúrate de tener la librería 'llama-cpp-python' instalada y compatible con tu hardware (GPU recomendada).")
    exit()

# --- Leer la Transcripción ---
print(f"Leyendo la transcripción desde: {TRANSCRIPTION_FILE}...")
try:
    with open(TRANSCRIPTION_FILE, "r", encoding="utf-8") as f:
        transcription_text = f.read()
    print("Transcripción leída exitosamente.")
except Exception as e:
    print(f"Error al leer el archivo de transcripción: {e}")
    exit()

# --- Función para obtener sugerencias de corrección basadas en la confianza del modelo ---
def get_contextual_correction_suggestion(text_segment, llm_model):
    """
    Pide al LLM que identifique posibles errores de transcripción en un segmento
    y sugiera la corrección más probable, devolviendo la palabra original y la corrección.
    """
    correction_prompt = f"""[INST]Eres un experto en transcripción y corrección de lenguaje natural para el contexto de reuniones laborales.
Tu tarea es analizar el siguiente segmento de texto e identificar errores de transcripción,
específicamente aquellos causados por la fonética, errores tipográficos, o mal reconocimiento de nombres de productos, sistemas o términos técnicos.

Si encuentras una palabra o frase que **claramente** parece un error de transcripción, debes responder en el siguiente formato **ESTRICTO**:
Original: [palabra_o_frase_erronea] -> Corrección: [corrección_sugerida]

Si la transcripción de una palabra/frase podría referirse a múltiples cosas (ej. "Cloc" vs. "Clockify"), sugiere la opción más común en un contexto de desarrollo/negocio, pero **solo si es un error de transcripción**.

Si **no hay un error de transcripción obvio** en el segmento, o la palabra está correctamente transcripta, responde **ESTRICTAMENTE**: NINGÚN ERROR

Ejemplos (presta atención al formato de salida requerido):
-   **Segmento:** "El equipo de CUA revisará esto."
    **Salida esperada:** Original: CUA -> Corrección: QA
-   **Segmento:** "Necesitamos trabajar en el vaquen."
    **Salida esperada:** Original: vaquen -> Corrección: Backend
-   **Segmento:** "Recordó usar la nueva plantilla de Google Sits que compartió Marcos."
    **Salida esperada:** Original: Google Sits -> Corrección: Google Sites
-   **Segmento:** "el enpont para la carga masiva estará listo el viernes 28."
    **Salida esperada:** Original: enpont -> Corrección: endpoint
-   **Segmento:** "todos deben cargar sus horas en cloc y fiantes del viernes 5 a las 6"
    **Salida esperada:** Original: cloc y fiantes -> Corrección: Clockify
-   **Segmento:** "La reunión duró una hora."
    **Salida esperada:** NINGÚN ERROR
-   **Segmento:** "La decisión final se tomará en la reunión técnica."
    **Salida esperada:** NINGÚN ERROR

---
Segmento de Texto para analizar: "{text_segment}"
---
Salida:[/INST]"""

    try:
        correction_output = llm(
            correction_prompt,
            max_tokens=60, # Suficiente para la pareja Original -> Corrección
            temperature=0.0, # Temperatura 0 para respuestas lo más deterministas y precisas posible.
            stop=["[INST]", "</s>"],
            echo=False
        )
        raw_correction = correction_output["choices"][0]["text"].strip()

        if "ningún error" in raw_correction.lower() or not raw_correction:
            return None

        # Intentar parsear el formato "Original: X -> Corrección: Y"
        match = re.match(r"Original:\s*(.*?)\s*->\s*Corrección:\s*(.*)", raw_correction, re.IGNORECASE)
        if match:
            original = match.group(1).strip()
            corrected = match.group(2).strip()
            return original, corrected
        else:
            # Si el modelo no sigue el formato, lo ignoramos o lo logeamos
            print(f"Advertencia: Modelo no siguió el formato esperado para la corrección: {raw_correction}")
            return None
    except Exception as e:
        print(f"Error al solicitar corrección para segmento '{text_segment}': {e}")
        return None

# --- Detección de segmentos con posibles errores y obtención de sugerencias ---
print("Identificando posibles errores de transcripción y solicitando sugerencias al modelo...")

# Dividir el texto en frases o segmentos para analizar el contexto
# Usamos un patrón que respeta puntos, comas, etc., para obtener segmentos de oración.
segments = re.split(r'(?<=[.!?])\s+|\n', transcription_text)
segments = [s.strip() for s in segments if s.strip()]

unique_suggestions = {} # Almacenará Original -> Corrección

# Iteramos sobre segmentos de texto para que el LLM tenga suficiente contexto
for segment in segments:
    if len(segment) < 10: # Ignorar segmentos muy cortos
        continue

    suggestion_pair = get_contextual_correction_suggestion(segment, llm)

    if suggestion_pair:
        original, corrected = suggestion_pair
        # Evitar sugerir lo mismo si la corrección es igual al original (ej. "PostgreSQL" -> "PostgreSQL")
        if original.lower() != corrected.lower():
            unique_suggestions[original] = corrected

# --- Preparar el Prompt para el Resumen ---
# Ajustes para ser aún más estricto en la separación de secciones y en el formato de acciones.
prompt_summary = f"""[INST]Eres un asistente de IA experto en resumir transcripciones de reuniones laborales.
Tu objetivo es generar un resumen altamente conciso, preciso y útil.

La transcripción de la reunión es la siguiente:
{transcription_text}

Por favor, genera el resumen de la reunión, estructurado estrictamente en las siguientes tres secciones usando formato Markdown y listas:

1.  **Puntos Clave Discutidos:**
    * Enumera solo los temas principales que se abordaron. No incluyas decisiones o acciones aquí.
2.  **Decisiones Tomadas:**
    * Detalla únicamente los acuerdos, resoluciones o determinaciones definitivas que se alcanzaron. No repitas puntos clave o acciones.
3.  **Acciones Pendientes (Action Items):**
    * Lista cada tarea específica que deba realizarse, siguiendo este formato para cada una:
        * **[Nombre del Responsable]:** [Descripción concisa de la acción] ([Fecha Límite/Plazo], si se mencionó explícitamente)
    * Si un responsable o una fecha no se mencionan explícitamente para una acción, omítelos para *esa* acción específica, pero mantén el formato general.
    * Asegúrate de incluir *todas* las acciones pendientes mencionadas.

El resumen debe ser directo y fiel a la transcripción. No añadas información que no esté en el texto.
---
Resumen de la Reunión:
[/INST]"""

# --- Generar el Resumen con Llama ---
print("Generando el resumen con el modelo Llama CPP. Esto puede tomar un momento...")
generated_summary = ""
try:
    output = llm(
        prompt_summary,
        max_tokens=800, # Aumentado para permitir resúmenes más detallados
        temperature=0.3, # Mantener baja para precisión, 0.3 es un buen balance.
        stop=["[INST]", "</s>"],
        echo=False
    )
    generated_summary = output["choices"][0]["text"].strip()
    print("\n--- Resumen Generado ---")
    print(generated_summary)

except Exception as e:
    print(f"Error al generar el resumen: {e}")

# --- Unificar y Guardar la Salida Final ---
final_output_content = f"--- Resumen de la Reunión ---\n\n{generated_summary}\n\n"

if unique_suggestions:
    suggestions_text_section = "--- Sugerencias de Corrección de Transcripción ---\n\n"
    print("\n--- Sugerencias de Corrección de Transcripción ---")
    # Ordenar las sugerencias para una salida consistente
    for original, suggested in sorted(unique_suggestions.items()):
        line = f"- '{original}' -> '{suggested}'"
        print(line)
        suggestions_text_section += line + "\n"
    final_output_content += suggestions_text_section
else:
    no_suggestions_msg = "\nNo se detectaron palabras/frases que requieran sugerencias de corrección de transcripción significativas."
    print(no_suggestions_msg)
    final_output_content += no_suggestions_msg + "\n"

try:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_output_content)
    print(f"\nSalida completa (resumen y sugerencias) guardada en: {OUTPUT_FILE}")
except Exception as e:
    print(f"Error al guardar el archivo de salida: {e}")