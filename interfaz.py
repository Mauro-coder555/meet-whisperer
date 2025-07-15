import gradio as gr
import shutil
import os
import time
from procesador.core import procesar_transcripcion

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

def subir_y_procesar(archivo):
    # Guardar archivo en carpeta input
    nombre_archivo = os.path.basename(archivo.name)
    path_destino = os.path.join(INPUT_FOLDER, nombre_archivo)
    shutil.copy(archivo.name, path_destino)

    # Esperar unos segundos a que el watcher lo procese (opcional)
    time.sleep(2)

    # Buscar archivo procesado
    nombre_base = os.path.splitext(nombre_archivo)[0]
    archivos_output = [f for f in os.listdir(OUTPUT_FOLDER) if f.startswith(nombre_base)]
    
    if not archivos_output:
        return "No se generó ningún resumen todavía."

    archivo_final = sorted(archivos_output)[-1]
    path_final = os.path.join(OUTPUT_FOLDER, archivo_final)

    with open(path_final, "r", encoding="utf-8") as f:
        contenido = f.read()

    return contenido

gr.Interface(
    fn=subir_y_procesar,
    inputs=gr.File(label="Arrastrá tu transcripción aquí (.txt)"),
    outputs=gr.Textbox(label="Resumen generado", lines=30),
    title="Procesador de Reuniones IT",
    description="Subí un archivo de transcripción (.txt) y generá un resumen estructurado.",
    theme="default"
).launch()
