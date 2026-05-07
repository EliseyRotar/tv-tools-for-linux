// File Transfer JavaScript

let screenshots = [];

// Load page
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('uploadForm').addEventListener('submit', handleUpload);
});

async function handleUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('uploadFile');
    const remotePath = document.getElementById('remotePath').value;
    const file = fileInput.files[0];
    
    if (!file) {
        showToast('Please select a file', 'warning');
        return;
    }
    
    try {
        document.getElementById('uploadProgress').style.display = 'block';
        document.querySelector('#uploadForm button[type="submit"]').disabled = true;
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('remote_path', remotePath);
        
        const response = await fetch('/api/files/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`File uploaded successfully to ${data.remote_path}`, 'success');
            fileInput.value = '';
        } else {
            showToast('Upload failed: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        showToast('Error uploading file: ' + error.message, 'error');
    } finally {
        document.getElementById('uploadProgress').style.display = 'none';
        document.querySelector('#uploadForm button[type="submit"]').disabled = false;
    }
}

async function takeScreenshot() {
    try {
        document.getElementById('screenshotProgress').style.display = 'block';
        
        const response = await api.post('/api/files/screenshot', {});
        
        if (response.success) {
            showToast('Screenshot captured successfully', 'success');
            
            // Add to cache
            await api.post('/api/screenshots/add', {
                filename: response.filename,
                path: response.path
            });
            
            // Add to gallery
            screenshots.unshift({
                filename: response.filename,
                path: response.path,
                timestamp: new Date().toISOString()
            });
            
            updateScreenshotsGallery();
        } else {
            showToast('Screenshot failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error taking screenshot:', error);
        showToast('Error taking screenshot: ' + error.message, 'error');
    } finally {
        document.getElementById('screenshotProgress').style.display = 'none';
    }
}

function updateScreenshotsGallery() {
    const gallery = document.getElementById('screenshotsGallery');
    
    if (screenshots.length === 0) {
        gallery.innerHTML = `
            <div class="col-12 text-center text-muted">
                <i class="bi bi-image" style="font-size: 3rem;"></i>
                <p class="mt-2">No screenshots yet. Take one to get started!</p>
            </div>
        `;
        return;
    }
    
    gallery.innerHTML = '';
    
    screenshots.forEach((screenshot, index) => {
        const col = document.createElement('div');
        col.className = 'col-md-3 mb-3';
        
        const date = new Date(screenshot.timestamp);
        const timeStr = date.toLocaleTimeString();
        
        col.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h6 class="card-title">${escapeHtml(screenshot.filename)}</h6>
                    <p class="card-text"><small class="text-muted">${timeStr}</small></p>
                    <div class="btn-group btn-group-sm w-100" role="group">
                        <a href="/api/files/download?remote_path=${encodeURIComponent(screenshot.path)}" 
                           class="btn btn-primary" download>
                            <i class="bi bi-download"></i> Download
                        </a>
                        <button class="btn btn-danger" onclick="removeScreenshot(${index})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        gallery.appendChild(col);
    });
}

function removeScreenshot(index) {
    screenshots.splice(index, 1);
    updateScreenshotsGallery();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
