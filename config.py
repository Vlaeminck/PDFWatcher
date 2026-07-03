import os

# Rutas Base (Relativas al proyecto para pruebas, pueden cambiarse a C:\...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "Facturas_A_Procesar")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "Facturas_Procesadas")
UNRECOGNIZED_FOLDER = os.path.join(BASE_DIR, "Facturas_No_Reconocidas")

# Extensiones a monitorear
ALLOWED_EXTENSIONS = [".pdf"]

# Diccionario de Proveedores y Expresiones Regulares
# Cada proveedor tiene una lista de palabras clave para identificarlo en el texto,
# y un patrón Regex para extraer el número de factura.
# El formato de número indicado es: Punto de Venta - Número (ej. 0001-12345678)
SUPPLIERS = {
    "Edenor": {
        "keywords": ["edenor", "empresa distribuidora y comercializadora norte"],
        # Busca un patrón tipo 1234-12345678 o similar (ej. 4 a 5 dígitos, guión, 8 dígitos)
        # Ajustar según la longitud real de los puntos de venta y números de factura.
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})" 
    },
    "Metrogas": {
        "keywords": ["metrogas"],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    "Mozzari": {
        "keywords": ["mozzari", "il sapore italiano", "brie", "30-71637640-7"],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
}
