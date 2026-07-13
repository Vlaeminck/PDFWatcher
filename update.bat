@echo off
chcp 65001 > nul
echo ========================================================
echo Buscando actualizaciones de PDFWatcher en el servidor...
echo ========================================================
echo.

:: Asegurar que el repositorio remoto está configurado
git remote add origin https://github.com/Vlaeminck/PDFWatcher.git 2>nul
git remote set-url origin https://github.com/Vlaeminck/PDFWatcher.git 2>nul

:: Obtener información de los últimos cambios sin aplicarlos
git fetch origin main

:: Mostrar qué archivos han sido modificados
echo Los siguientes archivos han sido modificados o agregados en el repositorio y seran actualizados:
git diff --name-status HEAD origin/main
echo.

echo ========================================================
echo Aplicando actualizaciones...
echo ========================================================
echo.

:: Descargar y aplicar los cambios
git pull origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================================
    echo ERROR: Hubo un problema al actualizar. 
    echo Es posible que tengas cambios locales en archivos de codigo que entran en conflicto.
    echo Tus facturas y registros NO han sido afectados.
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo ¡Actualizacion completada con exito!
    echo.
    echo Tus carpetas de datos (Facturas_A_Procesar, 
    echo Facturas_Procesadas, Facturas_No_Reconocidas, 
    echo registros, y CSV ARCA) NO se han visto afectadas,
    echo tu informacion sigue intacta.
    echo ========================================================
)

echo.
pause
