import os
import importlib
from flask import Flask, render_template, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from watcher import watcher_manager
from update_suppliers import update_config_suppliers
import config

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.CSV_ARCA_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max

def count_files(directory):
    if not os.path.exists(directory):
        return 0
    return sum(1 for root, dirs, files in os.walk(directory) for f in files if f.lower() not in ['.gitkeep', '.gitignore', 'desktop.ini'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    pending = count_files(config.INPUT_FOLDER)
    processed = count_files(config.OUTPUT_FOLDER)
    unrecognized = count_files(config.UNRECOGNIZED_FOLDER)
    
    return jsonify({
        "watcher_running": watcher_manager.is_running,
        "stats": {
            "pending": pending,
            "processed": processed,
            "unrecognized": unrecognized
        }
    })

@app.route('/api/suppliers')
def get_suppliers():
    importlib.reload(config)
    suppliers = []
    for name, data in config.SUPPLIERS.items():
        suppliers.append({
            "name": name,
            "keywords": data.get("keywords", []),
            "regex": data.get("invoice_regex", "")
        })
    return jsonify(suppliers)

@app.route('/api/progress')
def progress():
    return jsonify({
        "is_processing_batch": watcher_manager.is_processing_batch,
        "is_ai_processing": watcher_manager.is_ai_processing,
        "total": watcher_manager.total_files_to_process,
        "processed": watcher_manager.files_processed_so_far
    })

@app.route('/api/processed_invoices')
def processed_invoices():
    invoices = []
    if os.path.exists(config.OUTPUT_FOLDER):
        for root, dirs, files in os.walk(config.OUTPUT_FOLDER):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), config.OUTPUT_FOLDER)
                parts = rel_path.split(os.sep)
                if len(parts) >= 4:
                    year, month, supplier = parts[0], parts[1], parts[2]
                    filename = parts[-1]
                else:
                    year, month, supplier = "-", "-", "Desconocido"
                    filename = file
                    
                invoices.append({
                    "filename": filename,
                    "supplier": supplier,
                    "date": f"{month} {year}",
                    "path": rel_path.replace('\\', '/')
                })
    return jsonify(invoices)

@app.route('/api/file/<path:filepath>')
def serve_file(filepath):
    return send_from_directory(config.OUTPUT_FOLDER, filepath)

@app.route('/api/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No se envió ningún archivo"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "Ningún archivo seleccionado"}), 400
        
    if file and file.filename.lower().endswith('.csv'):
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Trigger update
        result = update_config_suppliers()
        if not result:
            result = {"success": True, "message": "Proceso finalizado. Revisa la consola para más detalles."}
        
        return jsonify(result)
        
    return jsonify({"success": False, "message": "Tipo de archivo inválido. Solo se admiten archivos CSV."}), 400

@app.route('/api/watcher/start', methods=['POST'])
def start_watcher():
    success, msg = watcher_manager.start()
    return jsonify({"success": success, "message": msg})

@app.route('/api/watcher/stop', methods=['POST'])
def stop_watcher():
    success, msg = watcher_manager.stop()
    return jsonify({"success": success, "message": msg})

import threading

scanning_lock = threading.Lock()

@app.route('/api/open_scanner', methods=['POST'])
def open_scanner():
    import subprocess
    import os
    import time
    from config import INPUT_FOLDER
    
    if not scanning_lock.acquire(blocking=False):
        return jsonify({"success": False, "message": "El escáner ya está en uso. Por favor espera a que termine el escaneo actual."})
        
    try:
        # Generar nombre de archivo único
        filename = f"Escáner_{time.strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(INPUT_FOLDER, filename)
        
        naps2_path = r"C:\Program Files\NAPS2\NAPS2.Console.exe"
        
        # Iniciar el vigía si no estaba corriendo (durará 5 min sin actividad)
        watcher_manager.start()
        
        def run_scanner():
            try:
                subprocess.run([naps2_path, '-o', output_path])
            finally:
                scanning_lock.release()
                
        # Ejecutar de fondo sin bloquear el servidor web
        thread = threading.Thread(target=run_scanner)
        thread.start()
        
        return jsonify({"success": True, "message": "Iniciando escaneo silencioso con NAPS2..."})
    except Exception as e:
        scanning_lock.release()
        return jsonify({"success": False, "message": f"Error: {e}"})


if __name__ == '__main__':
    import webbrowser
    from threading import Timer
    import config
    import sys
    import os
    import subprocess

    def check_and_install_dependencies():
        tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        naps2_path = r"C:\Program Files\NAPS2\NAPS2.Console.exe"
        
        missing = []
        if not os.path.exists(tesseract_path):
            missing.append(("Tesseract OCR", "UB-Mannheim.TesseractOCR"))
        if not os.path.exists(naps2_path):
            missing.append(("NAPS2", "NAPS2.NAPS2"))
            
        if missing:
            names = ", ".join([name for name, _ in missing])
            try:
                import ctypes
                msg = f"PDFWatcher necesita instalar componentes adicionales para funcionar correctamente:\n\n{names}\n\nSe abrirá una ventana de consola (pantalla negra) mostrando el progreso de la descarga e instalación. ¡NO LA CIERRES!\nPor favor, acepta los permisos de administrador (UAC) si Windows te los pide.\n\nEl programa se abrirá automáticamente al terminar. ¡Gracias por tu paciencia!"
                ctypes.windll.user32.MessageBoxW(0, msg, "Instalando Dependencias de PDFWatcher", 0x40 | 0x0)
            except Exception:
                pass
            
            print("\n" + "="*65)
            print("⏳ [Instalación Automática] Descargando dependencias del sistema")
            print("="*65)
            for name, pkg_id in missing:
                print(f"Descargando e instalando {name} (por favor espere)...")
                try:
                    # En modo --windowed, forzamos la creacion de una consola visible para que el usuario vea el progreso
                    creationflags = 0
                    if hasattr(subprocess, 'CREATE_NEW_CONSOLE'):
                        creationflags = subprocess.CREATE_NEW_CONSOLE
                        
                    subprocess.run(["winget", "install", "--id", pkg_id, "-e", "--accept-package-agreements", "--accept-source-agreements"], check=True, creationflags=creationflags)
                    print(f"[✔] {name} instalado correctamente.")
                except Exception as e:
                    print(f"[X] Error instalando {name}. Puede que requiera instalación manual. Error: {e}")
            print("="*65 + "\n")

    check_and_install_dependencies()

    # Preguntar por la API Key si no está configurada
    if not getattr(config, 'AI_API_KEY', '').strip():
        try:
            # En modo --windowed con PyInstaller, sys.stdin no existe y lanza RuntimeError
            print("\n" + "="*65)
            print("🤖 [Opcional] Rescate con Inteligencia Artificial (Gemini)")
            print("="*65)
            print("¿Deseas configurar una clave API de Gemini para poder leer facturas")
            print("borrosas o difíciles automáticamente?")
            print("\n[SEGURIDAD]: Esta clave se guarda EXCLUSIVAMENTE a nivel local en tu")
            print("computadora (en el archivo config.py). NO se subirá a ningún lado,")
            print("NO quedará expuesta en la web, y respeta todas las normas de privacidad.")
            print("Tus datos sensibles nunca saldrán de tu PC de forma insegura.")
            print("="*65)
            
            resp = input("¿Tienes una clave y deseas usarla? (S/N): ").strip().lower()
            if resp == 's':
                api_key = input("Pega tu API Key de Gemini: ").strip()
                if api_key:
                    try:
                        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.py')
                        with open(config_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if 'AI_API_KEY' in content:
                            import re
                            content = re.sub(r'AI_API_KEY\s*=\s*["\'].*?["\']', f'AI_API_KEY = "{api_key}"', content)
                        else:
                            content = content.replace("import os", f'import os\n\nAI_API_KEY = "{api_key}"\n', 1)
                        
                        with open(config_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print("\n[✔] ¡Excelente! Clave guardada de forma segura en config.py.")
                        
                        # Cargarla en memoria para esta ejecución
                        config.AI_API_KEY = api_key
                    except Exception as e:
                        print(f"\n[X] Error al guardar la clave: {e}")
                else:
                    print("\n[!] No ingresaste ninguna clave. Continuando sin IA...")
            else:
                print("\n[!] Entendido. Continuando sin IA. (Puedes agregarla luego manualmente en config.py)")
        except RuntimeError as e:
            if "lost sys.stdin" in str(e):
                pass # Ignorar el error si estamos en modo --windowed sin consola
            else:
                print(f"Error de input: {e}")
        except Exception:
            pass # Ignorar otros errores de stdin
            
    print("\nIniciando la aplicación web...")

    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000/')

    # Abre el navegador automáticamente tras 1 segundo
    Timer(1, open_browser).start()

    # use_reloader=False prevents watchdog observer from starting twice if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
