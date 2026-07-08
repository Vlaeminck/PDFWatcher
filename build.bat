@echo off
setlocal EnableDelayedExpansion
echo ===================================================
echo PDFWatcher - Crear Ejecutable (.exe)
echo ===================================================
echo.

:: Verificar si Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH del sistema.
    echo Por favor, instale Python version 3.8 o superior antes de continuar.
    pause
    exit /b 1
)

echo ===================================================
echo [OPCIONAL] Configuracion de Inteligencia Artificial
echo ===================================================
echo Desea ingresar su API Key de Gemini para que el ejecutable 
echo pueda rescatar facturas con IA? (S/N)
set /p add_api="> "
if /i "!add_api!"=="S" (
    set /p api_key="Ingrese su API Key de Gemini: "
    if not "!api_key!"=="" (
        python -c "import re; f=open('config.py', 'r', encoding='utf-8'); c=f.read(); f.close(); c = re.sub(r'AI_API_KEY\s*=\s*[\"''].*?[\"'']', '', c); c = c.replace('import os', f'import os\n\nAI_API_KEY = \"{!api_key!}\"\n', 1); f=open('config.py', 'w', encoding='utf-8'); f.write(c); f.close()"
        echo [OK] API Key inyectada en config.py.
    )
)
echo.
echo ===================================================
echo [VERIFICACION] CSV ARCA
echo ===================================================
if not exist "CSV ARCA\*.csv" (
    echo [ADVERTENCIA] No se encontro ningun archivo .csv en la carpeta "CSV ARCA".
    echo El ejecutable se compilara, pero no tendra datos pre-cargados de ARCA.
    echo Asegurese de anadirlos en la carpeta "CSV ARCA" final si es necesario.
    pause
) else (
    echo [OK] Archivos CSV encontrados.
)
echo.

echo [1/4] Instalando dependencias necesarias (incluyendo PyInstaller)...
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo [2/4] Generando el archivo ejecutable...
:: Usa --add-data para incluir las carpetas de Flask (templates y static)
python -m PyInstaller --noconfirm --onedir --windowed --name "PDFWatcher" --add-data "templates;templates/" --add-data "static;static/" app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Hubo un error al generar el ejecutable.
    pause
    exit /b 1
)

echo.
echo [3/4] Limpiando archivos temporales de compilacion...
rmdir /s /q build
del /q PDFWatcher.spec

echo.
echo [4/4] Creando carpetas de entorno en dist\PDFWatcher...
mkdir "dist\PDFWatcher\Facturas_A_Procesar" 2>nul
mkdir "dist\PDFWatcher\Facturas_Procesadas" 2>nul
mkdir "dist\PDFWatcher\Facturas_No_Reconocidas" 2>nul
mkdir "dist\PDFWatcher\CSV ARCA" 2>nul

echo.
echo ===================================================
echo ¡Ejecutable generado con exito!
echo.
echo Lo encontrara dentro de la carpeta "dist\PDFWatcher".
echo El archivo para ejecutar la aplicacion se llama "PDFWatcher.exe".
echo.
echo NOTA: Tenga en cuenta que en el nuevo equipo todavia necesita 
echo instalar Tesseract OCR y NAPS2 si los usa para escanear y procesar.
echo ===================================================
pause
