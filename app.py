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
import license_manager

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

@app.before_request
def update_last_ping():
    global last_ping_time
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
    remitos = count_files(config.REMITOS_FOLDER)
    
    return jsonify({
        "watcher_running": watcher_manager.is_running,
        "stats": {
            "pending": pending,
            "processed": processed,
            "unrecognized": unrecognized,
            "remitos": remitos
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

def parse_error_log():
    log_path = os.path.join(config.REGISTROS_FOLDER, "errores_debug.txt")
    error_map = {}
    if not os.path.exists(log_path):
        return error_map
        
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        blocks = content.split("=========================================")
        for block in blocks:
            lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
            if not lines:
                continue
            
            timestamp = ""
            filename = ""
            error_type = ""
            details = []
            in_details = False
            
            for line in lines:
                if line.startswith("Fecha/Hora:"):
                    timestamp = line.replace("Fecha/Hora:", "").strip()
                elif line.startswith("Archivo:"):
                    filename = line.replace("Archivo:", "").strip()
                elif line.startswith("Tipo de Error:"):
                    error_type = line.replace("Tipo de Error:", "").strip()
                elif line.startswith("Detalles:"):
                    in_details = True
                elif in_details:
                    details.append(line)
                    
            if filename:
                error_map[filename] = {
                    "timestamp": timestamp,
                    "error_type": error_type or "No reconocido",
                    "details": "\n".join(details) if details else "Sin detalles adicionales."
                }
    except Exception as e:
        print(f"Error parseando errores_debug.txt: {e}")
        
    return error_map

@app.route('/api/unrecognized_invoices')
def unrecognized_invoices():
    error_map = parse_error_log()
    invoices = []
    if os.path.exists(config.UNRECOGNIZED_FOLDER):
        for root, dirs, files in os.walk(config.UNRECOGNIZED_FOLDER):
            for file in files:
                if file == '.gitkeep':
                    continue
                rel_path = os.path.relpath(os.path.join(root, file), config.UNRECOGNIZED_FOLDER).replace('\\', '/')
                err_info = error_map.get(file, {
                    "timestamp": "-",
                    "error_type": "No reconocido",
                    "details": "El comprobante no pudo ser clasificado como factura fiscal ni remito."
                })
                invoices.append({
                    "filename": file,
                    "error_type": err_info["error_type"],
                    "details": err_info["details"],
                    "date": err_info["timestamp"],
                    "path": rel_path
                })
    return jsonify(invoices)

@app.route('/api/unrecognized_file/<path:filepath>')
def serve_unrecognized_file(filepath):
    return send_from_directory(config.UNRECOGNIZED_FOLDER, filepath)

@app.route('/api/processed_remitos')
def processed_remitos():
    remitos = []
    if os.path.exists(config.REMITOS_FOLDER):
        for root, dirs, files in os.walk(config.REMITOS_FOLDER):
            for file in files:
                if file == '.gitkeep':
                    continue
                rel_path = os.path.relpath(os.path.join(root, file), config.REMITOS_FOLDER)
                parts = rel_path.replace('\\', '/').split('/')
                if len(parts) >= 3:
                    year, month = parts[0], parts[1]
                    filename = parts[-1]
                else:
                    year, month = "-", "-"
                    filename = file
                    
                remitos.append({
                    "filename": filename,
                    "supplier": "Remito / Comprobante No Fiscal",
                    "date": f"{month} {year}",
                    "path": rel_path.replace('\\', '/')
                })
    return jsonify(remitos)

@app.route('/api/remito_file/<path:filepath>')
def serve_remito_file(filepath):
    return send_from_directory(config.REMITOS_FOLDER, filepath)

@app.route('/api/user_history', methods=['GET', 'DELETE'])
def handle_user_history():
    from processor import get_user_history, clear_user_history
    if request.method == 'DELETE':
        success = clear_user_history()
        return jsonify({"success": success, "message": "Historial limpiado correctamente"})
    else:
        return jsonify(get_user_history())

@app.route('/api/file/<path:filepath>')
def serve_file(filepath):
    return send_from_directory(config.OUTPUT_FOLDER, filepath)

import zipfile

@app.route('/api/upload_csv', methods=['POST'])
def upload_csv():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No se envió ningún archivo"}), 400
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({"success": False, "message": "Ningún archivo seleccionado"}), 400
            
        raw_name = file.filename
        ext = os.path.splitext(raw_name)[1].lower()
        
        if ext in ['.csv', '.zip']:
            safe_name = secure_filename(raw_name)
            name_part, ext_part = os.path.splitext(safe_name)
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            
            if not name_part or len(name_part) < 2:
                final_name = f"upload_{timestamp}{ext_part}"
            else:
                final_name = f"{name_part}_{timestamp}{ext_part}"
                
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], final_name)
            
            try:
                file.save(file_path)
            except PermissionError:
                import uuid
                fallback_name = f"upload_{timestamp}_{uuid.uuid4().hex[:6]}{ext_part}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], fallback_name)
                file.save(file_path)
            
            if ext == '.zip':
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
            from update_suppliers import update_config_suppliers
            result = update_config_suppliers()
            
            # Reload processor indices and config so it recognizes new suppliers without restarting
            import processor
            processor.reload_config()
            
            if not result:
                result = {"success": True, "message": "Proceso finalizado correctamente."}
            elif isinstance(result, dict) and "success" not in result:
                result["success"] = True
            
            return jsonify(result)
            
        return jsonify({"success": False, "message": "Tipo de archivo inválido. Solo se admiten archivos CSV o ZIP."}), 400
    except Exception as e:
        print(f"Error en /api/upload_csv: {e}", flush=True)
        return jsonify({"success": False, "message": f"Error procesando archivo CSV: {str(e)}"}), 500

@app.route('/api/upload_invoice', methods=['POST'])
def upload_invoice():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No se envió ningún archivo"}), 400
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({"success": False, "message": "Ningún archivo seleccionado"}), 400
            
        valid_exts = tuple(config.ALLOWED_EXTENSIONS)
        if file and file.filename.lower().endswith(valid_exts):
            raw_name = file.filename
            safe_name = secure_filename(raw_name)
            name, ext = os.path.splitext(raw_name)
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            
            if not safe_name or len(safe_name) < 4:
                filename = f"factura_{timestamp}{ext.lower()}"
            else:
                s_name, s_ext = os.path.splitext(safe_name)
                filename = f"{s_name}_{timestamp}{s_ext}"
            
            file_path = os.path.join(config.INPUT_FOLDER, filename)
            file.save(file_path)
            
            # Iniciar el vigía automáticamente
            watcher_manager.start()
            
            return jsonify({"success": True, "message": "Factura cargada exitosamente"})
            
        return jsonify({"success": False, "message": "Tipo de archivo no permitido. Sube un PDF o Imagen."}), 400
    except Exception as e:
        print(f"Error en /api/upload_invoice: {e}", flush=True)
        return jsonify({"success": False, "message": f"Error al subir factura: {str(e)}"}), 500

@app.route('/api/license/status')
def license_status():
    force = request.args.get('force', 'false').lower() == 'true'
    status = license_manager.check_license_status(force_network=force)
    return jsonify(status)

@app.route('/api/watcher/start', methods=['POST'])
def start_watcher():
    lic_status = license_manager.check_license_status()
    if not lic_status.get("valid"):
        return jsonify({"success": False, "message": f"Licencia inactiva: {lic_status.get('message')}"})
    
    import processor
    processor.reload_config()
    
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

@app.route('/api/settings/cuit', methods=['POST'])
def save_cuit():
    data = request.get_json()
    cuit = data.get('cuit', '').strip()
    
    import re
    cuit_digits = re.sub(r'\D', '', cuit)
    if len(cuit_digits) == 11:
        cuit_formatted = f"{cuit_digits[:2]}-{cuit_digits[2:10]}-{cuit_digits[10]}"
    else:
        cuit_formatted = cuit
    
    try:
        cuit_path = os.path.join(config.BASE_DIR, 'my_cuit.txt')
        with open(cuit_path, 'w', encoding='utf-8') as f:
            f.write(cuit_formatted)
        config.MY_CUIT = cuit_formatted
        
        # Recargar para que processor también se entere (por si acaso)
        import processor
        processor.reload_config()
        
        return jsonify({"success": True, "message": "CUIT guardado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al guardar CUIT: {e}"}), 500

@app.route('/api/settings/get_cuit', methods=['GET'])
def get_cuit():
    cuit = getattr(config, 'MY_CUIT', '')
    return jsonify({"cuit": cuit})

# --- Rutas Bot Sincronización ARCA ---
import arca_bot

@app.route('/api/arca/credentials', methods=['GET', 'POST'])
def arca_credentials():
    if request.method == 'GET':
        creds = arca_bot.get_arca_credentials()
        if creds:
            return jsonify({
                "configured": True,
                "cuit": creds.get("cuit", ""),
                "representada": creds.get("representada", ""),
                "has_clave": bool(creds.get("clave")),
                "updated_at": creds.get("updated_at")
            })
        return jsonify({"configured": False, "cuit": "", "representada": "", "has_clave": False})
    
    data = request.json or {}
    cuit = data.get("cuit", "")
    clave = data.get("clave", "")
    representada = data.get("representada", "")
    try:
        arca_bot.save_arca_credentials(cuit, clave, representada)
        return jsonify({"success": True, "message": "Credenciales de ARCA guardadas de forma segura."})
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error guardando credenciales: {e}"}), 500

@app.route('/api/arca/sync', methods=['POST'])
def arca_sync():
    lic_status = license_manager.check_license_status()
    if not lic_status.get("valid"):
        return jsonify({"success": False, "message": f"Licencia inactiva: {lic_status.get('message')}"})
    
    creds = arca_bot.get_arca_credentials()
    if not creds or not creds.get("cuit") or not creds.get("clave"):
        return jsonify({"success": False, "message": "Debes configurar tu CUIT y Clave Fiscal de ARCA en Ajustes antes de sincronizar."}), 400

    status = arca_bot.get_bot_status()
    if status.get("running"):
        return jsonify({"success": False, "message": "La sincronización con ARCA ya está en curso."})

    def run_async():
        arca_bot.run_arca_bot_sync()

    thread = threading.Thread(target=run_async)
    thread.start()
    return jsonify({"success": True, "message": "Iniciando sincronización automatizada con ARCA..."})

@app.route('/api/arca/status', methods=['GET'])
def arca_status():
    return jsonify(arca_bot.get_bot_status())

@app.route('/api/arca/logs', methods=['GET'])
def arca_logs():
    return jsonify({"logs": arca_bot.get_arca_logs()})

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
    lic_status = license_manager.check_license_status()
    if not lic_status.get("valid"):
        return jsonify({"success": False, "message": f"Licencia inactiva: {lic_status.get('message')}"})
        
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
                kwargs = {}
                if getattr(subprocess, 'CREATE_NO_WINDOW', None) is not None:
                    kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                kwargs['startupinfo'] = startupinfo
                
                subprocess.run([naps2_path, '-o', output_path], **kwargs)
            except Exception as e:
                print(f"Error durante el escaneo con NAPS2: {e}", flush=True)
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
        time.sleep(15)
        while True:
            time.sleep(3)
            # Evitar apagar si hay tareas activas en segundo plano
            bot_running = False
            try:
                import arca_bot
                bot_running = arca_bot.get_bot_status().get("running", False)
            except Exception:
                pass
                
            if bot_running or watcher_manager.is_processing_batch:
                last_ping_time = time.time()
                
            # Si pasan más de 25 segundos sin recibir pings ni peticiones, se cerró la pestaña web
            if time.time() - last_ping_time > 25:
                print("No se detectó actividad web. Apagando servidor...", flush=True)
                try:
                    watcher_manager.stop()
                except Exception:
                    pass
                os._exit(0)
                
    threading.Thread(target=check_timeout, daemon=True).start()

    print("\nIniciando la aplicación web...")

    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000/')

    Timer(1, open_browser).start()

    app.run(debug=False, port=5000, use_reloader=False, threaded=True)
