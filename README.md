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

---

## 📋 Requisitos del Sistema y Dependencias

### 1. Motor de OCR: Tesseract (Requerido para imágenes/PDFs escaneados)
Este proyecto requiere instalar el software Tesseract en Windows:
* Descargue el instalador desde [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki).
* Se espera la instalación por defecto en:
  `C:\Program Files\Tesseract-OCR\tesseract.exe`
  *(De instalarlo en otra ruta, modifique la variable `TESSERACT_PATH` al inicio de `processor.py`)*.

### 2. Dependencias de Python (`requirements.txt`)
Las librerías requeridas por el proyecto son:
* `watchdog==4.0.1` - Monitoreo del sistema de archivos.
* `pdfplumber==0.11.1` - Extracción directa de texto de PDFs.
* `pypdfium2==4.30.0` - Renderizado de páginas PDF a imagen para OCR.
* `Pillow==10.3.0` - Procesamiento y manipulación de imágenes.
* `pytesseract==0.3.10` - Interfaz de Python para Tesseract OCR.
* `reportlab==4.2.0` - Generación de PDFs para scripts de prueba.

---

## 🛠️ Instalación y Configuración

1. **Clonar o descargar el repositorio** en su máquina local.
2. Instalar **Tesseract OCR** (ver sección de requisitos).
3. **Instalar dependencias de Python:**
   En Windows, simplemente haga doble clic en el archivo ejecutable **`setup.bat`**, o ejecútelo desde la consola:
   ```cmd
   setup.bat
   ```
   Este archivo actualizará `pip` e instalará de forma automática todas las dependencias listadas en `requirements.txt`.

---

## 💻 Instrucciones de Uso

### 1. Actualizar e importar Proveedores desde ARCA (Opcional)
Si ha descargado sus listados de comprobantes de ARCA (Mis Comprobantes Recibidos/Emitidos) en formato CSV:
1. Coloque los archivos `.csv` en la carpeta `CSV ARCA/`.
2. Ejecute el actualizador para dar de alta nuevos proveedores y enriquecer palabras clave automáticamente:
   ```bash
   python update_suppliers.py
   ```

### 2. Iniciar el Vigía
Para iniciar el servicio de monitoreo en tiempo real, ejecute:
```bash
python main.py
```
* **Comprobantes Reconocidos:** Se renombrarán automáticamente al formato `proveedor-puntoVenta-numeroFactura.pdf` y se moverán a:
  `Facturas_Procesadas/<Año>/<Mes_Emisión>/<Proveedor>/`
* **Comprobantes No Reconocidos:** Se moverán a `Facturas_No_Reconocidas/` y sus causas de fallo se registrarán en `Facturas_No_Reconocidas/errores_procesamiento.txt`.

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
