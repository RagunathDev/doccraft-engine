document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const dropzone = document.getElementById('dropzone');
    const previewArea = document.getElementById('previewArea');
    const workspace = document.getElementById('workspace');
    const hero = document.getElementById('hero');
    const convertBtn = document.getElementById('convertBtn');
    const mergeBtn = document.getElementById('mergeBtn');
    const clearAllBtn = document.getElementById('clearAllBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const successModal = new bootstrap.Modal(document.getElementById('successModal'));
    const downloadLink = document.getElementById('downloadLink');
    const downloadList = document.getElementById('downloadList');

    // Tool Actions Containers
    const pdfActions = document.getElementById('pdfActions');
    const compressActions = document.getElementById('compressActions');
    const batchCompressBtn = document.getElementById('batchCompressBtn');
    const addFilesBtn = document.getElementById('addFilesBtn');

    // New Tool Elements
    const compressorSection = document.getElementById('compressor');
    const compressInput = document.getElementById('compressInput');
    const compressDropzone = document.getElementById('compressDropzone');
    const qualitySlider = document.getElementById('qualitySlider');
    const qualityVal = document.getElementById('qualityVal');
    const counterValue = document.getElementById('counterValue');

    let uploadedFiles = [];
    let currentMode = 'pdf'; // 'pdf' or 'compress'
    const API_BASE = 'http://localhost:5001/api';

    // Tool Switching
    window.showTool = (tool) => {
        uploadedFiles = [];
        updateUI();
        if (tool === 'compressor') {
            currentMode = 'compress';
            hero.classList.add('d-none');
            compressorSection.classList.remove('d-none');
            pdfActions.classList.add('d-none');
            compressActions.classList.remove('d-none');
        } else {
            currentMode = 'pdf';
            compressorSection.classList.add('d-none');
            hero.classList.remove('d-none');
            pdfActions.classList.remove('d-none');
            compressActions.classList.add('d-none');
        }
    };

    addFilesBtn.addEventListener('click', () => {
        if (currentMode === 'pdf') fileInput.click();
        else compressInput.click();
    });

    // Quality Slider
    qualitySlider.addEventListener('input', (e) => {
        qualityVal.textContent = e.target.value;
    });

    // 3D Tilt Effect - Refined/Slower
    document.querySelectorAll('.tilt-element').forEach(el => {
        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = (centerY - y) / 25; // Slower speed
            const rotateY = (x - centerX) / 25; // Slower speed
            el.style.transition = 'transform 0.1s linear';
            el.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
        });

        el.addEventListener('mouseleave', () => {
            el.style.transition = 'transform 1s cubic-bezier(0.2, 0, 0.2, 1)';
            el.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
        });
    });

    // Usage Counter Update
    const updateCounter = async () => {
        try {
            const response = await fetch(`${API_BASE}/counter`);
            const data = await response.json();
            counterValue.textContent = data.count || 0;
        } catch (e) {
            console.error('Counter error:', e);
        }
    };
    updateCounter();
    setInterval(updateCounter, 30000); // Update every 30s

    // Drag and Drop Handlers
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    [dropzone, compressDropzone].forEach(el => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            el.addEventListener(eventName, preventDefaults, false);
        });
        ['dragenter', 'dragover'].forEach(eventName => {
            el.addEventListener(eventName, () => el.classList.add('dragover'), false);
        });
        ['dragleave', 'drop'].forEach(eventName => {
            el.addEventListener(eventName, () => el.classList.remove('dragover'), false);
        });
    });

    dropzone.addEventListener('drop', (e) => handleFiles(e.dataTransfer.files));
    compressDropzone.addEventListener('drop', (e) => handleFiles(e.dataTransfer.files));
    fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
    compressInput.addEventListener('change', (e) => handleFiles(e.target.files));

    async function handleFiles(files) {
        if (files.length === 0) return;

        showLoading(true);
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await fetch(`${API_BASE}/upload`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (data.files) {
                uploadedFiles = [...uploadedFiles, ...data.files];
                updateUI();
                workspace.scrollIntoView({ behavior: 'smooth' });
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('Error uploading files.');
        } finally {
            showLoading(false);
            updateCounter();
        }
    }

    function updateUI() {
        if (uploadedFiles.length > 0) {
            workspace.classList.remove('d-none');
        } else {
            workspace.classList.add('d-none');
        }

        previewArea.innerHTML = '';
        uploadedFiles.forEach((file, index) => {
            const isPdf = file.original_name.toLowerCase().endsWith('.pdf');
            const col = document.createElement('div');
            col.className = 'col-6 col-md-3 col-lg-2';
            col.innerHTML = `
                <div class="preview-item">
                    <div class="item-actions">
                        <button class="btn btn-danger btn-sm rounded-circle" onclick="removeFile(${index})">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    ${isPdf ?
                    '<div class="d-flex align-items-center justify-content-center bg-light preview-thumb"><i class="fas fa-file-pdf fa-3x text-danger"></i></div>' :
                    `<img src="${API_BASE}/download/${file.server_name}" class="preview-thumb" alt="${file.original_name}">`
                }
                    <div class="preview-info">
                        <p class="text-truncate mb-0 small">${file.original_name}</p>
                    </div>
                </div>
            `;
            previewArea.appendChild(col);
        });

        // Hide/Show tool specific actions
        const hasPdf = uploadedFiles.some(f => f.original_name.toLowerCase().endsWith('.pdf'));
        if (currentMode === 'pdf') {
            if (hasPdf && uploadedFiles.length > 1) {
                mergeBtn.classList.remove('d-none');
                convertBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Process PDF';
            } else {
                mergeBtn.classList.add('d-none');
                convertBtn.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Generate PDF';
            }
        }
    }

    window.removeFile = (index) => {
        uploadedFiles.splice(index, 1);
        updateUI();
    };

    clearAllBtn.addEventListener('click', () => {
        uploadedFiles = [];
        updateUI();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    convertBtn.addEventListener('click', async () => {
        if (uploadedFiles.length === 0) return;
        showLoading(true);
        const fileNameBase = document.getElementById('outputName').value || 'DocCreft_Export';
        const payload = {
            files: uploadedFiles.map(f => f.server_name),
            output_name: fileNameBase
        };

        try {
            const response = await fetch(`${API_BASE}/convert`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            if (data.pdf_url) {
                downloadList.innerHTML = '';
                downloadLink.classList.remove('d-none');
                downloadLink.href = `${API_BASE}/download/${data.filename}`;
                downloadLink.setAttribute('download', `${fileNameBase}.pdf`);
                addDownloadItem(`${fileNameBase}.pdf`, `${API_BASE}/download/${data.filename}`);
                successModal.show();
            }
        } catch (error) {
            console.error('Conversion error:', error);
        } finally {
            showLoading(false);
            updateCounter();
        }
    });

    batchCompressBtn.addEventListener('click', async () => {
        if (uploadedFiles.length === 0) return;
        showLoading(true);
        downloadList.innerHTML = '';
        downloadLink.classList.add('d-none');
        const quality = parseInt(qualitySlider.value);
        const customBaseName = document.getElementById('outputName').value || 'DocCreft_Compressed';

        try {
            for (let i = 0; i < uploadedFiles.length; i++) {
                const file = uploadedFiles[i];
                const response = await fetch(`${API_BASE}/compress`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ file: file.server_name, quality: quality })
                });
                const data = await response.json();

                if (data.url) {
                    const finalName = `${customBaseName}_${i + 1}.jpg`;
                    addDownloadItem(finalName, `${API_BASE}/download/${data.filename}`);
                }
            }
            successModal.show();
        } catch (error) {
            console.error('Batch compress error:', error);
        } finally {
            showLoading(false);
            updateCounter();
        }
    });

    function addDownloadItem(name, url) {
        const div = document.createElement('div');
        div.className = 'col-12';
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center bg-light p-3 rounded mb-2 border shadow-sm">
                <span class="text-truncate fw-bold" style="max-width: 70%">${name}</span>
                <a href="${url}" download="${name}" class="btn btn-primary btn-sm px-3">
                    <i class="fas fa-download me-1"></i> Download
                </a>
            </div>
        `;
        downloadList.appendChild(div);
    }

    function showLoading(show) {
        if (show) loadingOverlay.classList.remove('d-none');
        else loadingOverlay.classList.add('d-none');
    }
});
