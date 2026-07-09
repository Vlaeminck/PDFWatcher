import os
import shutil
import re

import sys

print("="*65)
print(" ⚠️  ADVERTENCIA DE REINICIO DE FÁBRICA (RESET) ⚠️")
print("="*65)
print("ESTA ACCIÓN ES IRREVERSIBLE E IMPLICA LO SIGUIENTE:")
print("1. Se eliminarán TODAS las facturas procesadas y pendientes.")
print("2. Se borrarán los historiales de facturas no reconocidas.")
print("3. Se vaciará la carpeta de CSV de ARCA.")
print("4. Se eliminarán TODOS los proveedores registrados en config.py.")
print("\nBásicamente, la aplicación volverá a estar completamente en blanco.")
print("="*65)

resp = input("\n¿Estás ABSOLUTAMENTE SEGURO de que deseas continuar? (escribe 'SI' para aceptar): ").strip()
if resp != "SI":
    print("\n[INFO] Operación cancelada de forma segura. No se ha borrado nada.")
    sys.exit(0)

print("\nProcediendo con el borrado...\n")

base_dir = os.path.dirname(os.path.abspath(__file__))

def clean_folder(folder_name):
    folder_path = os.path.join(base_dir, folder_name)
    if os.path.exists(folder_path):
        count = 0
        for filename in os.listdir(folder_path):
            if filename.lower() in ['.gitkeep', '.gitignore', 'desktop.ini']:
                continue
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                count += 1
            except Exception as e:
                print(f"[!] Error eliminando {file_path}: {e}")
        print(f"[OK] {folder_name} limpiada ({count} elementos eliminados).")
    else:
        print(f"[-] {folder_name} no existe.")

# 1. Limpiar Carpetas
print("\nLimpiando carpetas de trabajo...")
clean_folder("Facturas_A_Procesar")
clean_folder("Facturas_Procesadas")
clean_folder("Facturas_No_Reconocidas")
clean_folder("CSV ARCA")
clean_folder("registros")

# 2. Eliminar suppliers.json
print("\nEliminando base de datos de proveedores (suppliers.json)...")
suppliers_path = os.path.join(base_dir, "suppliers.json")
if os.path.exists(suppliers_path):
    try:
        os.remove(suppliers_path)
        print("[OK] suppliers.json eliminado exitosamente.")
    except Exception as e:
        print(f"[!] Error eliminando suppliers.json: {e}")
else:
    print("[-] suppliers.json no existe, no hay nada que borrar.")

# 3. Resetear API Key en config.py
print("\nReseteando API Key en config.py...")
config_path = os.path.join(base_dir, "config.py")
if os.path.exists(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Buscar la linea AI_API_KEY = "..." o '...' y reemplazarla
        new_content = re.sub(r'AI_API_KEY\s*=\s*[\'"].*?[\'"]', 'AI_API_KEY = "TU_API_KEY_AQUI"', content)
        
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("[OK] API Key borrada exitosamente de config.py.")
    except Exception as e:
        print(f"[!] Error reseteando config.py: {e}")

print("\n" + "="*50)
print("  ¡APLICACION COMPLETAMENTE LIMPIA!")
print("  Lista para ser usada desde cero o subida a GitHub.")
print("="*50)
