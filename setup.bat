@echo off
echo ===================================================
echo PDFWatcher - Instalar Dependencias
echo ===================================================
echo.

:: Verificar si Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH del sistema.
    echo Por favor, instale Python (version 3.8 o superior) antes de continuar.
    pause
    exit /b 1
)

echo [1/3] Actualizando pip...
python -m pip install --upgrade pip

echo [2/3] Instalando dependencias de Python desde requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Hubo un error al instalar las dependencias de Python.
    pause
    exit /b 1
)

echo.
echo [3/3] IMPORTANTE: Tesseract OCR
echo Este proyecto utiliza Tesseract OCR para extraer texto de imagenes y PDFs escaneados.
echo Debe instalar Tesseract OCR para Windows y asegurarse de que este en la siguiente ruta:
echo C:\Program Files\Tesseract-OCR\tesseract.exe
echo.
echo Puede descargarlo desde: https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo ===================================================
echo Instalacion completada con exito.
echo Para iniciar el programa ejecute: python main.py
echo ===================================================
pause
