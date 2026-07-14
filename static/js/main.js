document.addEventListener('DOMContentLoaded', () => {
    // --- Navigation ---
    const navLinks = document.querySelectorAll('.nav-links li');
    const tabPanes = document.querySelectorAll('.tab-pane');

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Remove active from all
            navLinks.forEach(l => l.classList.remove('active'));
            tabPanes.forEach(p => p.style.display = 'none');
            
            // Add active to clicked
            link.classList.add('active');
            const targetTab = document.getElementById(`tab-${link.dataset.tab}`);
            if (targetTab) {
                targetTab.style.display = 'block';
                targetTab.classList.remove('fade-in');
                // trigger reflow to restart animation
                void targetTab.offsetWidth;
                targetTab.classList.add('fade-in');
            }

            // Fetch data if needed based on tab
            if (link.dataset.tab === 'dashboard') {
                fetchStatus();
                fetchProgress();
            }
            if (link.dataset.tab === 'suppliers') fetchSuppliers();
            if (link.dataset.tab === 'processed') fetchProcessedInvoices();
        });
    });

    // --- Toast Notifications ---
    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = 'fa-check-circle';
        if (type === 'error') icon = 'fa-circle-xmark';
        if (type === 'warning') icon = 'fa-triangle-exclamation';
        
        toast.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <div class="toast-content"><p>${message}</p></div>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease forwards';
            setTimeout(() => {
                if(container.contains(toast)) container.removeChild(toast);
            }, 300);
        }, 5000);
    }

    // --- Dashboard & Watcher Controls ---
    const btnStart = document.getElementById('btn-start-watcher');
    const btnStop = document.getElementById('btn-stop-watcher');
    const btnScanner = document.getElementById('btn-open-scanner');

    const statusText = document.getElementById('watcher-status-text');
    const statusBadge = document.getElementById('watcher-status-badge');

    let prevUnrecognizedCount = null;

    async function fetchStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            
            updateWatcherStatusUI(data.watcher_running);
            
            document.getElementById('stat-pending').textContent = data.stats.pending;
            document.getElementById('stat-processed').textContent = data.stats.processed;
            document.getElementById('stat-unrecognized').textContent = data.stats.unrecognized;
            
            if (prevUnrecognizedCount !== null && data.stats.unrecognized > prevUnrecognizedCount) {
                showToast("¡Atención! Una factura no reconocida requiere revisión.", "warning");
            }
            prevUnrecognizedCount = data.stats.unrecognized;
        } catch (error) {
            console.error("Error fetching status:", error);
        }
    }

    const progressContainer = document.getElementById('progress-container');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressText = document.getElementById('progress-text');
    const aiIndicator = document.getElementById('ai-processing-indicator');

    async function fetchProgress() {
        try {
            const res = await fetch('/api/progress');
            const data = await res.json();
            
            if (data.is_processing_batch) {
                progressContainer.style.display = 'block';
                let percent = 0;
                if (data.total > 0) {
                    percent = Math.round((data.processed / data.total) * 100);
                }
                progressBarFill.style.width = `${percent}%`;
                progressText.textContent = `${data.processed} / ${data.total} (${percent}%)`;
            } else {
                progressContainer.style.display = 'none';
            }
            
            if (data.is_ai_processing) {
                aiIndicator.style.display = 'block';
            } else {
                aiIndicator.style.display = 'none';
            }
        } catch (error) {
            console.error("Error fetching progress:", error);
        }
    }

    function updateWatcherStatusUI(isRunning) {
        if (isRunning) {
            statusText.textContent = 'ACTIVO (Escuchando...)';
            statusBadge.className = 'status-badge status-active';
            btnStart.disabled = true;
            btnStop.disabled = false;
        } else {
            statusText.textContent = 'DETENIDO';
            statusBadge.className = 'status-badge status-inactive';
            btnStart.disabled = false;
            btnStop.disabled = true;
        }
    }

    btnStart.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/watcher/start', { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                showToast(data.message, 'success');
                updateWatcherStatusUI(true);
            } else {
                showToast(data.message, 'error');
            }
        } catch (e) {
            showToast("Error al iniciar el vigía", 'error');
        }
    });

    btnStop.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/watcher/stop', { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                showToast(data.message, 'success');
                updateWatcherStatusUI(false);
            } else {
                showToast(data.message, 'error');
            }
        } catch (e) {
            showToast("Error al detener el vigía", 'error');
        }
    });

    if (btnScanner) {
        btnScanner.addEventListener('click', async () => {
            // Animación temporal en el botón
            const originalHTML = btnScanner.innerHTML;
            btnScanner.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Escaneando...';
            btnScanner.disabled = true;

            try {
                const res = await fetch('/api/open_scanner', { method: 'POST' });
                const data = await res.json();
                if (data.success) {
                    showToast(data.message, 'success');
                } else {
                    showToast("Error al abrir escáner automático", 'error');
                }
            } catch (e) {
                showToast("Error de conexión con el escáner", 'error');
            }
            
            // Habilitar botón de nuevo después de 5s para que no se quede pegado 
            // (el script de pywinauto funciona de fondo)
            setTimeout(() => {
                btnScanner.innerHTML = originalHTML;
                btnScanner.disabled = false;
            }, 5000);
        });
    }



    // --- Suppliers Tab ---
    const suppliersTableBody = document.getElementById('suppliers-table-body');
    const searchInput = document.getElementById('search-suppliers');
    const btnRefreshSuppliers = document.getElementById('btn-refresh-suppliers');
    const noResultsMsg = document.getElementById('no-results-msg');
    const supplierCount = document.getElementById('supplier-count');
    
    let allSuppliers = [];

    async function fetchSuppliers() {
        try {
            const res = await fetch('/api/suppliers');
            allSuppliers = await res.json();
            renderSuppliers(allSuppliers);
        } catch (error) {
            console.error("Error fetching suppliers:", error);
            showToast("Error al cargar proveedores", "error");
        }
    }

    function renderSuppliers(suppliersList) {
        suppliersTableBody.innerHTML = '';
        
        supplierCount.textContent = `${suppliersList.length} proveedores`;
        
        if (suppliersList.length === 0) {
            noResultsMsg.style.display = 'flex';
            document.querySelector('.table-container').style.display = 'none';
            return;
        }
        
        noResultsMsg.style.display = 'none';
        document.querySelector('.table-container').style.display = 'block';
        
        suppliersList.forEach(sup => {
            const tr = document.createElement('tr');
            
            // Name
            const tdName = document.createElement('td');
            tdName.innerHTML = `<strong>${sup.name}</strong>`;
            
            // Keywords
            const tdKw = document.createElement('td');
            let kwHtml = '';
            sup.keywords.forEach(kw => {
                kwHtml += `<span class="kw-tag">${kw}</span>`;
            });
            tdKw.innerHTML = kwHtml;
            
            // Regex
            const tdRegex = document.createElement('td');
            tdRegex.innerHTML = `<span class="code-snippet">${sup.regex}</span>`;
            
            tr.appendChild(tdName);
            tr.appendChild(tdKw);
            tr.appendChild(tdRegex);
            suppliersTableBody.appendChild(tr);
        });
    }

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = allSuppliers.filter(sup => {
            return sup.name.toLowerCase().includes(query) || 
                   sup.keywords.some(k => k.toLowerCase().includes(query));
        });
        renderSuppliers(filtered);
    });

    btnRefreshSuppliers.addEventListener('click', () => {
        searchInput.value = '';
        fetchSuppliers();
        showToast("Lista actualizada");
    });

    // --- Processed Invoices Tab ---
    const processedTreeContainer = document.getElementById('processed-tree-container');
    const searchProcessedInput = document.getElementById('search-processed');
    const btnRefreshProcessed = document.getElementById('btn-refresh-processed');
    const noProcessedMsg = document.getElementById('no-processed-msg');
    const processedCount = document.getElementById('processed-count');
    
    let allProcessedInvoices = [];

    async function fetchProcessedInvoices() {
        try {
            const res = await fetch('/api/processed_invoices');
            allProcessedInvoices = await res.json();
            renderProcessedTree(allProcessedInvoices);
        } catch (error) {
            console.error("Error fetching processed invoices:", error);
            showToast("Error al cargar facturas procesadas", "error");
        }
    }

    function renderProcessedTree(invoicesList) {
        processedTreeContainer.innerHTML = '';
        processedCount.textContent = `${invoicesList.length} facturas`;
        
        if (invoicesList.length === 0) {
            noProcessedMsg.style.display = 'flex';
            document.querySelector('#tab-processed .table-container').style.display = 'none';
            return;
        }
        
        noProcessedMsg.style.display = 'none';
        document.querySelector('#tab-processed .table-container').style.display = 'block';

        // Group by Year -> Month -> Supplier
        const tree = {};
        invoicesList.forEach(inv => {
            const parts = inv.date.split(' ');
            const month = parts[0] || 'N/A';
            const year = parts[1] || 'N/A';
            const s = inv.supplier || 'N/A';
            
            if (!tree[year]) tree[year] = {};
            if (!tree[year][month]) tree[year][month] = {};
            if (!tree[year][month][s]) tree[year][month][s] = [];
            
            tree[year][month][s].push(inv);
        });

        function buildFolder(name, contentHtml, isOpen = false) {
            const folderDiv = document.createElement('div');
            folderDiv.className = `tree-folder ${isOpen ? 'open' : ''}`;
            
            const folderNameDiv = document.createElement('div');
            folderNameDiv.className = 'tree-folder-name';
            folderNameDiv.innerHTML = `<i class="fa-solid fa-folder${isOpen ? '-open' : ''}"></i> <strong>${name}</strong>`;
            
            const folderContentDiv = document.createElement('div');
            folderContentDiv.className = 'tree-folder-content';
            folderContentDiv.appendChild(contentHtml);

            folderNameDiv.addEventListener('click', () => {
                const isOpenNow = folderDiv.classList.toggle('open');
                folderNameDiv.querySelector('i').className = `fa-solid fa-folder${isOpenNow ? '-open' : ''}`;
            });

            folderDiv.appendChild(folderNameDiv);
            folderDiv.appendChild(folderContentDiv);
            return folderDiv;
        }

        const rootDiv = document.createElement('div');
        const hasSearch = searchProcessedInput.value.trim().length > 0;

        Object.keys(tree).sort().reverse().forEach(year => {
            const yearContent = document.createElement('div');
            Object.keys(tree[year]).sort().forEach(month => {
                const monthContent = document.createElement('div');
                Object.keys(tree[year][month]).sort().forEach(supplier => {
                    const supplierContent = document.createElement('div');
                    tree[year][month][supplier].forEach(inv => {
                        const fileDiv = document.createElement('div');
                        fileDiv.className = 'tree-file';
                        fileDiv.innerHTML = `<i class="fa-solid fa-file-pdf"></i> <span>${inv.filename}</span>`;
                        fileDiv.addEventListener('click', () => openModal(inv));
                        supplierContent.appendChild(fileDiv);
                    });
                    monthContent.appendChild(buildFolder(supplier, supplierContent, true));
                });
                yearContent.appendChild(buildFolder(month, monthContent, true));
            });
            rootDiv.appendChild(buildFolder(year, yearContent, true));
        });

        processedTreeContainer.appendChild(rootDiv);
    }

    searchProcessedInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = allProcessedInvoices.filter(inv => {
            return inv.filename.toLowerCase().includes(query) || 
                   inv.supplier.toLowerCase().includes(query) ||
                   inv.date.toLowerCase().includes(query);
        });
        renderProcessedTree(filtered);
    });

    btnRefreshProcessed.addEventListener('click', () => {
        searchProcessedInput.value = '';
        fetchProcessedInvoices();
        showToast("Historial actualizado");
    });

    // --- Modal Logic ---
    const modal = document.getElementById('file-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalIframe = document.getElementById('modal-iframe');
    const closeModalBtn = document.querySelector('.close-modal');

    function openModal(inv) {
        modalTitle.textContent = `${inv.supplier} - ${inv.filename}`;
        // Enforce proper encoding of the path
        const encodedPath = inv.path.split('/').map(encodeURIComponent).join('/');
        modalIframe.src = `/api/file/${encodedPath}`;
        modal.style.display = 'flex';
        modal.classList.add('fade-in');
    }

    closeModalBtn.addEventListener('click', () => {
        modal.style.display = 'none';
        modalIframe.src = '';
    });

    window.addEventListener('click', (e) => {
        if (e.target == modal) {
            modal.style.display = 'none';
            modalIframe.src = '';
        }
    });

    // --- Upload CSV Tab ---
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-upload');
    const uploadStatus = document.getElementById('upload-status');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        let dt = e.dataTransfer;
        let files = dt.files;
        handleFiles(files);
    });

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length === 0) return;
        const file = files[0];
        if (!file.name.toLowerCase().endsWith('.csv') && !file.name.toLowerCase().endsWith('.zip')) {
            showToast("Solo se admiten archivos .csv o .zip", "error");
            return;
        }
        uploadFile(file);
    }

    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        dropZone.style.display = 'none';
        uploadStatus.style.display = 'block';

        try {
            const response = await fetch('/api/upload_csv', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (data.success) {
                showToast(data.message, 'success');
                // Refresh data if needed
                fetchSuppliers();
            } else {
                showToast(data.message || "Error al procesar el archivo", 'error');
            }
        } catch (error) {
            console.error("Error upload:", error);
            showToast("Error de red al subir el archivo", 'error');
        } finally {
            // Reset UI
            setTimeout(() => {
                uploadStatus.style.display = 'none';
                dropZone.style.display = 'block';
                fileInput.value = ''; // clear input
            }, 3000);
        }
    }

    // --- Settings Tab ---
    const btnSaveApiKey = document.getElementById('btn-save-api-key');
    const inputApiKey = document.getElementById('input-api-key');

    if (btnSaveApiKey && inputApiKey) {
        // Cargar clave actual
        fetch('/api/settings/get_api_key')
            .then(res => res.json())
            .then(data => {
                if (data.api_key) inputApiKey.value = data.api_key;
            }).catch(e => console.error("Error loading API Key", e));

        btnSaveApiKey.addEventListener('click', async () => {
            const apiKey = inputApiKey.value.trim();
            if (!apiKey) {
                showToast("Por favor ingresa una API Key", "warning");
                return;
            }
            // Add loading state
            const originalHTML = btnSaveApiKey.innerHTML;
            btnSaveApiKey.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Guardando...';
            btnSaveApiKey.disabled = true;

            try {
                const res = await fetch('/api/settings/api_key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: apiKey })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(data.message, 'success');
                } else {
                    showToast(data.message, 'error');
                }
            } catch (error) {
                showToast("Error de conexión al guardar", 'error');
            } finally {
                btnSaveApiKey.innerHTML = originalHTML;
                btnSaveApiKey.disabled = false;
            }
        });
    }

    // --- Driver.js Tutorial ---
    if (window.driver) {
        const driver = window.driver.js.driver;
        
        const driverObj = driver({
            showProgress: true,
            nextBtnText: 'Siguiente',
            prevBtnText: 'Anterior',
            doneBtnText: 'Entendido',
            steps: [
                { element: 'li[data-tab="dashboard"]', popover: { title: 'Panel General', description: 'Aquí podrás ver las estadísticas y controlar el inicio/fin del vigía de facturas.' } },
                { element: 'li[data-tab="processed"]', popover: { title: 'Facturas Procesadas', description: 'Revisa tus facturas organizadas automáticamente por año, mes y proveedor.' } },
                { element: 'li[data-tab="upload"]', popover: { title: 'Cargar CSV o ZIP', description: 'Sube aquí el archivo descargado de ARCA para registrar tus comprobantes.' } },
                { element: 'li[data-tab="settings"]', popover: { title: 'Ajustes de IA', description: 'Configura tu API Key de Gemini para que la IA lea automáticamente facturas difíciles o borrosas.' } }
            ]
        });

        const btnHelp = document.getElementById('btn-help');
        if (btnHelp) {
            btnHelp.addEventListener('click', () => {
                driverObj.drive();
            });
        }

        // Auto-start si es la primera vez
        if (!localStorage.getItem('pdfwatcher_tutorial_seen')) {
            setTimeout(() => {
                driverObj.drive();
                localStorage.setItem('pdfwatcher_tutorial_seen', 'true');
            }, 1000);
        }
    }

    // --- Heartbeat Ping ---
    // Enviar ping cada 3 segundos para mantener el proceso vivo.
    // Si cerramos la pestaña, el backend no recibe pings y se auto-apagará en 15s.
    setInterval(() => {
        fetch('/api/ping', { method: 'POST' }).catch(() => {});
    }, 3000);

    // Init polling for status every 2 seconds if dashboard is active
    fetchStatus();
    setInterval(() => {
        const activeTab = document.querySelector('.nav-links li.active');
        if (activeTab && activeTab.dataset.tab === 'dashboard') {
            fetchStatus();
            fetchProgress();
        }
    }, 2000);

    // --- Doctor Tab Logic ---
    const btnDoctorScan = document.getElementById('btn-doctor-scan');
    const btnDoctorFix = document.getElementById('btn-doctor-fix');
    const doctorResultsContainer = document.getElementById('doctor-results-container');
    const doctorResultsList = document.getElementById('doctor-results-list');
    const doctorCount = document.getElementById('doctor-count');
    
    let currentAnomalies = [];

    if (btnDoctorScan) {
        btnDoctorScan.addEventListener('click', async () => {
            const originalHTML = btnDoctorScan.innerHTML;
            btnDoctorScan.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Escaneando...';
            btnDoctorScan.disabled = true;
            btnDoctorFix.disabled = true;
            
            try {
                const res = await fetch('/api/doctor/scan');
                const data = await res.json();
                
                if (data.success) {
                    currentAnomalies = data.anomalies;
                    renderDoctorResults(currentAnomalies);
                } else {
                    showToast("Error al escanear: " + data.message, "error");
                }
            } catch (error) {
                showToast("Error de conexión con el Doctor", "error");
            } finally {
                btnDoctorScan.innerHTML = originalHTML;
                btnDoctorScan.disabled = false;
            }
        });
    }

    if (btnDoctorFix) {
        btnDoctorFix.addEventListener('click', async () => {
            if (currentAnomalies.length === 0) return;
            
            const originalHTML = btnDoctorFix.innerHTML;
            btnDoctorFix.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Curando...';
            btnDoctorFix.disabled = true;
            btnDoctorScan.disabled = true;
            
            try {
                const res = await fetch('/api/doctor/fix', { method: 'POST' });
                const data = await res.json();
                
                if (data.success) {
                    showToast(`Se aplicaron ${data.fixes} curas automáticas.`, "success");
                    if (data.errors.length > 0) {
                        showToast(`Hubo ${data.errors.length} errores al curar. Revisa la consola.`, "warning");
                        console.error("Errores del doctor:", data.errors);
                    }
                    // Rescan
                    btnDoctorScan.click();
                } else {
                    showToast("Error al aplicar curas: " + data.message, "error");
                }
            } catch (error) {
                showToast("Error de red al aplicar curas", "error");
            } finally {
                btnDoctorFix.innerHTML = originalHTML;
                btnDoctorScan.disabled = false;
            }
        });
    }

    function renderDoctorResults(anomalies) {
        doctorResultsContainer.style.display = 'block';
        doctorResultsList.innerHTML = '';
        doctorCount.textContent = `${anomalies.length} anomalías`;
        
        if (anomalies.length === 0) {
            doctorCount.className = "badge status-active";
            doctorResultsList.innerHTML = '<div style="padding: 1rem; text-align: center; color: var(--success);"><i class="fa-solid fa-check-circle" style="font-size: 2rem; margin-bottom: 0.5rem;"></i><br>¡Todo está perfecto! No se encontraron anomalías.</div>';
            btnDoctorFix.disabled = true;
            return;
        }
        
        doctorCount.className = "badge status-inactive";
        btnDoctorFix.disabled = false;
        
        anomalies.forEach(anom => {
            const div = document.createElement('div');
            
            let color = "var(--text)";
            let icon = "fa-triangle-exclamation";
            
            if (anom.severity === 'high') { color = "var(--danger)"; icon = "fa-circle-xmark"; }
            else if (anom.severity === 'medium') { color = "var(--warning)"; }
            else if (anom.severity === 'low') { color = "var(--text-secondary)"; icon = "fa-info-circle"; }
            
            div.style.padding = "1rem";
            div.style.border = "1px solid rgba(255,255,255,0.1)";
            div.style.borderRadius = "0.5rem";
            div.style.background = "rgba(0,0,0,0.2)";
            
            div.innerHTML = `
                <div style="display: flex; align-items: flex-start; gap: 1rem;">
                    <i class="fa-solid ${icon}" style="color: ${color}; margin-top: 0.2rem;"></i>
                    <div>
                        <strong style="color: ${color}; text-transform: uppercase; font-size: 0.8rem;">${anom.type.replace(/_/g, ' ')}</strong>
                        <p style="margin: 0.2rem 0; font-size: 0.95rem;">${anom.message}</p>
                        <small style="color: var(--text-secondary); word-break: break-all;"><code>${anom.path}</code></small>
                    </div>
                </div>
            `;
            doctorResultsList.appendChild(div);
        });
    }
});
