import os

# Rutas Base (Relativas al proyecto para pruebas, pueden cambiarse a C:\...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "Facturas_A_Procesar")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "Facturas_Procesadas")
UNRECOGNIZED_FOLDER = os.path.join(BASE_DIR, "Facturas_No_Reconocidas")

# Extensiones a monitorear
ALLOWED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"]

# Diccionario de Proveedores y Expresiones Regulares
# Cada proveedor tiene una lista de palabras clave para identificarlo en el texto,
# y un patrón Regex para extraer el número de factura.
# El formato de número indicado es: Punto de Venta - Número (ej. 0001-12345678)
SUPPLIERS = {}
