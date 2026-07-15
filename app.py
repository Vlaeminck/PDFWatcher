import sys
import os
import time
import threading
import importlib
from flask import Flask, render_template, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from watcher import watcher_manager
from update_suppliers import update_config_suppliers
import doctor
import config

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = config.CSV_ARCA_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max

# Control de ciclo de vida (Auto-Apagado)
last_ping_time = time.time()

@app.route('/api/ping', methods=['POST'])
def ping():
    global last_ping_time
    last_ping_time = time.time()
    return jsonify({"status": "ok"})

@app.after_request
def add_header(response):
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

def count_files(directory):
    if not os.path.exists(directory):
        return 0
    valid_exts = tuple(config.ALLOWED_EXTENSIONS)
    return sum(1 for root, dirs, files in os.walk(directory) for f in files if f.lower().endswith(valid_exts))

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
                if file == '.gitkeep':
                    continue
                rel_path = os.path.relpath(os.path.join(root, file), config.OUTPUT_FOLDER)
                parts = rel_path.replace('\\', '/').split('/')
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

import zipfile

@app.route('/api/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No se envió ningún archivo"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "Ningún archivo seleccionado"}), 400
        
    if file and (file.filename.lower().endswith('.csv') or file.filename.lower().endswith('.zip')):
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        if filename.lower().endswith('.zip'):
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    for zip_info in zip_ref.infolist():
                        if zip_info.filename.lower().endswith('.csv'):
                            zip_info.filename = os.path.basename(zip_info.filename)
                            zip_ref.extract(zip_info, app.config['UPLOAD_FOLDER'])
                os.remove(file_path)
            except Exception as e:
                return jsonify({"success": False, "message": f"Error extrayendo ZIP: {e}"}), 500

        # Trigger update
        result = update_config_suppliers()
        if not result:
            result = {"success": True, "message": "Proceso finalizado correctamente."}
        
        return jsonify(result)
        
    return jsonify({"success": False, "message": "Tipo de archivo inválido. Solo se admiten archivos CSV o ZIP."}), 400

@app.route('/api/upload_invoice', methods=['POST'])
def upload_invoice():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No se envió ningún archivo"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "Ningún archivo seleccionado"}), 400
        
    valid_exts = tuple(config.ALLOWED_EXTENSIONS)
    if file and file.filename.lower().endswith(valid_exts):
        filename = secure_filename(file.filename)
        # Añadir timestamp para evitar sobreescribir archivos con el mismo nombre
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_{timestamp}{ext}"
        
        file_path = os.path.join(config.INPUT_FOLDER, new_filename)
        file.save(file_path)
        
        # Iniciar el vigía automáticamente
        watcher_manager.start()
        
        return jsonify({"success": True, "message": "Factura cargada exitosamente"})
        
    return jsonify({"success": False, "message": "Tipo de archivo no permitido. Sube un PDF o Imagen."}), 400

@app.route('/api/watcher/start', methods=['POST'])
def start_watcher():
    success, msg = watcher_manager.start()
    return jsonify({"success": success, "message": msg})

@app.route('/api/watcher/stop', methods=['POST'])
def stop_watcher():
    success, msg = watcher_manager.stop()
    return jsonify({"success": success, "message": msg})

@app.route('/api/settings/api_key', methods=['POST'])
def save_api_key():
    data = request.get_json()
    api_key = data.get('api_key', '').strip()
    
    if not api_key:
        return jsonify({"success": False, "message": "La API Key no puede estar vacía"}), 400
        
    try:
        # Save to api_key.txt for compiled environments
        api_key_path = os.path.join(config.BASE_DIR, 'api_key.txt')
        obfuscated_key = config.obfuscate_key(api_key)
        with open(api_key_path, 'w', encoding='utf-8') as f:
            f.write(obfuscated_key)
        config.AI_API_KEY = api_key
        return jsonify({"success": True, "message": "API Key guardada correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al guardar la clave: {e}"}), 500

@app.route('/api/settings/get_api_key', methods=['GET'])
def get_api_key():
    key = getattr(config, 'AI_API_KEY', '')
    if key == "TU_API_KEY_AQUI":
        key = ""
    return jsonify({"api_key": key})

@app.route('/api/doctor/scan', methods=['GET'])
def doctor_scan():
    try:
        anomalies = doctor.scan_database()
        return jsonify({"success": True, "anomalies": anomalies})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/doctor/fix', methods=['POST'])
def doctor_fix():
    try:
        result = doctor.fix_database()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

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

    def check_timeout():
        global last_ping_time
        # Esperar 10 segundos inicialmente para dar tiempo a que abra el navegador
        time.sleep(10)
        while True:
            time.sleep(3)
            # Si pasan más de 15 segundos sin ping, significa que se cerró la pestaña web
            if time.time() - last_ping_time > 15:
                print("No se detectó actividad web. Apagando servidor...")
                try:
                    watcher_manager.stop()
                except:
                    pass
                os._exit(0)
                
    threading.Thread(target=check_timeout, daemon=True).start()

    print("\nIniciando la aplicación web...")

    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000/')

    # Abre el navegador automáticamente tras 1 segundo
    Timer(1, open_browser).start()

    # use_reloader=False prevents watchdog observer from starting twice if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
