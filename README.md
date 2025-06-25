# MeetWhisperer

**Transcribe, resume y extrae tareas de tus reuniones (Google Meet, Teams, Zoom, etc.) usando Python y librerías open-source.**

Ideal para personas que asisten a reuniones técnicas o laborales y quieren ahorrar tiempo y ordenar la información sin depender de herramientas cerradas.

---

## 🚀 Características

- Transcripción automática de audio en español (usando Whisper)
- Resumen generado con modelos de NLP
- Extracción de tareas, nombres y fechas mencionadas
- Exportación de resultados en archivos `.txt` y `.json`
- Todo funciona offline y con librerías de código abierto

---

## 📦 Requisitos

- Python 3.9 o superior
- Linux, macOS o Windows

---

## 🛠 Instalación

```bash
# Clona el repositorio
git clone https://github.com/TU_USUARIO/meet-whisperer.git
cd meet-whisperer

# Crea y activa el entorno virtual
python -m venv .venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows

# Instala las dependencias
pip install -r requirements.txt

# Descarga el modelo de idioma para spaCy
python -m spacy download es_core_news_md
```

## 🎧 Cómo usar

Colocá un archivo de audio .wav o .mp3 en la carpeta audio/.

Ejecutá el script principal con:

```bash
python main.py audio/mi_reunion.wav --model small
```
Cambiá mi_reunion.wav por el nombre de tu archivo.

Podés usar modelos Whisper como tiny, base, small, medium, o large (cuanto más grande, mejor precisión pero más lento y más RAM).


## 📁 Archivos generados

Después de ejecutar, encontrarás los resultados en la carpeta output/:

    transcripcion.txt → todo lo dicho, de forma literal

    resumen.txt → resumen automático

    tareas_entidades.json → nombres, fechas y tareas detectadas

## 📌 Ejemplo de uso

```bash
python main.py audio/demo_meet.mp3 --model small
```

📝 transcripcion.txt guardado en output/

📝 resumen.txt guardado en output/

📝 tareas_entidades.json guardado en output/

## 🧠 Roadmap futuro (ideas)

Captura de audio en tiempo real con micrófono

Interfaz web con Streamlit o Tkinter

Envío automático de resumen por correo

    Exportar a Markdown, Notion, Google Docs

## 📜 Licencia

Este proyecto es open-source y está bajo la licencia MIT.
Podés usarlo, modificarlo y compartirlo libremente.