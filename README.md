# 🧠 Meet Whisperer - Procesador de Transcripciones de Reuniones IT

**Meet Whisperer** es una herramienta inteligente para transformar transcripciones caóticas de reuniones en resúmenes claros, estructurados y útiles para equipos de tecnología, datos y producto.

Detecta tareas, decisiones, ambigüedades, corrige errores técnicos de transcripción y genera reportes profesionales en segundos.

---

## 🚀 Características principales

- ✅ Corrección automática de términos técnicos mal transcriptos.
- ✅ Generación de resumen ejecutivo en formato Markdown.
- ✅ Identificación de tareas confirmadas y sugeridas.
- ✅ Detección de decisiones y ambigüedades no resueltas.
- ✅ Interfaz gráfica minimalista para operar sin código.
- ✅ 100% offline: sin enviar datos a servidores externos.
- ✅ Basado en modelos LLM locales (Mistral 7B Instruct GGUF).

---

## 📁 Estructura del proyecto

```
meet-whisperer/
│
├── core.py                      # Lógica principal de procesamiento y resumen
├── main.py                      # Interfaz gráfica con tkinter
├── watcher.py                   # Alternativa para monitoreo automático de la carpeta input
│
├── input/                       # Colocar aquí las transcripciones (.txt)
│   └── test.txt
│
├── output/                      # Aquí se generarán los resúmenes .md
│   └── test_resumen_20250715_152309.md
│
├── procesador/
│   └── glosario_tecnico.json   # Glosario con errores comunes y sus correcciones
│
├── models/
│   └── mistral/                # Carpeta con modelo GGUF local (Mistral 7B)
│       └── mistral-7b-instruct-v0.1.Q4_K_M.gguf
```

---

## 📅 Requisitos

Instalación de dependencias:
```bash
pip install -r requirements.txt
```

---

## ⚖️ Uso del programa (modo visual)

1. Ejecutá `main.py`:
```bash
python main.py
```
2. Se abrirá una pequeña ventana. Seleccioná un archivo `.txt` desde tu computadora.
3. El sistema lo procesará con el modelo local.
4. Al terminar, aparecerá un mensaje y un botón para abrir directamente el resumen generado.

---

## 🎨 Ejemplo de salida
Archivo generado en `output/test_resumen_YYYYMMDD_HHMMSS.md` con formato como:

```markdown
# Resumen de la reunión

**Archivo procesado**: test.txt

**Fecha de procesamiento**: 2025-07-15 15:23:04

## Resumen Ejecutivo
- ...

## Tareas Confirmadas
| Tarea | Responsable | Fecha |
|-------|-------------|-------|
| ...   | ...         | ...   |

## Tareas Sugeridas (no confirmadas)
| Tarea | Responsable posible | Comentario |
|-------|----------------------|------------|
| ...   | ...                  | ...        |

## Decisiones
- ...

## Ambigüedades y Temas No Resueltos
- ...
```

---

## 🎓 Autor

Mauro Pereyra

---

## 🌟 Futuro
- Exportación a CSV/Excel.
- Clasificación de oradores.
- Detección de sentimientos y tono.
- API local y versión web para equipos.

---

📊 Compartilo en LinkedIn o con tus colegas si te resulta útil :)
