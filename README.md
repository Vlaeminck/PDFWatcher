# PDFWatcher - Vigía y Organizador Inteligente de Facturas

Este proyecto es una herramienta automatizada para Windows que monitorea de forma continua una carpeta de entrada (`Facturas_A_Procesar`), extrae la información relevante de facturas en formato PDF o imágenes (PNG, JPG, etc.), y las organiza automáticamente en carpetas jerárquicas estructuradas por **Año**, **Mes de emisión** y **Nombre de Proveedor**.

---

## 🚀 Características Principales

* **Monitoreo en Tiempo Real:** Utiliza la librería `watchdog` para vigilar de forma reactiva y en tiempo real cualquier adición o cambio en la carpeta de entrada.
* **Organización por Fecha Real de Factura:** Extrae y utiliza la fecha de emisión contenida en el comprobante (ya sea mediante cruce con ARCA CSV o vía regex del texto) para organizar los archivos en el directorio del mes correcto (ej. `/Facturas_Procesadas/2026/Junio/`), previniendo que facturas de meses previos se guarden en el mes de ejecución actual.
* **Motor de Matching Multitier:**
  1. **Tier 1 (CAE):** Detecta códigos de autorización de 14 dígitos (CAE) y los busca en los CSV oficiales de ARCA (ex-AFIP) para reconstruir con precisión los datos de la factura.
  2. **Tier 2 (CUIT como Alias/ID):** Identifica al emisor de manera inequívoca extrayendo su CUIT de 11 dígitos de la factura y cruzándolo con los registros de ARCA CSV. Esto permite clasificar correctamente al proveedor aunque el OCR no lea su nombre comercial debido a logotipos o fuentes complejas.
  3. **Tier 3 (Keywords Inteligentes):** Busca coincidencias textuales en el documento priorizando la palabra clave más larga registrada.
* **Log de Errores con Diagnóstico Inteligente:** Si un comprobante no puede ser procesado, se mueve a `Facturas_No_Reconocidas` y se registra un análisis detallado en `errores_procesamiento.txt` con la causa exacta (sin texto legible, proveedor no registrado, CUIT ausente en ARCA o falla en la expresión regular del número de factura) y la solución recomendada.
* **Soporte OCR Integrado:** Aplica OCR con **Tesseract** de manera transparente si el archivo es una imagen o un PDF sin capa de texto.
* **Sincronización Automática de Proveedores:** Permite actualizar de forma automática la base de datos de proveedores (`config.py`) a partir de archivos CSV oficiales de ARCA colocados en `CSV ARCA` mediante la ejecución de `update_suppliers.py`.
* **Interfaz Web (Dashboard):** Una interfaz gráfica atractiva y moderna (`app.py`) para gestionar los procesos, iniciar el vigía e inspeccionar proveedores en tiempo real.
* **Rescate Asistido por IA (Gemini):** Cuando las expresiones regulares u OCR tradicional fallan, interviene un agente inteligente con Google Gemini Flash Lite para intentar extraer proveedor, fecha y número de comprobante visualmente.
* **Escaneo Automatizado y Silencioso:** Integración con NAPS2 que permite iniciar escaneos directamente desde la interfaz web. El escaneo ocurre de fondo (headless) sin robar el control del mouse y deposita los PDFs directamente para su procesamiento.

---

## 📋 Requisitos del Sistema y Dependencias

### 1. Motor de OCR: Tesseract (Requerido para imágenes/PDFs escaneados)
Este proyecto requiere instalar el software Tesseract en Windows:
* Descargue el instalador desde [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki).
* Se espera la instalación por defecto en:
  `C:\Program Files\Tesseract-OCR\tesseract.exe`
  *(De instalarlo en otra ruta, modifique la variable `TESSERACT_PATH` al inicio de `processor.py`)*.

### 2. NAPS2 (Requerido para el botón Escáner Automático)
Se utiliza para realizar los escaneos silenciosos desde la aplicación web sin interrumpir tu flujo de trabajo.
* Se espera la instalación por defecto en: `C:\Program Files\NAPS2\NAPS2.Console.exe`
* Puede descargarlo desde: [naps2.com](https://www.naps2.com/).
* **IMPORTANTE:** Una vez instalado, abre NAPS2 manualmente por primera vez y haz clic en **"Perfiles" -> "Nuevo"** para configurar y guardar tu escáner. Sin un perfil creado, el escaneo desde la web fallará.

### 3. Dependencias de Python (`requirements.txt`)
Las librerías requeridas por el proyecto son:
* `watchdog==4.0.1` - Monitoreo del sistema de archivos.
* `pdfplumber==0.11.1` - Extracción directa de texto de PDFs.
* `pypdfium2==4.30.0` - Renderizado de páginas PDF a imagen para OCR.
* `Pillow==10.3.0` - Procesamiento y manipulación de imágenes.
* `pytesseract==0.3.10` - Interfaz de Python para Tesseract OCR.
* `reportlab==4.2.0` - Generación de PDFs para scripts de prueba.

---

## 🛠️ Paso a Paso para Empezar (Muy Importante)

Si es la primera vez que vas a usar el sistema, sigue estos **4 pasos estrictamente en orden**. La aplicación **NO funcionará** si intentas iniciarla sin antes cargar tus proveedores.

### Paso 1: Instalar dependencias iniciales
1. Descarga o clona el repositorio.
2. Haz doble clic en el archivo **`setup.bat`** (o ejecútalo desde tu consola).
Este script instalará las librerías de Python requeridas y, si es posible, instalará Tesseract OCR y NAPS2 (programas base necesarios).
3. **Abre NAPS2** (búscalo en el menú inicio de Windows) y crea un **Perfil** seleccionando tu escáner. Esto es obligatorio para que el escaneo automático funcione.

### Paso 2: Cargar tu CSV de ARCA
Para que el sistema sepa reconocer a qué proveedor pertenece cada factura, debes darle un listado inicial:
1. Descarga tu reporte de *Mis Comprobantes Recibidos* desde ARCA (en formato CSV).
2. Coloca ese archivo `.csv` directamente adentro de la carpeta **`CSV ARCA/`**.

### Paso 3: Sincronizar Proveedores
Una vez que tu CSV esté en la carpeta, debes actualizar la base de datos del sistema. Abre la consola en la carpeta del proyecto y ejecuta:
```bash
python update_suppliers.py
```
*(Sin esto, tu sistema no tendrá registrados proveedores para reconocer las facturas).*

### Paso 4: Iniciar la Aplicación
Con los proveedores ya cargados, ahora sí puedes arrancar el programa:
```bash
python app.py
```
Al ejecutarlo, **se abrirá automáticamente una ventana de tu navegador** con el panel de control (Dashboard). Desde ahí podrás activar el vigía para que empiece a organizar tus PDF, o bien iniciar escaneos manuales.

---

### ⚙️ Configuraciones Opcionales Recomendadas

* **Motor de IA (Gemini):** Para habilitar el rescate de facturas borrosas con inteligencia artificial, edita el archivo `config.py` y asigne su token a `AI_API_KEY = "tu-api-key"`.
* **Ruta de Tesseract/NAPS2:** Si instalaste estos programas en rutas diferentes a las estándar, ajusta las rutas en `processor.py` y en `app.py`.

---

## 📂 Estructura de Archivos del Proyecto

```markdown
├── CSV ARCA/                 # Carpeta para colocar reportes de ARCA (.csv)
├── Facturas_A_Procesar/       # Carpeta de entrada monitoreada en tiempo real
├── Facturas_Procesadas/       # Salida organizada jerárquicamente por fecha y proveedor
├── Facturas_No_Reconocidas/   # Archivos no clasificados y log de errores
│   └── errores_procesamiento.txt  # Historial descriptivo de fallas de clasificación
├── config.py                 # Configuración de carpetas y diccionario de proveedores
├── processor.py              # Lógica de OCR, extracción, matching de CUIT/CAE y ruteo
├── update_suppliers.py       # Utilidad para importar/actualizar proveedores desde ARCA CSV
├── main.py                   # Servicio watchdog iniciador del monitoreo
├── requirements.txt          # Requerimientos de librerías Python
└── setup.bat                 # Instalador automatizado de dependencias para Windows
```
