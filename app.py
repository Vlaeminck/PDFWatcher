import os
import importlib
from flask import Flask, render_template, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from watcher import watcher_manager
from update_suppliers import update_config_suppliers
import config

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, "CSV ARCA")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max

def count_files(directory):
    if not os.path.exists(directory):
        return 0
    return sum(1 for root, dirs, files in os.walk(directory) for f in files)

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

@app.route('/api/open_scanner', methods=['POST'])
def open_scanner():
    import subprocess
    import os
    import time
    from config import INPUT_FOLDER
    try:
        # Generar nombre de archivo único
        filename = f"Escáner_{time.strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(INPUT_FOLDER, filename)
        
        naps2_path = r"C:\Program Files\NAPS2\NAPS2.Console.exe"
        
        # Ejecutar de fondo sin bloquear el servidor web
        subprocess.Popen([naps2_path, '-o', output_path])
        return jsonify({"success": True, "message": "Iniciando escaneo silencioso con NAPS2..."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {e}"})
@app.route('/api/test_paint', methods=['POST'])
def test_paint():
    import os
    try:
        os.startfile('mspaint.exe')
        return jsonify({"success": True, "message": "Paint abierto"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {e}"})

if __name__ == '__main__':
    # use_reloader=False prevents watchdog observer from starting twice if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
