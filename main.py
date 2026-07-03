import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from processor import process_invoice
from config import INPUT_FOLDER, ALLOWED_EXTENSIONS

class InvoiceHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = event.src_path
        _, ext = os.path.splitext(file_path)
        
        if ext.lower() in ALLOWED_EXTENSIONS:
            print(f"Nuevo PDF detectado: {file_path}")
            try:
                process_invoice(file_path)
            except Exception as e:
                print(f"Error al procesar {file_path}: {e}")

def main():
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"Carpeta de entrada creada: {INPUT_FOLDER}")
        
    event_handler = InvoiceHandler()
    observer = Observer()
    observer.schedule(event_handler, path=INPUT_FOLDER, recursive=False)
    
    print(f"Iniciando el Vigía en {INPUT_FOLDER}...")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nVigía detenido.")
        
    observer.join()

if __name__ == "__main__":
    main()
