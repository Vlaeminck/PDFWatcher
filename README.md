# PDFWatcher - Vigía y Organizador Inteligente de Facturas

Este proyecto es una herramienta automatizada para Windows que extrae la información relevante de facturas en formato PDF o imágenes (PNG, JPG, etc.), y las organiza automáticamente en carpetas jerárquicas estructuradas por **Año**, **Mes de emisión** y **Nombre de Proveedor**.

---

## 🚀 Características Principales

* **Interfaz Gráfica Moderna (Dashboard Web):** Una interfaz de usuario atractiva que te permite monitorear estadísticas en tiempo real, visualizar facturas procesadas, y administrar proveedores directamente desde el navegador.
* **Organización Inteligente por Fecha:** Extrae la fecha de emisión contenida en el comprobante (mediante texto, OCR o IA) para organizar los archivos en el directorio del mes correcto (`/Facturas_Procesadas/YYYY/Mes/Proveedor/`).
* **Soporte para CSV y ZIP de ARCA:** Actualiza tu base de datos de proveedores automáticamente subiendo tu reporte de "Mis Comprobantes Recibidos" (en CSV o directamente el ZIP de ARCA) desde la pestaña de carga de la aplicación.
* **Motor de Matching Multinivel:** 
  1. **Tier 1 (CAE):** Cruza el CAE extraído con los datos de ARCA.
  2. **Tier 2 (CUIT):** Identifica al emisor de manera inequívoca usando su CUIT.
  3. **Tier 3 (Keywords):** Busca coincidencias textuales inteligentes de la Razón Social.
* **Rescate Asistido por IA (Gemini Flash Lite):** Cuando el OCR tradicional falla o la factura es muy borrosa, interviene un agente inteligente de Google Gemini para extraer proveedor, fecha y número. Se puede configurar fácilmente desde la pestaña **"Ajustes"** de la app.
* **Carga Rápida Manual:** Arrastra y suelta tus PDF o imágenes directamente en el panel general para procesarlos en el acto.
* **Soporte de Escáner Integrado (NAPS2):** Inicia escaneos silenciosos directamente desde la aplicación web. El documento pasará de papel a tu base de datos en un solo clic.
* **Tutorial Interactivo:** Un asistente paso a paso integrado para guiar a los nuevos usuarios.
* **Versión Ejecutable (.exe):** Incluye un script `build.bat` que empaqueta todo el programa en un solo archivo ejecutable para Windows, sin depender de la consola.

---

## 📋 Requisitos del Sistema (Dependencias Externas)

Aunque compiles el programa como `.exe`, el sistema operativo necesita de estos dos programas externos gratuitos para funcionar al 100%:

### 1. Tesseract OCR (Requerido para imágenes/PDFs escaneados)
* Descargue el instalador desde [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki).
* Se instala por defecto en: `C:\Program Files\Tesseract-OCR\tesseract.exe`

### 2. NAPS2 (Requerido para el botón Escáner Automático)
* Descargue desde [naps2.com](https://www.naps2.com/).
* Se instala por defecto en: `C:\Program Files\NAPS2\NAPS2.Console.exe`
* **IMPORTANTE:** Tras instalarlo, abre NAPS2 y ve a **"Perfiles" -> "Nuevo"** para configurar tu escáner físico. Si no hay perfil, el botón de escaneo en la web fallará.

*(Nota: Si distribuyes el `.exe`, el programa está programado para detectar si faltan estos dos componentes e intentará instalarlos automáticamente mediante `winget` la primera vez que se abra).*

---

## 🛠️ Cómo Iniciar y Usar (Modo Ejecutable)

La forma más cómoda de utilizar PDFWatcher es compilarlo.

### 1. Generar el Ejecutable
Asegúrate de tener Python instalado y haz doble clic en el archivo **`build.bat`**. 
El script instalará las dependencias necesarias de Python y generará una carpeta `dist/PDFWatcher` que contiene el archivo **`PDFWatcher.exe`**. 

### 2. Abrir la Aplicación
Haz doble clic en **`PDFWatcher.exe`**.
Se abrirá automáticamente una pestaña en tu navegador web mostrando la interfaz gráfica de la aplicación. 
*(Nota: Al cerrar la pestaña web, el proceso en segundo plano se apagará automáticamente luego de 15 segundos).*

### 3. Cargar Proveedores (Paso Crucial Inicial)
Si es la primera vez que lo abres:
1. Ve a la pestaña **Cargar CSV de ARCA**.
2. Descarga tu reporte histórico de *Mis Comprobantes Recibidos* desde la web de ARCA (se recomiendan al menos los últimos 6 meses para un buen aprendizaje inicial).
3. Arrastra el archivo **.zip** o **.csv** al recuadro de la aplicación.
4. El programa registrará a todos tus proveedores automáticamente. ¡Luego de esto, el sistema está listo para reconocer facturas!

### 4. Procesar Facturas
- **Vigía en Segundo Plano:** Presiona "Iniciar" en el Panel General y cualquier documento que coloques en la carpeta `Facturas_A_Procesar` será ordenado al instante.
- **Carga Manual:** En el mismo Panel General, puedes simplemente arrastrar un PDF o imagen al recuadro de "Carga Rápida" para procesarlo sin siquiera abrir las carpetas de Windows.

---

## ⚙️ Configuración de Inteligencia Artificial

Para activar la inteligencia artificial de **Gemini** que rescata facturas ilegibles:
1. Ve a [Google AI Studio](https://aistudio.google.com/) y genera una API Key gratuita.
2. Abre la aplicación PDFWatcher y ve a la pestaña **Ajustes**.
3. Pega tu clave y dale a "Guardar". La clave quedará guardada de forma encriptada y segura en tu equipo local (`api_key.txt`).

---

## 📂 Modo Desarrollador (Para modificaciones)
Si deseas trabajar en el código fuente en lugar del `.exe`:
1. Ejecuta `setup.bat` para instalar las librerías (`requirements.txt`).
2. Para iniciar la interfaz, simplemente ejecuta:
   ```bash
   python app.py
   ```
