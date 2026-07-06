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

echo [1/4] Actualizando pip...
python -m pip install --upgrade pip

echo [2/4] Instalando dependencias de Python desde requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Hubo un error al instalar las dependencias de Python.
    pause
    exit /b 1
)

echo.
echo [3/4] Instalando dependencias del sistema (Tesseract OCR y NAPS2)...
echo Comprobando si winget esta disponible...
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Instalando Tesseract OCR...
    winget install --id UB-Mannheim.TesseractOCR -e --accept-package-agreements --accept-source-agreements --silent
    echo Instalando NAPS2...
    winget install --id NAPS2.NAPS2 -e --accept-package-agreements --accept-source-agreements --silent
) else (
    echo [ADVERTENCIA] Winget no esta disponible en este sistema. 
    echo Instale Tesseract OCR y NAPS2 manualmente:
    echo Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
    echo NAPS2: https://www.naps2.com/
)

echo.
echo ===================================================
echo Instalacion completada con exito.
echo Para iniciar el programa ejecute: python app.py
echo ===================================================
pause
