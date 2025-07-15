import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
from procesador.core import procesar_transcripcion

OUTPUT_FOLDER = "output"

def seleccionar_archivo():
    ruta_archivo = filedialog.askopenfilename(
        title="Selecciona un archivo de texto",
        filetypes=[("Archivos de texto", "*.txt")]
    )
    if ruta_archivo:
        procesar_archivo(ruta_archivo)

def procesar_archivo(ruta_archivo):
    status_label.config(text="Procesando...", fg="blue")
    root.update_idletasks()

    try:
        procesar_transcripcion(ruta_archivo)
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
        status_label.config(text="Error durante el procesamiento", fg="red")
        return

    import glob

    nombre = os.path.splitext(os.path.basename(ruta_archivo))[0]
    patron = os.path.join(OUTPUT_FOLDER, f"{nombre}_resumen*.md")
    coincidencias = sorted(glob.glob(patron), key=os.path.getmtime, reverse=True)

    if coincidencias:
        resumen_path = coincidencias[0]
        status_label.config(text="¡Resumen generado con éxito!", fg="green")
        abrir_btn.config(state=tk.NORMAL)
        abrir_btn.config(command=lambda: abrir_archivo(resumen_path))
    else:
        status_label.config(text="No se generó el resumen.", fg="red")


def abrir_archivo(ruta):
    if os.name == "nt":  # Windows
        os.startfile(ruta)
    elif os.name == "posix":  # Linux/macOS
        subprocess.call(["xdg-open", ruta])

# Interfaz básica con Tkinter
root = tk.Tk()
root.title("Procesador de Transcripciones")
root.geometry("400x200")
root.resizable(False, False)

titulo = tk.Label(root, text="Procesador de Transcripciones IT", font=("Arial", 14, "bold"))
titulo.pack(pady=10)

seleccionar_btn = tk.Button(root, text="Seleccionar archivo .txt", command=seleccionar_archivo, font=("Arial", 11))
seleccionar_btn.pack(pady=5)

status_label = tk.Label(root, text="", font=("Arial", 11))
status_label.pack(pady=10)

abrir_btn = tk.Button(root, text="Abrir resumen", state=tk.DISABLED, font=("Arial", 11))
abrir_btn.pack()

root.mainloop()
