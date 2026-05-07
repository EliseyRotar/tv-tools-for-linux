// Apps Management JavaScript

let currentFilter = 'all';
let allApps = [];

document.addEventListener('DOMContentLoaded', function() {
    loadApps();
    document.getElementById('searchInput').addEventListener('input', filterApps);
});

function setFilter(filter, btn) {
    currentFilter = filter;
    // Update active tab
    document.querySelectorAll('#appTabs .nav-link').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterApps();
}

async function loadApps() {
    try {
        document.getElementById('loadingApps').style.display = 'block';
        document.getElementById('appsTable').style.display = 'none';
        document.getElementById('noApps').style.display = 'none';
        
        const response = await api.get('/api/apps/list?filter=all');
        
        if (response.success) {
            allApps = response.packages;
            displayApps(allApps);
        } else {
            showToast('Failed to load apps', 'error');
        }
    } catch (error) {
        console.error('Error loading apps:', error);
        showToast('Error loading apps: ' + error.message, 'error');
    } finally {
        document.getElementById('loadingApps').style.display = 'none';
    }
}

function displayApps(apps) {
    const tbody = document.getElementById('appsTableBody');
    tbody.innerHTML = '';
    
    if (apps.length === 0) {
        document.getElementById('appsTable').style.display = 'none';
        document.getElementById('noApps').style.display = 'block';
        return;
    }
    
    document.getElementById('appsTable').style.display = 'block';
    document.getElementById('noApps').style.display = 'none';
    
    apps.forEach(app => {
        const row = document.createElement('tr');
        
        const typeIcon = app.is_system ? '⚙️' : '📦';
        const statusBadge = app.is_enabled 
            ? '<span class="badge bg-success">On</span>' 
            : '<span class="badge bg-secondary">Off</span>';
        const displayName = (app.label && app.label !== app.package_name) ? app.label : '';
        
        row.innerHTML = `
            <td class="text-center">${typeIcon}</td>
            <td class="text-center">${statusBadge}</td>
            <td>
                ${displayName ? `<div class="fw-semibold small">${escapeHtml(displayName)}</div>` : ''}
                <div class="text-muted" style="font-size:0.75rem">${escapeHtml(app.package_name)}</div>
            </td>
            <td class="small text-muted">${escapeHtml(app.version_name || 'N/A')}</td>
            <td>
                <div class="d-flex gap-1">
                    ${app.is_enabled 
                        ? `<button class="btn btn-outline-warning btn-sm" onclick="disableApp('${app.package_name}')" title="Disable"><i class="bi bi-pause-fill"></i></button>`
                        : `<button class="btn btn-outline-success btn-sm" onclick="enableApp('${app.package_name}')" title="Enable"><i class="bi bi-play-fill"></i></button>`
                    }
                    <button class="btn btn-outline-danger btn-sm" onclick="uninstallApp('${app.package_name}', ${app.is_system})" title="Uninstall"><i class="bi bi-trash"></i></button>
                </div>
            </td>
        `;
        
        tbody.appendChild(row);
    });
    
    document.getElementById('appsCount').textContent = `Total: ${apps.length} apps`;
}

function filterApps() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    let filtered = allApps;
    
    // Filter by type
    if (currentFilter === 'user') {
        filtered = filtered.filter(app => !app.is_system);
    } else if (currentFilter === 'system') {
        filtered = filtered.filter(app => app.is_system);
    }
    
    // Filter by search term
    if (searchTerm) {
        filtered = filtered.filter(app => 
            app.package_name.toLowerCase().includes(searchTerm) ||
            (app.label && app.label.toLowerCase().includes(searchTerm))
        );
    }
    
    displayApps(filtered);
}

async function installAPK() {
    const fileInput = document.getElementById('apkFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showToast('Please select an APK file', 'warning');
        return;
    }
    
    if (!file.name.endsWith('.apk')) {
        showToast('File must be an APK', 'error');
        return;
    }
    
    try {
        document.getElementById('installProgress').style.display = 'block';
        document.querySelector('#installModal .btn-primary').disabled = true;
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/apps/install', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('App installed successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('installModal')).hide();
            fileInput.value = '';
            await loadApps();
        } else {
            showToast('Installation failed: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error installing APK:', error);
        showToast('Error installing APK: ' + error.message, 'error');
    } finally {
        document.getElementById('installProgress').style.display = 'none';
        document.querySelector('#installModal .btn-primary').disabled = false;
    }
}

async function uninstallApp(packageName, isSystem) {
    if (!confirm(`Are you sure you want to uninstall ${packageName}?`)) {
        return;
    }
    
    try {
        const response = await api.post('/api/apps/uninstall', {
            package_name: packageName,
            system_app: isSystem
        });
        
        if (response.success) {
            showToast('App uninstalled successfully', 'success');
            await loadApps();
        } else {
            showToast('Uninstall failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error uninstalling app:', error);
        showToast('Error uninstalling app: ' + error.message, 'error');
    }
}

async function enableApp(packageName) {
    try {
        const response = await api.post('/api/apps/enable', {
            package_name: packageName
        });
        
        if (response.success) {
            showToast('App enabled successfully', 'success');
            await loadApps();
        } else {
            showToast('Enable failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error enabling app:', error);
        showToast('Error enabling app: ' + error.message, 'error');
    }
}

async function disableApp(packageName) {
    if (!confirm(`Are you sure you want to disable ${packageName}?`)) {
        return;
    }
    
    try {
        const response = await api.post('/api/apps/disable', {
            package_name: packageName
        });
        
        if (response.success) {
            showToast('App disabled successfully', 'success');
            await loadApps();
        } else {
            showToast('Disable failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error disabling app:', error);
        showToast('Error disabling app: ' + error.message, 'error');
    }
}

function refreshApps() {
    loadApps();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
