import os
import re
import shutil
import time
import datetime
import pdfplumber
import pypdfium2 as pdfium
from PIL import Image
from config import SUPPLIERS, OUTPUT_FOLDER, UNRECOGNIZED_FOLDER

MONTHS_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Ruta al ejecutable de Tesseract (instalado en Windows)
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def get_tesseract():
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    return pytesseract

def extract_text_via_ocr_image(image_path):
    """Aplica OCR a un archivo de imagen directamente."""
    img = None
    try:
        pytesseract = get_tesseract()
        img = Image.open(image_path)
        # lang='spa' para español, '+eng' agrega inglés como fallback
        text = pytesseract.image_to_string(img, lang='spa+eng', config='--psm 3')
        return text.lower()
    except Exception as e:
        print(f"Error haciendo OCR en la imagen {image_path}: {e}", flush=True)
        return ""
    finally:
        if img:
            img.close()

def extract_text_via_ocr_pdf(pdf_path):
    """Convierte páginas de PDF a imagen y aplica OCR."""
    text_parts = []
    doc = None
    try:
        pytesseract = get_tesseract()
        doc = pdfium.PdfDocument(pdf_path)
        for page in doc:
            # Renderizar a 200 DPI (scale=200/72)
            bitmap = page.render(scale=200/72)
            pil_img = bitmap.to_pil()
            text = pytesseract.image_to_string(pil_img, lang='spa+eng', config='--psm 3')
            text_parts.append(text)
    except Exception as e:
        print(f"Error haciendo OCR en el PDF {pdf_path}: {e}", flush=True)
    finally:
        if doc:
            doc.close()
    return "\n".join(text_parts).lower()

def extract_text_from_pdf(pdf_path):
    """Extrae texto directamente de la capa de texto del PDF."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error leyendo PDF {pdf_path}: {e}", flush=True)
    return text.lower()

def extract_text(file_path):
    """Selecciona el método de extracción según el tipo de archivo."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.pdf':
        # 1. Intentar extracción directa de texto
        text = extract_text_from_pdf(file_path)
        if text.strip():
            return text
        # 2. Si no hay texto, aplicar OCR al PDF renderizado
        print("PDF sin capa de texto. Aplicando OCR local (Tesseract)...", flush=True)
        return extract_text_via_ocr_pdf(file_path)
    else:
        # Es un archivo de imagen directo (.png, .jpg, etc.)
        print("Imagen detectada. Aplicando OCR local (Tesseract)...", flush=True)
        return extract_text_via_ocr_image(file_path)

# ---------------------------------------------------------------------------
# Motor de matching: CUIT primero, keywords como fallback
# ---------------------------------------------------------------------------

def extract_cuits_from_text(text):
    """
    Extrae todos los CUITs encontrados en el texto, tolerando guiones con posibles espacios intermedios.
    Soporta formato con guiones (ej. 30 - 70721038 - 5) y sin guiones (30707210385).
    Devuelve lista de strings de 11 dígitos, en orden de aparición.
    """
    found = []
    seen = set()

    # Formato con guiones y posibles espacios: XX - XXXXXXXX - X
    for m in re.finditer(r'\b(\d{2})\s*-\s*(\d{8})\s*-\s*(\d)\b', text):
        digits = m.group(1) + m.group(2) + m.group(3)
        if digits not in seen:
            found.append(digits)
            seen.add(digits)

    # Formato sin guiones: 11 dígitos con prefijo válido de CUIT argentino
    for m in re.finditer(r'\b((?:20|23|24|27|30|33|34)\d{9})\b', text):
        digits = m.group(1)
        if digits not in seen:
            found.append(digits)
            seen.add(digits)

    return found

def load_arca_csvs():
    """
    Lee todos los archivos CSV en la carpeta CSV ARCA y construye un índice por CAE.
    """
    cae_index = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_folder = os.path.join(base_dir, "CSV ARCA")
    if not os.path.exists(csv_folder):
        return cae_index

    import csv
    import io

    csv_files = [os.path.join(csv_folder, f) for f in os.listdir(csv_folder) if f.lower().endswith('.csv')]
    for file_path in csv_files:
        try:
            # Leer archivo de forma segura con varias codificaciones
            content = None
            encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-8-sig']
            for encoding in encodings:
                try:
                    with open(file_path, mode='r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                continue

            reader = csv.reader(io.StringIO(content), delimiter=';')
            rows = list(reader)
            if not rows:
                continue

            header = [col.strip().replace('"', '') for col in rows[0]]
            
            try:
                cuit_idx = header.index("Nro. Doc. Emisor")
                name_idx = header.index("Denominación Emisor")
                cae_idx = header.index("Cód. Autorización")
                pv_idx = header.index("Punto de Venta")
                num_idx = header.index("Número Desde")
                total_idx = header.index("Imp. Total")
                date_idx = header.index("Fecha de Emisión")
            except ValueError:
                cuit_idx = 7
                name_idx = 8
                cae_idx = 5
                pv_idx = 2
                num_idx = 3
                total_idx = 29
                date_idx = 0

            for row in rows[1:]:
                if len(row) <= max(cuit_idx, name_idx, cae_idx, pv_idx, num_idx, total_idx, date_idx):
                    continue
                
                cuit = re.sub(r'\D', '', row[cuit_idx].strip().replace('"', ''))
                name = row[name_idx].strip().replace('"', '')
                cae = row[cae_idx].strip().replace('"', '')
                pv = row[pv_idx].strip().replace('"', '')
                num = row[num_idx].strip().replace('"', '')
                total = row[total_idx].strip().replace('"', '')
                date_val = row[date_idx].strip().replace('"', '') if len(row) > date_idx else None

                if cae:
                    cae_index[cae] = {
                        "cuit": cuit,
                        "name": name,
                        "pv": pv,
                        "num": num,
                        "total": total,
                        "date": date_val
                    }
        except Exception as e:
            print(f"Error procesando CSV {os.path.basename(file_path)}: {e}", flush=True)

    return cae_index

def normalize_string(s):
    """Normaliza un texto para comparaciones de keywords robustas."""
    s = s.lower()
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def build_cuit_to_supplier_map():
    """
    Construye un mapa {cuit_digits: supplier_name_in_config} buscando:
    1. En los keywords de SUPPLIERS.
    2. En los CSVs de ARCA (cruzando el nombre del emisor del CSV con los keywords/nombres de SUPPLIERS).
    """
    cuit_map = {}
    
    # 1. Primero, mapear por los CUITs declarados explícitamente en keywords
    for supplier_name, data in SUPPLIERS.items():
        for kw in data.get("keywords", []):
            digits = re.sub(r'\D', '', kw)
            if len(digits) == 11:
                cuit_map[digits] = supplier_name

    # 2. Segundo, leer los CSV de ARCA y cruzar por nombre
    kw_to_supplier = {}
    for supplier_name, data in SUPPLIERS.items():
        kw_to_supplier[normalize_string(supplier_name)] = supplier_name
        for kw in data.get("keywords", []):
            kw_norm = normalize_string(kw)
            if not kw_norm.isdigit():
                kw_to_supplier[kw_norm] = supplier_name
                
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_folder = os.path.join(base_dir, "CSV ARCA")
    if os.path.exists(csv_folder):
        import csv
        import io
        csv_files = [os.path.join(csv_folder, f) for f in os.listdir(csv_folder) if f.lower().endswith('.csv')]
        for file_path in csv_files:
            try:
                content = None
                encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-8-sig']
                for encoding in encodings:
                    try:
                        with open(file_path, mode='r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                if content is None:
                    continue
                
                reader = csv.reader(io.StringIO(content), delimiter=';')
                rows = list(reader)
                if len(rows) < 2:
                    continue
                
                header = [col.strip().replace('"', '') for col in rows[0]]
                try:
                    cuit_idx = header.index("Nro. Doc. Emisor")
                    name_idx = header.index("Denominación Emisor")
                except ValueError:
                    cuit_idx = 7
                    name_idx = 8
                    
                for row in rows[1:]:
                    if len(row) <= max(cuit_idx, name_idx):
                        continue
                    cuit = re.sub(r'\D', '', row[cuit_idx].strip().replace('"', ''))
                    name = row[name_idx].strip().replace('"', '')
                    
                    if len(cuit) == 11 and cuit not in cuit_map:
                        name_norm = normalize_string(name)
                        if name_norm in kw_to_supplier:
                            cuit_map[cuit] = kw_to_supplier[name_norm]
                        else:
                            for kw_norm, supplier_name in kw_to_supplier.items():
                                if len(name_norm) > 4 and (name_norm in kw_norm or kw_norm in name_norm):
                                    cuit_map[cuit] = supplier_name
                                    break
            except Exception as e:
                pass
                
    return cuit_map

# Índices globales construidos una sola vez
_CUIT_INDEX = build_cuit_to_supplier_map()
_CAE_INDEX = load_arca_csvs()

def find_supplier(text):
    """
    Identifica el proveedor con la siguiente prioridad:
      1. CAE encontrado en el texto y coincidente en ARCA CSV
      2. CUIT encontrado en el texto  →  match exacto e inequívoco
      3. Keywords del diccionario     →  smart match (mayor longitud de keyword coincidente)
    Devuelve (supplier_name, match_method, csv_info) o (None, None, None).
    """
    # Normalizar el texto completo de la factura para matching de keywords
    normalized_text = normalize_string(text)

    # --- Tier 1: matching por CAE ---
    # Un CAE es un número de 14 dígitos en las facturas electrónicas argentinas
    caes_in_text = re.findall(r'\b\d{14}\b', text)
    for cae in caes_in_text:
        if cae in _CAE_INDEX:
            csv_info = _CAE_INDEX[cae]
            cuit = csv_info["cuit"]
            if cuit in _CUIT_INDEX:
                supplier = _CUIT_INDEX[cuit]
                print(f"  [OK] Proveedor identificado por CAE {cae} de ARCA: {supplier}", flush=True)
                return supplier, "CAE", csv_info

    # --- Tier 2: matching por CUIT ---
    cuits_in_text = extract_cuits_from_text(text)
    for cuit in cuits_in_text:
        if cuit in _CUIT_INDEX:
            supplier = _CUIT_INDEX[cuit]
            cuit_fmt = f"{cuit[:2]}-{cuit[2:10]}-{cuit[10]}"
            print(f"  [OK] Proveedor identificado por CUIT {cuit_fmt}: {supplier}", flush=True)
            return supplier, "CUIT", None

    # --- Tier 3: matching por keywords (smart match seleccionando la coincidencia más larga) ---
    best_supplier = None
    longest_keyword_len = 0
    matched_keyword = ""

    for supplier_name, data in SUPPLIERS.items():
        for kw in data.get("keywords", []):
            kw_normalized = normalize_string(kw)
            # Evitar que los CUITs o números interfieran en el matching textual
            if kw_normalized.isdigit() or re.match(r'^\d{2}\s\d{8}\s\d$', kw_normalized):
                continue
            if kw_normalized in normalized_text:
                if len(kw_normalized) > longest_keyword_len:
                    longest_keyword_len = len(kw_normalized)
                    best_supplier = supplier_name
                    matched_keyword = kw_normalized

    if best_supplier:
        print(f"  [OK] Proveedor identificado por keyword mas larga '{matched_keyword}' (largo={longest_keyword_len}): {best_supplier}", flush=True)
        return best_supplier, "keyword", None

    return None, None, None

def parse_valid_date(day_str, month_str, year_str):
    try:
        day = int(day_str)
        month = int(month_str)
        year = int(year_str)
        
        if year < 100:
            # Asumir siglo 21 (20XX) para años de 2 dígitos
            year += 2000
            
        if 2000 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
            return datetime.date(year, month, day)
    except Exception:
        pass
    return None

def extract_date_from_text(text):
    """
    Intenta extraer la fecha de emisión del comprobante a partir del texto.
    Busca patrones de fechas y prioriza aquellas asociadas a palabras clave de fecha de emisión.
    Si no encuentra ninguna con palabras clave, devuelve la primera fecha válida del texto.
    """
    text_lower = text.lower()
    
    # 1. Buscar fechas explícitas asociadas a "fecha de emisión", "fecha", "emision", etc.
    keywords_patterns = [
        r'(?:fecha\s+de\s+emisión|fecha\s+de\s+emision|fecha\s+emisión|fecha\s+emision|f\.\s*emisión|f\.\s*emision|fecha\s+de\s+vto|fecha\s+vto|f\.\s*vto|f\.vto|vencimiento|vto\.|vto|fecha|fech|feha|feca|fea|fecna)\b.*?(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})',
        r'\b(?:emisión|emision)\b.*?(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})'
    ]
    
    for pattern in keywords_patterns:
        matches = re.finditer(pattern, text_lower, re.DOTALL)
        for m in matches:
            d, month, y = m.group(1), m.group(2), m.group(3)
            parsed_date = parse_valid_date(d, month, y)
            if parsed_date:
                return parsed_date

    # 2. Buscar cualquier fecha en formato DD/MM/AAAA o DD/MM/AA o YYYY-MM-DD
    general_patterns = [
        r'\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})\b',
        r'\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2})\b',
        r'\b(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})\b'
    ]
    
    for pattern in general_patterns:
        matches = re.finditer(pattern, text_lower)
        for m in matches:
            if pattern == r'\b(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})\b':
                y, month, d = m.group(1), m.group(2), m.group(3)
            else:
                d, month, y = m.group(1), m.group(2), m.group(3)
            parsed_date = parse_valid_date(d, month, y)
            if parsed_date:
                return parsed_date
                
    return None

def wait_for_file_ready(file_path, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not os.path.exists(file_path):
            return False
        try:
            # Intentar renombrar el archivo a sí mismo para verificar si está bloqueado
            os.rename(file_path, file_path)
            return True
        except OSError:
            time.sleep(0.5)
    return False

def process_invoice(file_path):
    print(f"\nProcesando: {file_path}", flush=True)

    is_ready = wait_for_file_ready(file_path)
    if not is_ready:
        if not os.path.exists(file_path):
            print(f"El archivo desapareció antes de poder leerlo.", flush=True)
        else:
            print(f"El archivo sigue bloqueado después de 10 segundos. Saltando.", flush=True)
        return

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    text = extract_text(file_path)

    if not text.strip():
        print("No se encontró texto. Intentando rescate con IA (Gemini)...", flush=True)
        ai_data = extract_data_via_ai(file_path)
        if ai_data and ai_data.get('cuit') and ai_data.get('numero_factura'):
            cuit_cleaned = re.sub(r'\D', '', str(ai_data.get('cuit', '')))
            supplier_found = _CUIT_INDEX.get(cuit_cleaned)
            if not supplier_found:
                supplier_found = ai_data.get('nombre_emisor', 'Proveedor Rescatado')
            
            invoice_number = ai_data.get('numero_factura')
            invoice_date = None
            if ai_data.get('fecha_emision'):
                try:
                    invoice_date = datetime.datetime.strptime(ai_data['fecha_emision'], "%Y-%m-%d").date()
                except Exception:
                    pass
                    
            print(f"  [OK] Rescatado por IA: {supplier_found} - {invoice_number}", flush=True)
            invoice_formatted = invoice_number.replace('-', ' - ')
            new_filename = f"{invoice_formatted} (Rescatado IA){ext}"
            move_to_processed(file_path, supplier_found, new_filename, invoice_date)
            return
            
        print("No se encontró texto (ni con OCR ni con IA). Moviendo a no reconocidas.", flush=True)
        log_error_to_file(file_path, "SIN TEXTO", "El archivo no contiene capa de texto ni se pudo extraer texto mediante OCR o IA.")
        move_to_unrecognized(file_path, f"Desconocido-sin-texto{ext}")
        return

    print(f"--- Texto detectado (primeros 200 caracteres) ---\n{text[:200]}...", flush=True)

    supplier_found, match_method, csv_info = find_supplier(text)
    invoice_number = None

    if supplier_found:
        data = SUPPLIERS[supplier_found]
        # Si se identificó por CAE, reconstruimos el número de factura de forma exacta desde ARCA CSV
        if match_method == "CAE" and csv_info:
            try:
                pv_val = int(csv_info['pv'])
                num_val = int(csv_info['num'])
                pv_len = len(csv_info['pv'])
                pv_fmt = f"{pv_val:05d}" if pv_len == 5 else f"{pv_val:04d}"
                invoice_number = f"{pv_fmt}-{num_val:08d}"
            except Exception:
                invoice_number = f"{csv_info['pv']}-{csv_info['num']}"
            print(f"  [OK] Numero de factura obtenido de ARCA CSV: {invoice_number}", flush=True)
        else:
            match = re.search(data["invoice_regex"], text)
            if match:
                invoice_number = match.group(1).replace(" ", "")

    if supplier_found:
        # Extraer la fecha de la factura para determinar el destino
        invoice_date = None
        if match_method == "CAE" and csv_info and csv_info.get("date"):
            try:
                invoice_date = datetime.datetime.strptime(csv_info["date"], "%Y-%m-%d").date()
                print(f"  [OK] Fecha obtenida de ARCA CSV: {invoice_date}", flush=True)
            except Exception:
                pass
        
        if not invoice_date:
            invoice_date = extract_date_from_text(text)
            if invoice_date:
                print(f"  [OK] Fecha extraída del texto: {invoice_date}", flush=True)
            else:
                print(f"  [ADVERTENCIA] No se pudo extraer la fecha. Usando fecha actual.", flush=True)

        if invoice_number:
            invoice_formatted = invoice_number.replace('-', ' - ')
            new_filename = f"{invoice_formatted}{ext}"
            move_to_processed(file_path, supplier_found, new_filename, invoice_date)
        else:
            print("  [INFO] Falló extracción de número. Intentando rescate con IA...", flush=True)
            ai_data = extract_data_via_ai(file_path)
            if ai_data and ai_data.get('numero_factura'):
                invoice_number = ai_data['numero_factura']
                print(f"  [OK] Numero rescatado por IA: {invoice_number}", flush=True)
                invoice_formatted = invoice_number.replace('-', ' - ')
                new_filename = f"{invoice_formatted} (Rescatado IA){ext}"
                move_to_processed(file_path, supplier_found, new_filename, invoice_date)
            else:
                new_filename = f"{supplier_found}-sin-numero{ext}"
                regex_used = data.get("invoice_regex", "None")
                diagnosis = diagnose_error(text, file_path, supplier_found, regex_used)
                log_error_to_file(file_path, "SIN NUMERO DE FACTURA", diagnosis)
                move_to_unrecognized(file_path, new_filename)
    else:
        print("  [INFO] Falló identificación de proveedor. Intentando rescate con IA...", flush=True)
        ai_data = extract_data_via_ai(file_path)
        if ai_data and ai_data.get('cuit') and ai_data.get('numero_factura'):
            cuit_cleaned = re.sub(r'\D', '', str(ai_data['cuit']))
            supplier_found = _CUIT_INDEX.get(cuit_cleaned)
            if not supplier_found:
                supplier_found = ai_data.get('nombre_emisor', 'Proveedor Rescatado').replace('/', '-')
                
            invoice_number = ai_data['numero_factura']
            invoice_date = None
            if ai_data.get('fecha_emision'):
                try:
                    invoice_date = datetime.datetime.strptime(ai_data['fecha_emision'], "%Y-%m-%d").date()
                except Exception:
                    pass
            print(f"  [OK] Rescatado por IA: {supplier_found} - {invoice_number}", flush=True)
            invoice_formatted = invoice_number.replace('-', ' - ')
            new_filename = f"{invoice_formatted} (Rescatado IA){ext}"
            move_to_processed(file_path, supplier_found, new_filename, invoice_date)
        else:
            diagnosis = diagnose_error(text, file_path)
            log_error_to_file(file_path, "PROVEEDOR NO RECONOCIDO", diagnosis)
            move_to_unrecognized(file_path, f"Desconocido-sin-reconocer{ext}")

def diagnose_error(text, file_path, supplier_found=None, regex_used=None):
    if not text.strip():
        return "El archivo no contiene capa de texto legible ni fue posible extraer caracteres mediante OCR. Verifique si el archivo está dañado, si es una imagen totalmente en blanco o si Tesseract OCR está correctamente configurado."
        
    if not supplier_found:
        detected_cuits = extract_cuits_from_text(text)
        if not detected_cuits:
            return (
                "No se detectó ningún CUIT de 11 dígitos ni palabras clave de proveedores conocidos en el texto.\n"
                "Esto sugiere que:\n"
                "  1. El proveedor es totalmente nuevo (no está en config.py ni en los CSV de ARCA).\n"
                "  2. El OCR tuvo dificultades de lectura debido a tipografías complejas o baja calidad de imagen.\n"
                "Acción recomendada: Verifique si el nombre comercial o CUIT son legibles en la imagen, agregue manualmente el proveedor en config.py o coloque la consulta de ARCA en 'CSV ARCA' y ejecute 'python update_suppliers.py'."
            )
            
        cuit_details = []
        for cuit in detected_cuits:
            csv_company_name = None
            base_dir = os.path.dirname(os.path.abspath(__file__))
            csv_folder = os.path.join(base_dir, "CSV ARCA")
            if os.path.exists(csv_folder):
                import csv
                import io
                csv_files = [os.path.join(csv_folder, f) for f in os.listdir(csv_folder) if f.lower().endswith('.csv')]
                for file_path_csv in csv_files:
                    try:
                        content = None
                        encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-8-sig']
                        for encoding in encodings:
                            try:
                                with open(file_path_csv, mode='r', encoding=encoding) as f:
                                    content = f.read()
                                break
                            except UnicodeDecodeError:
                                continue
                        if content is None:
                            continue
                        reader = csv.reader(io.StringIO(content), delimiter=';')
                        rows = list(reader)
                        if len(rows) < 2:
                            continue
                        header = [col.strip().replace('"', '') for col in rows[0]]
                        try:
                            cuit_idx = header.index("Nro. Doc. Emisor")
                            name_idx = header.index("Denominación Emisor")
                        except ValueError:
                            cuit_idx = 7
                            name_idx = 8
                        for row in rows[1:]:
                            if len(row) <= max(cuit_idx, name_idx):
                                continue
                            row_cuit = re.sub(r'\D', '', row[cuit_idx].strip().replace('"', ''))
                            if row_cuit == cuit:
                                csv_company_name = row[name_idx].strip().replace('"', '')
                                break
                        if csv_company_name:
                            break
                    except Exception:
                        pass
            
            cuit_fmt = f"{cuit[:2]}-{cuit[2:10]}-{cuit[10]}"
            if csv_company_name:
                cuit_details.append(
                    f"CUIT {cuit_fmt} (Corresponde a '{csv_company_name}' según ARCA CSV).\n"
                    f"     Diagnóstico: El proveedor existe en los registros de ARCA pero no está dado de alta en config.py.\n"
                    f"     Acción recomendada: Ejecute 'python update_suppliers.py' para registrarlo automáticamente en config.py, o agréguelo de forma manual."
                )
            else:
                cuit_details.append(
                    f"CUIT {cuit_fmt} (No se encontró en los CSV de ARCA).\n"
                    f"     Diagnóstico: El CUIT no se encuentra en las bases de comprobantes de ARCA cargadas ni en config.py.\n"
                    f"     Acción recomendada: Verifique si el OCR leyó con errores los números del CUIT o agregue manualmente el emisor en config.py."
                )
                
        return (
            "Se detectaron CUITs en la factura pero no coinciden con ningún proveedor activo de config.py:\n  - " 
            + "\n  - ".join(cuit_details)
        )
        
    return (
        f"Se identificó al proveedor como '{supplier_found}', pero falló la extracción del número de factura.\n"
        f"Diagnóstico: La expresión regular configurada para este proveedor ('{regex_used}') no encontró coincidencias.\n"
        f"Acción recomendada:\n"
        f"  1. Verifique si el número de la factura es legible e impreso de manera estándar (ej: 0001-00012345).\n"
        f"  2. Si el formato es diferente, actualice la regla 'invoice_regex' de este proveedor en config.py.\n"
        f"  3. Revise si el OCR distorsionó el número de comprobante."
    )

def log_error_to_file(file_path, error_type, details=None):
    ensure_dir(UNRECOGNIZED_FOLDER)
    log_path = os.path.join(UNRECOGNIZED_FOLDER, "errores_procesamiento.txt")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = os.path.basename(file_path)
    
    log_entry = f"=========================================\n"
    log_entry += f"Fecha/Hora: {timestamp}\n"
    log_entry += f"Archivo: {file_name}\n"
    log_entry += f"Tipo de Error: {error_type}\n"
    if details:
        log_entry += f"Detalles:\n{details}\n"
    log_entry += f"=========================================\n\n"
    
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"  [LOG] Error registrado en: {log_path}", flush=True)
    except Exception as e:
        print(f"Error escribiendo en el log de errores: {e}", flush=True)

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

def move_to_processed(file_path, supplier, new_filename, invoice_date=None):
    if invoice_date is None:
        invoice_date = datetime.date.today()
    year = str(invoice_date.year)
    month_name = MONTHS_ES[invoice_date.month]

    supplier_dir = os.path.join(OUTPUT_FOLDER, year, month_name, supplier)
    ensure_dir(supplier_dir)

    unique_filename = generate_unique_filename(supplier_dir, new_filename)
    dest_path = os.path.join(supplier_dir, unique_filename)

    try:
        shutil.move(file_path, dest_path)
        print(f"¡Éxito! Movido a: {dest_path}", flush=True)
    except Exception as e:
        print(f"Error moviendo archivo: {e}", flush=True)

def move_to_unrecognized(file_path, new_filename):
    ensure_dir(UNRECOGNIZED_FOLDER)
    unique_filename = generate_unique_filename(UNRECOGNIZED_FOLDER, new_filename)
    dest_path = os.path.join(UNRECOGNIZED_FOLDER, unique_filename)

    try:
        shutil.move(file_path, dest_path)
        print(f"No reconocido. Movido a: {dest_path}", flush=True)
    except Exception as e:
        print(f"Error moviendo archivo: {e}", flush=True)

def extract_data_via_ai(file_path):
    from config import AI_API_KEY
    import json
    
    watcher_manager = None
    try:
        from watcher import watcher_manager
    except Exception:
        pass

    if not AI_API_KEY or AI_API_KEY == "TU_API_KEY_AQUI":
        print("  [INFO] Clave de API de IA no configurada. Saltando fallback.", flush=True)
        return None
        
    try:
        if watcher_manager:
            watcher_manager.is_ai_processing = True
            
        import google.generativeai as genai
        import pypdfium2 as pdfium
        import PIL.Image
        
        genai.configure(api_key=AI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Leemos el archivo en memoria para no bloquearlo en Windows
        with open(file_path, 'rb') as f:
            file_data = f.read()
            
        import io
        if ext in ['.png', '.jpg', '.jpeg']:
            img = PIL.Image.open(io.BytesIO(file_data))
            contents = [img]
        elif ext == '.pdf':
            doc = pdfium.PdfDocument(file_data)
            bitmap = doc[0].render(scale=200/72)
            img = bitmap.to_pil()
            contents = [img]
        else:
            return None
            
        prompt = """
        Eres un asistente experto en analizar facturas de Argentina.
        Extrae la siguiente información de la imagen y devuelve ÚNICAMENTE un objeto JSON válido con este formato exacto:
        {
            "cuit": "el CUIT del emisor (11 digitos sin guiones)",
            "nombre_emisor": "el nombre o razón social del emisor",
            "numero_factura": "el número completo de la factura con formato XXXX-XXXXXXXX",
            "fecha_emision": "la fecha de emisión en formato YYYY-MM-DD",
            "keywords_optimizadas": ["palabra1", "palabra2"]
        }
        Si no encuentras alguno de los datos, coloca null en su valor sin comillas.
        Para keywords_optimizadas, extrae 1 o 2 palabras clave únicas y características del emisor (ej. nombre comercial corto) que sirvan para identificar a este proveedor en el futuro. Evita palabras genéricas como "factura" o "SA".
        NO devuelvas explicaciones, marcadores markdown (```json) ni texto adicional, SOLAMENTE el diccionario JSON en texto plano.
        """
        contents.append(prompt)
        
        response = model.generate_content(contents)
        text = response.text
        
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        
        if data and data.get('nombre_emisor') and data.get('keywords_optimizadas'):
            save_ai_supplier(data['nombre_emisor'], data.get('cuit'), data['keywords_optimizadas'])
            
        return data
            
    except Exception as e:
        print(f"Error usando IA de Gemini: {e}", flush=True)
    finally:
        if watcher_manager:
            watcher_manager.is_ai_processing = False
        
    return None

def save_ai_supplier(nombre, cuit, keywords):
    import os
    import json
    import re
    from update_suppliers import format_cuit
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    suppliers_file = os.path.join(base_dir, "suppliers.json")
    
    try:
        suppliers = {}
        if os.path.exists(suppliers_file):
            with open(suppliers_file, 'r', encoding='utf-8') as f:
                suppliers = json.load(f)
                
        final_keywords = []
        if isinstance(keywords, list):
            final_keywords.extend([str(k).lower() for k in keywords])
            
        if cuit:
            cuit_digits = re.sub(r'\D', '', str(cuit))
            if len(cuit_digits) == 11:
                cuit_fmt = format_cuit(cuit_digits)
                final_keywords.extend([cuit_digits, cuit_fmt])
                
        final_keywords.append(nombre.lower())
        final_keywords = list(dict.fromkeys(final_keywords))
        
        if nombre not in suppliers:
            suppliers[nombre] = {
                "keywords": final_keywords,
                "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
            }
            with open(suppliers_file, 'w', encoding='utf-8') as f:
                json.dump(suppliers, f, indent=4, ensure_ascii=False)
            print(f"  [IA] Proveedor '{nombre}' guardado en suppliers.json con keywords optimizadas para futuros escaneos.", flush=True)
            
            from config import SUPPLIERS
            SUPPLIERS[nombre] = suppliers[nombre]
            
            global _CUIT_INDEX
            _CUIT_INDEX = build_cuit_to_supplier_map()
    except Exception as e:
        print(f"Error guardando proveedor de IA: {e}", flush=True)
