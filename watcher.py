import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from procesador.core import procesar_transcripcion
import os

class TxtEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".txt"):
            print(f"Nuevo archivo detectado: {event.src_path}")
            procesar_transcripcion(event.src_path)

def iniciar_watcher():
    path = "input"
    os.makedirs(path, exist_ok=True)
    event_handler = TxtEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=False)
    observer.start()
    print(f"Monitoreando carpeta: {path}/")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
