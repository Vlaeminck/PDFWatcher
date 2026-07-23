document.addEventListener('DOMContentLoaded', () => {
    // --- Navigation ---
    const navLinks = document.querySelectorAll('.nav-links li, li[data-tab="doctor"]');
    const tabPanes = document.querySelectorAll('.tab-pane');

    function switchTab(tabName) {
        navLinks.forEach(l => l.classList.remove('active'));
        tabPanes.forEach(p => p.style.display = 'none');
        
        const activeLink = document.querySelector(`.nav-links li[data-tab="${tabName}"]`);
        if (activeLink) activeLink.classList.add('active');

        const targetTab = document.getElementById(`tab-${tabName}`);
        if (targetTab) {
            targetTab.style.display = 'block';
            targetTab.classList.remove('fade-in');
            void targetTab.offsetWidth;
            targetTab.classList.add('fade-in');
        }

        if (tabName === 'dashboard') {
            fetchStatus();
            fetchProgress();
        }
        if (tabName === 'suppliers') fetchSuppliers();
        if (tabName === 'processed') fetchProcessedInvoices();
        if (tabName === 'remitos') fetchProcessedRemitos();
        if (tabName === 'unrecognized') fetchUnrecognizedInvoices();
    }

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            switchTab(link.dataset.tab);
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

    // --- License Check ---
    const licenseStatusBadge = document.getElementById('license-status-badge');
    const licenseStatusText = document.getElementById('license-status-text');
    const inputHardwareId = document.getElementById('input-hardware-id');
    const btnCopyHwId = document.getElementById('btn-copy-hwid');
    const expBanner = document.getElementById('expiration-banner');
    const expText = document.getElementById('expiration-text');
    const btnSyncLicense = document.getElementById('btn-sync-license');
    let isLicenseValid = true; // Default to true until checked, or default to false and let check enable it

    async function fetchLicenseStatus(force = false) {
        try {
            const url = force ? '/api/license/status?force=true' : '/api/license/status';
            const res = await fetch(url);
            const data = await res.json();
            
            if (inputHardwareId) {
                inputHardwareId.value = data.hw_id || 'ERROR';
            }

            if (data.valid) {
                isLicenseValid = true;
                if (licenseStatusBadge) {
                    licenseStatusBadge.className = 'status-badge status-active';
                    licenseStatusText.textContent = data.message || 'Activa';
                }
                
                if (data.days_left !== undefined && data.days_left !== null && data.days_left <= 15) {
                    if (expBanner && expText) {
                        expBanner.style.display = 'block';
                        expText.textContent = `Atención: Tu licencia expirará en ${data.days_left} día(s).`;
                    }
                } else {
                    if (expBanner) expBanner.style.display = 'none';
                }
            } else {
                isLicenseValid = false;
                if (licenseStatusBadge) {
                    licenseStatusBadge.className = 'status-badge status-inactive';
                    licenseStatusText.textContent = 'Inactiva / No Registrada';
                }
                
                // Deshabilitar botones principales si hay referencias
                const bStart = document.getElementById('btn-start-watcher');
                const bStop = document.getElementById('btn-stop-watcher');
                const bScan = document.getElementById('btn-open-scanner');
                
                if (bStart) bStart.disabled = true;
                if (bStop) bStop.disabled = true;
                if (bScan) bScan.disabled = true;
                
                // Force update UI
                updateWatcherStatusUI(false);
                
                if (expBanner) expBanner.style.display = 'none';
                
                showToast(`Licencia Inválida: ${data.message || 'Contacta al administrador'}`, 'error');
            }
        } catch (error) {
            console.error("Error fetching license status:", error);
            if (licenseStatusBadge) {
                licenseStatusBadge.className = 'status-badge status-inactive';
                licenseStatusText.textContent = 'Error de Conexión';
            }
        }
    }

    if (btnCopyHwId) {
        btnCopyHwId.addEventListener('click', () => {
            if (inputHardwareId && inputHardwareId.value) {
                navigator.clipboard.writeText(inputHardwareId.value)
                    .then(() => showToast('Hardware ID copiado al portapapeles', 'success'))
                    .catch(err => showToast('Error al copiar ID', 'error'));
            }
        });
    }

    if (btnSyncLicense) {
        btnSyncLicense.addEventListener('click', async () => {
            const icon = btnSyncLicense.querySelector('i');
            icon.classList.add('fa-spin');
            await fetchLicenseStatus(true);
            icon.classList.remove('fa-spin');
            showToast('Licencia sincronizada con Firebase', 'success');
        });
    }

    // --- Dashboard & Watcher Controls ---
    const btnStart = document.getElementById('btn-start-watcher');
    const btnStop = document.getElementById('btn-stop-watcher');
    const btnScanner = document.getElementById('btn-open-scanner');

    const statusText = document.getElementById('watcher-status-text');
    const statusBadge = document.getElementById('watcher-status-badge');

    let prevUnrecognizedCount = null;

    const cardProcessed = document.getElementById('card-processed');
    const cardRemitos = document.getElementById('card-remitos');
    const cardUnrecognized = document.getElementById('card-unrecognized');

    if (cardProcessed) {
        cardProcessed.addEventListener('click', () => switchTab('processed'));
    }
    if (cardRemitos) {
        cardRemitos.addEventListener('click', () => switchTab('remitos'));
    }
    if (cardUnrecognized) {
        cardUnrecognized.addEventListener('click', () => switchTab('unrecognized'));
    }

    async function fetchStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            
            updateWatcherStatusUI(data.watcher_running);
            
            document.getElementById('stat-pending').textContent = data.stats.pending;
            document.getElementById('stat-processed').textContent = data.stats.processed;
            document.getElementById('stat-unrecognized').textContent = data.stats.unrecognized;
            if (document.getElementById('stat-remitos')) {
                document.getElementById('stat-remitos').textContent = data.stats.remitos || 0;
            }
            
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
        if (!isLicenseValid) {
            statusText.textContent = 'BLOQUEADO (Sin Licencia)';
            statusBadge.className = 'status-badge status-inactive';
            if (btnStart) btnStart.disabled = true;
            if (btnStop) btnStop.disabled = true;
            return;
        }
        
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

    // --- Remitos y Documentos No Fiscales ---
    const remitosTreeContainer = document.getElementById('remitos-tree-container');
    const remitosCount = document.getElementById('remitos-count');
    const noRemitosMsg = document.getElementById('no-remitos-msg');
    const searchRemitosInput = document.getElementById('search-remitos');
    const btnRefreshRemitos = document.getElementById('btn-refresh-remitos');
    let rawRemitosList = [];

    async function fetchProcessedRemitos() {
        try {
            const res = await fetch('/api/processed_remitos');
            rawRemitosList = await res.json();
            renderRemitosTree(rawRemitosList);
        } catch (e) {
            console.error("Error fetching processed remitos:", e);
            showToast("Error al cargar remitos", "error");
        }
    }

    function renderRemitosTree(list) {
        if (!remitosTreeContainer) return;
        remitosTreeContainer.innerHTML = '';
        remitosCount.textContent = `${list.length} remitos`;

        if (list.length === 0) {
            noRemitosMsg.style.display = 'flex';
            if (document.querySelector('#tab-remitos .table-container')) {
                document.querySelector('#tab-remitos .table-container').style.display = 'none';
            }
            return;
        }

        noRemitosMsg.style.display = 'none';
        if (document.querySelector('#tab-remitos .table-container')) {
            document.querySelector('#tab-remitos .table-container').style.display = 'block';
        }

        const tree = {};
        list.forEach(item => {
            const parts = item.date.split(' ');
            const month = parts[0] || 'N/A';
            const year = parts[1] || 'N/A';

            if (!tree[year]) tree[year] = {};
            if (!tree[year][month]) tree[year][month] = [];
            tree[year][month].push(item);
        });

        function buildFolder(name, contentHtml, isOpen = true) {
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

        Object.keys(tree).sort().reverse().forEach(year => {
            const yearContent = document.createElement('div');
            Object.keys(tree[year]).sort().forEach(month => {
                const monthContent = document.createElement('div');
                tree[year][month].forEach(item => {
                    const fileDiv = document.createElement('div');
                    fileDiv.className = 'tree-file';
                    fileDiv.innerHTML = `<i class="fa-solid fa-receipt" style="color: #9b59b6;"></i> <span>${item.filename}</span>`;
                    fileDiv.addEventListener('click', () => openModal(item, '/api/remito_file/'));
                    monthContent.appendChild(fileDiv);
                });
                yearContent.appendChild(buildFolder(month, monthContent, true));
            });
            rootDiv.appendChild(buildFolder(year, yearContent, true));
        });

        remitosTreeContainer.appendChild(rootDiv);
    }

    if (searchRemitosInput) {
        searchRemitosInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const filtered = rawRemitosList.filter(item => 
                item.filename.toLowerCase().includes(query) ||
                item.date.toLowerCase().includes(query)
            );
            renderRemitosTree(filtered);
        });
    }

    if (btnRefreshRemitos) {
        btnRefreshRemitos.addEventListener('click', () => {
            if (searchRemitosInput) searchRemitosInput.value = '';
            fetchProcessedRemitos();
            showToast("Remitos actualizados");
        });
    }

    // --- Facturas No Reconocidas con Diagnóstico ---
    const unrecognizedTableBody = document.getElementById('unrecognized-table-body');
    const unrecognizedCount = document.getElementById('unrecognized-count');
    const noUnrecognizedMsg = document.getElementById('no-unrecognized-msg');
    const searchUnrecognizedInput = document.getElementById('search-unrecognized');
    const btnRefreshUnrecognized = document.getElementById('btn-refresh-unrecognized');
    let rawUnrecognizedList = [];

    async function fetchUnrecognizedInvoices() {
        try {
            const res = await fetch('/api/unrecognized_invoices');
            rawUnrecognizedList = await res.json();
            renderUnrecognizedTable(rawUnrecognizedList);
        } catch (e) {
            console.error("Error fetching unrecognized invoices:", e);
            showToast("Error al cargar facturas no reconocidas", "error");
        }
    }

    function renderUnrecognizedTable(list) {
        if (!unrecognizedTableBody) return;
        unrecognizedTableBody.innerHTML = '';
        unrecognizedCount.textContent = `${list.length} archivos`;

        if (list.length === 0) {
            noUnrecognizedMsg.style.display = 'flex';
            if (document.querySelector('#tab-unrecognized .table-container')) {
                document.querySelector('#tab-unrecognized .table-container').style.display = 'none';
            }
            return;
        }

        noUnrecognizedMsg.style.display = 'none';
        if (document.querySelector('#tab-unrecognized .table-container')) {
            document.querySelector('#tab-unrecognized .table-container').style.display = 'block';
        }

        list.forEach(item => {
            const tr = document.createElement('tr');
            
            const tdFile = document.createElement('td');
            tdFile.innerHTML = `<i class="fa-solid fa-file-pdf" style="color: #e74c3c; margin-right: 8px;"></i><strong>${item.filename}</strong>`;

            const tdErrorType = document.createElement('td');
            tdErrorType.innerHTML = `<span class="badge" style="background: rgba(231,76,60,0.2); color: #e74c3c; border: 1px solid rgba(231,76,60,0.3);">${item.error_type}</span>`;

            const tdDate = document.createElement('td');
            tdDate.textContent = item.date || '-';

            const tdDetails = document.createElement('td');
            tdDetails.style.maxWidth = '380px';
            tdDetails.style.fontSize = '0.85rem';
            tdDetails.style.color = 'var(--text-secondary)';
            tdDetails.style.whiteSpace = 'pre-line';
            tdDetails.textContent = item.details;

            const tdAction = document.createElement('td');
            const btnPreview = document.createElement('button');
            btnPreview.className = 'btn btn-secondary btn-icon';
            btnPreview.innerHTML = '<i class="fa-solid fa-eye"></i>';
            btnPreview.title = 'Previsualizar archivo';
            btnPreview.addEventListener('click', () => {
                openModal({ filename: item.filename, path: item.path, supplier: 'No Reconocida' }, '/api/unrecognized_file/');
            });
            tdAction.appendChild(btnPreview);

            tr.appendChild(tdFile);
            tr.appendChild(tdErrorType);
            tr.appendChild(tdDate);
            tr.appendChild(tdDetails);
            tr.appendChild(tdAction);

            unrecognizedTableBody.appendChild(tr);
        });
    }

    if (searchUnrecognizedInput) {
        searchUnrecognizedInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const filtered = rawUnrecognizedList.filter(item => 
                item.filename.toLowerCase().includes(query) ||
                item.error_type.toLowerCase().includes(query) ||
                item.details.toLowerCase().includes(query)
            );
            renderUnrecognizedTable(filtered);
        });
    }

    if (btnRefreshUnrecognized) {
        btnRefreshUnrecognized.addEventListener('click', () => {
            if (searchUnrecognizedInput) searchUnrecognizedInput.value = '';
            fetchUnrecognizedInvoices();
            showToast("No reconocidas actualizadas");
        });
    }

    // --- Modal Logic ---
    const modal = document.getElementById('file-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalIframe = document.getElementById('modal-iframe');
    const closeModalBtn = document.querySelector('.close-modal');

    function openModal(inv, baseUrl = '/api/file/') {
        modalTitle.textContent = inv.supplier ? `${inv.supplier} - ${inv.filename}` : inv.filename;
        const encodedPath = inv.path.split('/').map(encodeURIComponent).join('/');
        modalIframe.src = `${baseUrl}${encodedPath}`;
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
            
            let data;
            try {
                data = await response.json();
            } catch (e) {
                throw new Error(`Respuesta no válida del servidor (${response.status})`);
            }
            
            if (response.ok && data.success) {
                showToast(data.message || "Archivo procesado exitosamente", 'success');
                fetchSuppliers();
            } else {
                showToast(data.message || `Error al procesar el archivo (${response.status})`, 'error');
            }
        } catch (error) {
            console.error("Error upload:", error);
            showToast(error.message || "Error al subir el archivo", 'error');
        } finally {
            // Reset UI
            setTimeout(() => {
                uploadStatus.style.display = 'none';
                dropZone.style.display = 'block';
                fileInput.value = ''; // clear input
            }, 3000);
        }
    }

    // --- Invoice Upload ---
    const invoiceDropZone = document.getElementById('invoice-drop-zone');
    const invoiceFileInput = document.getElementById('invoice-file-upload');

    if (invoiceDropZone && invoiceFileInput) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            invoiceDropZone.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            invoiceDropZone.addEventListener(eventName, () => {
                invoiceDropZone.classList.add('dragover');
                invoiceDropZone.style.background = 'rgba(74, 144, 226, 0.2)';
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            invoiceDropZone.addEventListener(eventName, () => {
                invoiceDropZone.classList.remove('dragover');
                invoiceDropZone.style.background = 'rgba(0,0,0,0.1)';
            }, false);
        });

        invoiceDropZone.addEventListener('drop', (e) => {
            let dt = e.dataTransfer;
            let files = dt.files;
            handleInvoiceFiles(files);
        });

        invoiceFileInput.addEventListener('change', function() {
            handleInvoiceFiles(this.files);
        });

        function handleInvoiceFiles(files) {
            if (files.length === 0) return;
            for (let i = 0; i < files.length; i++) {
                uploadInvoice(files[i]);
            }
            invoiceFileInput.value = '';
        }

        async function uploadInvoice(file) {
            const validExts = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'];
            const fileExt = '.' + file.name.split('.').pop().toLowerCase();
            
            if (!validExts.includes(fileExt)) {
                showToast(`Tipo de archivo no permitido: ${file.name}`, 'error');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            // Cambiar icono temporalmente
            const icon = invoiceDropZone.querySelector('i');
            const oldClass = icon.className;
            icon.className = 'fa-solid fa-spinner fa-spin';

            try {
                const response = await fetch('/api/upload_invoice', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                
                if (data.success) {
                    showToast(`Carga exitosa: ${file.name}`, 'success');
                    fetchStatus(); // Refrescar contadores
                } else {
                    showToast(data.message || `Error al subir ${file.name}`, 'error');
                }
            } catch (error) {
                console.error("Error invoice upload:", error);
                showToast(`Error de red al subir ${file.name}`, 'error');
            } finally {
                icon.className = oldClass;
            }
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
    fetchLicenseStatus(); // Initial fetch
    fetchStatus();
    setInterval(() => {
        const activeTab = document.querySelector('.nav-links li.active');
        if (activeTab && activeTab.dataset.tab === 'dashboard') {
            fetchStatus();
            fetchProgress();
            // We can also poll license periodically if we want, e.g. every 10 mins
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

    // --- ARCA Credentials & Bot Sync ---
    const inputArcaCuit = document.getElementById('input-arca-cuit');
    const inputArcaClave = document.getElementById('input-arca-clave');
    const inputArcaRepresentada = document.getElementById('input-arca-representada');
    const btnSaveArcaCreds = document.getElementById('btn-save-arca-creds');
    const arcaStatusBadge = document.getElementById('arca-status-badge');
    const arcaStatusText = document.getElementById('arca-status-text');
    const btnSyncArca = document.getElementById('btn-sync-arca');
    const btnSyncArcaUpload = document.getElementById('btn-sync-arca-upload');
    const arcaSyncStatusMsg = document.getElementById('arca-sync-status-msg');

    async function fetchArcaCredentials() {
        try {
            const res = await fetch('/api/arca/credentials');
            const data = await res.json();
            if (data.configured) {
                if (inputArcaCuit) inputArcaCuit.value = data.cuit || '';
                if (inputArcaRepresentada) inputArcaRepresentada.value = data.representada || '';
                if (inputArcaClave && data.has_clave) inputArcaClave.value = '••••••••';
                if (arcaStatusBadge && arcaStatusText) {
                    arcaStatusBadge.className = 'status-badge status-active';
                    arcaStatusText.textContent = 'Configurada';
                }
            } else {
                if (arcaStatusBadge && arcaStatusText) {
                    arcaStatusBadge.className = 'status-badge status-inactive';
                    arcaStatusText.textContent = 'Sin configurar';
                }
            }
        } catch (e) {
            console.error("Error fetching ARCA credentials:", e);
        }
    }

    if (btnSaveArcaCreds) {
        btnSaveArcaCreds.addEventListener('click', async () => {
            const cuit = inputArcaCuit.value.trim();
            const clave = inputArcaClave.value.trim();
            const representada = inputArcaRepresentada ? inputArcaRepresentada.value.trim() : '';
            
            if (!cuit || cuit.length !== 11) {
                showToast("Ingresa un CUIT de usuario válido (11 dígitos)", "error");
                return;
            }
            if (!clave) {
                showToast("Ingresa la Clave Fiscal de ARCA", "error");
                return;
            }

            try {
                const res = await fetch('/api/arca/credentials', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cuit, clave, representada })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(data.message, "success");
                    inputArcaClave.value = '••••••••';
                    fetchArcaCredentials();
                } else {
                    showToast(data.message || "Error al guardar credenciales", "error");
                }
            } catch (e) {
                console.error("Error saving ARCA creds:", e);
                showToast("Error de red al guardar credenciales de ARCA", "error");
            }
        });
    }

    let arcaPollInterval = null;

    async function startArcaSync() {
        try {
            const res = await fetch('/api/arca/sync', { method: 'POST' });
            const data = await res.json();
            
            if (!data.success) {
                showToast(data.message, "error");
                return;
            }

            showToast(data.message, "success");
            if (btnSyncArca) btnSyncArca.disabled = true;
            if (btnSyncArcaUpload) btnSyncArcaUpload.disabled = true;

            if (arcaPollInterval) clearInterval(arcaPollInterval);
            arcaPollInterval = setInterval(pollArcaStatus, 2000);
        } catch (e) {
            console.error("Error starting ARCA sync:", e);
            showToast("Error al iniciar la sincronización con ARCA", "error");
        }
    }

    const arcaHeaderBadge = document.getElementById('arca-header-badge');
    const arcaHeaderIcon = document.getElementById('arca-header-icon');
    const arcaHeaderStatusText = document.getElementById('arca-header-status-text');

    async function pollArcaStatus() {
        try {
            const res = await fetch('/api/arca/status');
            const status = await res.json();

            if (arcaSyncStatusMsg) {
                arcaSyncStatusMsg.textContent = status.message || status.step;
            }

            if (arcaHeaderBadge && arcaHeaderStatusText) {
                if (status.running) {
                    arcaHeaderBadge.style.display = 'inline-flex';
                    arcaHeaderBadge.style.background = 'rgba(155, 89, 182, 0.2)';
                    arcaHeaderBadge.style.color = '#9b59b6';
                    arcaHeaderBadge.style.borderColor = 'rgba(155, 89, 182, 0.4)';
                    if (arcaHeaderIcon) arcaHeaderIcon.className = 'fa-solid fa-arrows-rotate fa-spin';
                    arcaHeaderStatusText.textContent = status.message || status.step;
                } else if (status.step === 'COMPLETED') {
                    arcaHeaderBadge.style.display = 'inline-flex';
                    arcaHeaderBadge.style.background = 'rgba(16, 185, 129, 0.2)';
                    arcaHeaderBadge.style.color = '#34d399';
                    arcaHeaderBadge.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                    if (arcaHeaderIcon) arcaHeaderIcon.className = 'fa-solid fa-circle-check';
                    arcaHeaderStatusText.textContent = 'ARCA Sincronizado';
                } else if (status.step === 'ERROR') {
                    arcaHeaderBadge.style.display = 'inline-flex';
                    arcaHeaderBadge.style.background = 'rgba(239, 68, 68, 0.2)';
                    arcaHeaderBadge.style.color = '#f87171';
                    arcaHeaderBadge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
                    if (arcaHeaderIcon) arcaHeaderIcon.className = 'fa-solid fa-triangle-exclamation';
                    arcaHeaderStatusText.textContent = 'Error en ARCA';
                }
            }

            if (!status.running) {
                clearInterval(arcaPollInterval);
                arcaPollInterval = null;
                if (btnSyncArca) btnSyncArca.disabled = false;
                if (btnSyncArcaUpload) btnSyncArcaUpload.disabled = false;

                if (status.step === 'COMPLETED') {
                    showToast(status.message, "success");
                    fetchSuppliers();
                } else if (status.step === 'ERROR') {
                    showToast(status.message || status.last_error, "error");
                }
            }
        } catch (e) {
            console.error("Error polling ARCA status:", e);
        }
    }

    if (btnSyncArca) btnSyncArca.addEventListener('click', startArcaSync);
    if (btnSyncArcaUpload) btnSyncArcaUpload.addEventListener('click', startArcaSync);

    // --- Modal de Logs de ARCA ---
    const btnViewArcaLogs = document.getElementById('btn-view-arca-logs');
    const arcaLogsModal = document.getElementById('arca-logs-modal');
    const arcaLogsContent = document.getElementById('arca-logs-content');
    const btnRefreshArcaLogs = document.getElementById('btn-refresh-arca-logs');
    const closeArcaModalBtns = document.querySelectorAll('.close-arca-modal');

    async function fetchArcaLogs() {
        if (!arcaLogsContent) return;
        arcaLogsContent.textContent = 'Cargando registros...';
        try {
            const res = await fetch('/api/arca/logs');
            const data = await res.json();
            arcaLogsContent.textContent = data.logs || 'No se registraron entradas.';
            arcaLogsContent.scrollTop = arcaLogsContent.scrollHeight;
        } catch (e) {
            arcaLogsContent.textContent = `Error al cargar logs: ${e}`;
        }
    }

    if (btnViewArcaLogs) {
        btnViewArcaLogs.addEventListener('click', () => {
            fetchArcaLogs();
            if (arcaLogsModal) {
                arcaLogsModal.style.display = 'flex';
                arcaLogsModal.classList.add('fade-in');
            }
        });
    }

    if (btnRefreshArcaLogs) {
        btnRefreshArcaLogs.addEventListener('click', fetchArcaLogs);
    }

    closeArcaModalBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (arcaLogsModal) arcaLogsModal.style.display = 'none';
        });
    });

    window.addEventListener('click', (e) => {
        if (e.target == arcaLogsModal) {
            arcaLogsModal.style.display = 'none';
        }
    });

    fetchArcaCredentials();
});
