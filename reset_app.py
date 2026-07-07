import os
import shutil
import re

print("="*50)
print("  PREPARANDO APP PARA INICIO LIMPIO (RESET)")
print("="*50)

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

# 2. Resetear config.py
print("\nReseteando diccionario de proveedores en config.py...")
config_path = os.path.join(base_dir, "config.py")
try:
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar dónde empieza SUPPLIERS
    match = re.search(r'^SUPPLIERS\s*=\s*\{', content, re.MULTILINE)
    if match:
        top_part = content[:match.start()]
        new_content = top_part + "SUPPLIERS = {}\n"
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("[OK] config.py reseteado correctamente (SUPPLIERS = {}).")
    else:
        print("[!] No se encontro la declaracion 'SUPPLIERS =' en config.py")
except Exception as e:
    print(f"[!] Error reseteando config.py: {e}")

print("\n" + "="*50)
print("  ¡APLICACION COMPLETAMENTE LIMPIA!")
print("  Lista para ser usada desde cero o subida a GitHub.")
print("="*50)
