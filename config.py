import os
import sys

# Rutas Base (Relativas al proyecto para pruebas, pueden cambiarse a C:\...)
if getattr(sys, 'frozen', False):
    # Si se ejecuta como .exe compilado por PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si se ejecuta el script normal
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

API_KEY_FILE = os.path.join(BASE_DIR, 'api_key.txt')
if os.path.exists(API_KEY_FILE):
    try:
        with open(API_KEY_FILE, 'r', encoding='utf-8') as f:
            AI_API_KEY = f.read().strip()
    except Exception:
        AI_API_KEY = ""
else:
    AI_API_KEY = ""

INPUT_FOLDER = os.path.join(BASE_DIR, "Facturas_A_Procesar")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "Facturas_Procesadas")
UNRECOGNIZED_FOLDER = os.path.join(BASE_DIR, "Facturas_No_Reconocidas")
CSV_ARCA_FOLDER = os.path.join(BASE_DIR, "CSV ARCA")
REGISTROS_FOLDER = os.path.join(BASE_DIR, "registros")

# Asegurar que las carpetas existan (se crean automáticamente si no)
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(UNRECOGNIZED_FOLDER, exist_ok=True)
os.makedirs(CSV_ARCA_FOLDER, exist_ok=True)
os.makedirs(REGISTROS_FOLDER, exist_ok=True)

# Extensiones a monitorear
ALLOWED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"]

import json

SUPPLIERS_FILE = os.path.join(BASE_DIR, "suppliers.json")

# Diccionario de Proveedores y Expresiones Regulares
if os.path.exists(SUPPLIERS_FILE):
    try:
        with open(SUPPLIERS_FILE, 'r', encoding='utf-8') as f:
            SUPPLIERS = json.load(f)
    except Exception as e:
        print(f"Error cargando {SUPPLIERS_FILE}: {e}")
        SUPPLIERS = {}
else:
    SUPPLIERS = {}

