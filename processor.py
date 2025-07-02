from llama_cpp import Llama
import os

# Ruta al modelo
MODEL_PATH = "./models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"

# Inicializar el modelo
llm = Llama(model_path=MODEL_PATH, n_ctx=2048)

# Leer la transcripción
with open("output/transcripcion.txt", "r", encoding="utf-8") as f:
    transcripcion = f.read()

# Prompt para estructurar el resumen
prompt = f"""
Eres un asistente experto en gestión de proyectos de IT. Has recibido la siguiente transcripción de una reunión laboral. Quiero que generes un resumen estructurado con los siguientes apartados:

1. 📌 **Resumen general** de los temas tratados.
2. ✅ **Lista de tareas o decisiones**, indicando:
   - Tarea o acción
   - Persona/s responsable/s
   - Fecha mencionada o estimada
   - Deadline (si se infiere)
   - Detalles relevantes
3. 🛠️ **Sugerencias de corrección de errores ortográficos o confusiones comunes**, basadas en jerga técnica (por ejemplo: 'CUA' podría ser 'QA', 'power vi' debería ser 'Power BI').

Aquí está la transcripción:
\"\"\"
{transcripcion}
\"\"\"

Responde en formato claro y estructurado, usando listas y markdown si lo deseas.
"""

# Ejecutar el modelo
respuesta = llm(prompt=prompt, max_tokens=1024, stop=["</s>"])

# Grabar la respuesta generada
with open("output/resumen_reunion.md", "w", encoding="utf-8") as f:
    f.write(respuesta["choices"][0]["text"].strip())

