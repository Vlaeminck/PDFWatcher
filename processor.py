import os
import re
import shutil
import time
import datetime
import pdfplumber
from config import SUPPLIERS, OUTPUT_FOLDER, UNRECOGNIZED_FOLDER

MONTHS_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error leyendo PDF {pdf_path}: {e}")
    return text.lower()

def wait_for_file_ready(file_path, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not os.path.exists(file_path):
            return False
        try:
            # Intentar renombrar el archivo a sí mismo para verificar si está bloqueado por otro proceso
            os.rename(file_path, file_path)
            return True
        except OSError:
            time.sleep(0.5)
    return False

def process_invoice(file_path):
    print(f"\nProcesando: {file_path}")
    
    # Esperar hasta que el archivo deje de estar bloqueado por el escáner (hasta 10 segundos)
    is_ready = wait_for_file_ready(file_path)
    
    if not is_ready:
        if not os.path.exists(file_path):
            print(f"El archivo {file_path} desapareció antes de poder leerlo. Probablemente era un archivo temporal del escáner.")
        else:
            print(f"El archivo {file_path} sigue bloqueado después de 10 segundos. Saltando.")
        return
    
    text = extract_text_from_pdf(file_path)
    
    if not text.strip():
        print("No se encontró texto en el PDF. ¿Quizás el OCR falló o no se aplicó? Moviendo a no reconocidas.")
        move_to_unrecognized(file_path, "Desconocido-sin-texto.pdf")
        return
        
    print(f"--- Texto detectado (primeros 200 caracteres) ---\n{text[:200]}...")
    
    supplier_found = None
    invoice_number = None
    
    for supplier_name, data in SUPPLIERS.items():
        # Verificar si alguna palabra clave coincide
        if any(keyword.lower() in text for keyword in data["keywords"]):
            supplier_found = supplier_name
            # Buscar el número de factura
            match = re.search(data["invoice_regex"], text)
            if match:
                invoice_number = match.group(1).replace(" ", "") # Quitamos espacios
            break
            
    if supplier_found:
        if invoice_number:
            new_filename = f"{supplier_found.lower()}-{invoice_number}.pdf"
            move_to_processed(file_path, supplier_found, new_filename)
        else:
            # Proveedor reconocido, pero número no procesado
            new_filename = f"{supplier_found}-sin-reconocer.pdf"
            move_to_unrecognized(file_path, new_filename)
    else:
        # Completamente desconocido
        move_to_unrecognized(file_path, "Desconocido-sin-reconocer.pdf")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_unique_filename(destination_dir, filename):
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(destination_dir, new_filename)):
        new_filename = f"{name}_{counter}{ext}"
        counter += 1
    return new_filename

def move_to_processed(file_path, supplier, new_filename):
    now = datetime.datetime.now()
    year = str(now.year)
    month_name = MONTHS_ES[now.month]
    
    # Estructura: Facturas_Procesadas / Año / Mes / Proveedor
    supplier_dir = os.path.join(OUTPUT_FOLDER, year, month_name, supplier)
    ensure_dir(supplier_dir)
    
    unique_filename = generate_unique_filename(supplier_dir, new_filename)
    dest_path = os.path.join(supplier_dir, unique_filename)
    
    try:
        shutil.move(file_path, dest_path)
        print(f"¡Éxito! Movido a: {dest_path}")
    except Exception as e:
        print(f"Error moviendo archivo: {e}")

def move_to_unrecognized(file_path, new_filename):
    ensure_dir(UNRECOGNIZED_FOLDER)
    unique_filename = generate_unique_filename(UNRECOGNIZED_FOLDER, new_filename)
    dest_path = os.path.join(UNRECOGNIZED_FOLDER, unique_filename)
    
    try:
        shutil.move(file_path, dest_path)
        print(f"No reconocido. Movido a: {dest_path}")
    except Exception as e:
        print(f"Error moviendo archivo: {e}")
