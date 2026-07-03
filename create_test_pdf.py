from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
from config import INPUT_FOLDER

def create_pdf(filename, text_lines):
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
    
    path = os.path.join(INPUT_FOLDER, filename)
    c = canvas.Canvas(path, pagesize=letter)
    
    y = 700
    for line in text_lines:
        c.drawString(100, y, line)
        y -= 20
        
    c.save()
    print(f"Created {path}")

if __name__ == '__main__':
    # Test 1: Todo correcto (Edenor)
    create_pdf("escaneo_001.pdf", [
        "Factura de servicio",
        "Empresa Distribuidora y Comercializadora Norte",
        "Total a pagar: $1500",
        "Factura Nro: 0001-12345678"
    ])
    
    # Test 2: Proveedor reconocido pero sin numero valido
    create_pdf("escaneo_002.pdf", [
        "Factura de Edenor",
        "Total a pagar: $2000",
        "El numero esta ilegible o ausente"
    ])
    
    # Test 3: Desconocido total
    create_pdf("escaneo_003.pdf", [
        "Factura de servicios generales",
        "Libreria y fotocopias",
        "Total: $500",
        "0002-98765432"
    ])
