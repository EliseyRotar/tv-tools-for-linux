// Advanced Features JavaScript

document.addEventListener('DOMContentLoaded', function() {
    loadScreenshots();
    loadBackups();
    
    document.getElementById('backupForm').addEventListener('submit', handleCreateBackup);
    document.getElementById('batchInstallForm').addEventListener('submit', handleBatchInstall);
});

// ==================== BACKUP & RESTORE ====================

async function handleCreateBackup(e) {
    e.preventDefault();
    
    const name = document.getElementById('backupName').value || `backup_${Date.now()}`;
    const includeApks = document.getElementById('includeApks').checked;
    const includeData = document.getElementById('includeData').checked;
    
    try {
        const response = await api.post('/api/backup/create', {
            name: name,
            include_apks: includeApks,
            include_data: includeData
        });
        
        if (response.success) {
            showToast('Backup created successfully', 'success');
            document.getElementById('backupForm').reset();
            await loadBackups();
        } else {
            showToast('Failed to create backup: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error creating backup:', error);
        showToast('Error creating backup: ' + error.message, 'error');
    }
}

async function loadBackups() {
    try {
        const response = await api.get('/api/backup/list');
        
        if (response.success) {
            displayBackups(response.backups);
        }
    } catch (error) {
        console.error('Error loading backups:', error);
    }
}

function displayBackups(backups) {
    const container = document.getElementById('backupsList');
    
    if (backups.length === 0) {
        container.innerHTML = '<div class="text-muted text-center py-3">No backups available</div>';
        return;
    }
    
    container.innerHTML = backups.map(backup => `
        <div class="list-group-item">
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${escapeHtml(backup.name)}</h6>
                <small>${formatDate(backup.timestamp)}</small>
            </div>
            <p class="mb-1">
                <small class="text-muted">
                    ${backup.include_apks ? '✓ APKs' : ''} 
                    ${backup.include_data ? '✓ Data' : ''}
                </small>
            </p>
            <button class="btn btn-sm btn-primary" onclick="restoreBackup('${backup.name}')">
                <i class="bi bi-arrow-clockwise"></i> Restore
            </button>
        </div>
    `).join('');
}

async function restoreBackup(name) {
    if (!confirm(`Are you sure you want to restore backup "${name}"?`)) {
        return;
    }
    
    showToast('Restore functionality coming soon', 'info');
}

// ==================== BATCH OPERATIONS ====================

async function handleBatchInstall(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('batchApks');
    const files = fileInput.files;
    
    if (files.length === 0) {
        showToast('Please select at least one APK file', 'warning');
        return;
    }
    
    try {
        document.getElementById('batchInstallProgress').style.display = 'block';
        document.querySelector('#batchInstallForm button[type="submit"]').disabled = true;
        
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }
        
        const progressBar = document.getElementById('batchProgressBar');
        const progressText = document.getElementById('batchProgressText');
        
        progressText.textContent = `Installing ${files.length} APKs...`;
        
        const response = await fetch('/api/batch/install', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            progressBar.style.width = '100%';
            progressText.textContent = `Complete: ${data.successful} successful, ${data.failed} failed`;
            
            showToast(`Batch install complete: ${data.successful}/${data.total} successful`, 'success');
            
            fileInput.value = '';
            
            setTimeout(() => {
                document.getElementById('batchInstallProgress').style.display = 'none';
                progressBar.style.width = '0%';
            }, 3000);
        } else {
            showToast('Batch install failed: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error in batch install:', error);
        showToast('Error in batch install: ' + error.message, 'error');
    } finally {
        document.querySelector('#batchInstallForm button[type="submit"]').disabled = false;
    }
}

// ==================== SCREENSHOT GALLERY ====================

async function loadScreenshots() {
    try {
        document.getElementById('loadingGallery').style.display = 'block';
        document.getElementById('galleryContainer').style.display = 'none';
        document.getElementById('noScreenshots').style.display = 'none';
        
        const response = await api.get('/api/screenshots/list');
        
        if (response.success) {
            displayScreenshots(response.screenshots);
        }
    } catch (error) {
        console.error('Error loading screenshots:', error);
    } finally {
        document.getElementById('loadingGallery').style.display = 'none';
    }
}

function displayScreenshots(screenshots) {
    const gallery = document.getElementById('screenshotGallery');
    
    if (screenshots.length === 0) {
        document.getElementById('galleryContainer').style.display = 'none';
        document.getElementById('noScreenshots').style.display = 'block';
        return;
    }
    
    document.getElementById('galleryContainer').style.display = 'block';
    document.getElementById('noScreenshots').style.display = 'none';
    
    gallery.innerHTML = '';
    
    screenshots.forEach(screenshot => {
        const col = document.createElement('div');
        col.className = 'col-md-3 mb-3';
        
        const date = new Date(screenshot.timestamp);
        const timeStr = date.toLocaleString();
        
        col.innerHTML = `
            <div class="card">
                <img src="/api/screenshots/thumbnail/${encodeURIComponent(screenshot.filename)}" 
                     class="card-img-top" 
                     alt="${escapeHtml(screenshot.filename)}"
                     style="cursor: pointer; height: 200px; object-fit: cover;"
                     onclick="viewScreenshot('${screenshot.filename}', '${screenshot.path}')">
                <div class="card-body">
                    <h6 class="card-title text-truncate">${escapeHtml(screenshot.filename)}</h6>
                    <p class="card-text"><small class="text-muted">${timeStr}</small></p>
                    <a href="/api/files/download?remote_path=${encodeURIComponent(screenshot.path)}" 
                       class="btn btn-sm btn-primary" download>
                        <i class="bi bi-download"></i> Download
                    </a>
                </div>
            </div>
        `;
        
        gallery.appendChild(col);
    });
}

function viewScreenshot(filename, path) {
    const modal = new bootstrap.Modal(document.getElementById('screenshotModal'));
    document.getElementById('screenshotModalTitle').textContent = filename;
    document.getElementById('screenshotModalImage').src = `/api/screenshots/thumbnail/${encodeURIComponent(filename)}`;
    document.getElementById('screenshotDownloadBtn').href = `/api/files/download?remote_path=${encodeURIComponent(path)}`;
    modal.show();
}

// ==================== UTILITIES ====================

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


// ==================== ACCESSIBILITY ====================

async function toggleTalkBack(enable) {
    try {
        const response = await api.post('/api/accessibility/talkback', {
            enable: enable
        });
        
        if (response.success) {
            showToast(`TalkBack ${enable ? 'enabled' : 'disabled'}`, 'success');
        } else {
            showToast('Failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error toggling TalkBack:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function configureCaptions(enabled) {
    try {
        const response = await api.post('/api/accessibility/captions', {
            enabled: enabled,
            font_scale: 1.0
        });
        
        if (response.success) {
            showToast(`Captions ${enabled ? 'enabled' : 'disabled'}`, 'success');
        } else {
            showToast('Failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error configuring captions:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function toggleHighContrast(enabled) {
    try {
        const response = await api.post('/api/accessibility/high-contrast', {
            enabled: enabled
        });
        
        if (response.success) {
            showToast('High contrast ' + (enabled ? 'enabled' : 'disabled'), 'success');
        } else {
            showToast('Failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error toggling high contrast:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function setColorCorrection() {
    const mode = parseInt(document.getElementById('colorCorrectionMode').value);
    
    try {
        const response = await api.post('/api/accessibility/color-correction', {
            mode: mode
        });
        
        if (response.success) {
            showToast('Color correction applied', 'success');
        } else {
            showToast('Failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error setting color correction:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function toggleMagnification(enabled) {
    try {
        const response = await api.post('/api/accessibility/magnification', {
            enabled: enabled
        });
        
        if (response.success) {
            showToast('Magnification ' + (enabled ? 'enabled' : 'disabled'), 'success');
        } else {
            showToast('Failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error toggling magnification:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

// ==================== AD BLOCKING (DNS) ====================

async function getDNSStatus() {
    try {
        const response = await api.get('/api/adblock/dns/status');
        
        if (response.success) {
            const statusDiv = document.getElementById('dnsStatus');
            if (response.dns === 'off') {
                statusDiv.innerHTML = '<div class="alert alert-warning">Private DNS is disabled</div>';
            } else if (response.dns === 'opportunistic') {
                statusDiv.innerHTML = '<div class="alert alert-info">Private DNS: Automatic mode</div>';
            } else {
                statusDiv.innerHTML = `<div class="alert alert-success">Private DNS: ${response.dns}</div>`;
            }
        } else {
            showToast('Failed to get DNS status: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error getting DNS status:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function enableAdGuardDNS(familyMode) {
    try {
        const response = await api.post('/api/adblock/dns/adguard', {
            family_mode: familyMode
        });
        
        if (response.success) {
            showToast('AdGuard DNS enabled', 'success');
            getDNSStatus();
        } else {
            showToast('Failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error enabling AdGuard DNS:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function enableControlDDNS(mode) {
    try {
        const response = await api.post('/api/adblock/dns/controld', {
            mode: mode
        });
        
        if (response.success) {
            showToast('ControlD DNS enabled', 'success');
            getDNSStatus();
        } else {
            showToast('Failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error enabling ControlD DNS:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function enableCustomDNS() {
    const hostname = document.getElementById('customDNS').value;
    
    if (!hostname) {
        showToast('Please enter a DNS hostname', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/adblock/dns/custom', {
            hostname: hostname
        });
        
        if (response.success) {
            showToast('Custom DNS enabled', 'success');
            getDNSStatus();
        } else {
            showToast('Failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error enabling custom DNS:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function disableDNS() {
    if (!confirm('Disable Private DNS?')) {
        return;
    }
    
    try {
        const response = await api.post('/api/adblock/dns/disable', {});
        
        if (response.success) {
            showToast('Private DNS disabled', 'success');
            getDNSStatus();
        } else {
            showToast('Failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error disabling DNS:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

// ==================== ADB SHELL ====================

async function executeShellCommand() {
    const command = document.getElementById('shellCommand').value;
    
    if (!command) {
        showToast('Please enter a command', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/shell/execute', {
            command: command
        });
        
        const outputDiv = document.getElementById('shellOutput');
        const outputContent = document.getElementById('shellOutputContent');
        
        outputDiv.style.display = 'block';
        outputContent.textContent = response.output || (response.success ? 'Command executed successfully' : 'Command failed');
        
        if (response.success) {
            showToast('Command executed', 'success');
        } else {
            showToast('Command failed', 'error');
        }
    } catch (error) {
        console.error('Error executing command:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function showCommonCommands() {
    try {
        const response = await api.get('/api/shell/commands');
        
        if (response.success && response.commands) {
            const listDiv = document.getElementById('commonCommandsList');
            let html = '';
            
            for (const [cmd, info] of Object.entries(response.commands)) {
                html += `
                    <div class="mb-3">
                        <h6><code>${cmd}</code> - ${info.description}</h6>
                        <ul class="list-unstyled ms-3">
                            ${info.examples.map(ex => `
                                <li class="mb-1">
                                    <code class="text-primary">${ex}</code>
                                    <button class="btn btn-sm btn-outline-primary ms-2" 
                                            onclick="useCommand('${ex.replace(/'/g, "\\'")}')">
                                        Use
                                    </button>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `;
            }
            
            listDiv.innerHTML = html;
            const modal = new bootstrap.Modal(document.getElementById('commonCommandsModal'));
            modal.show();
        }
    } catch (error) {
        console.error('Error loading commands:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

function useCommand(command) {
    document.getElementById('shellCommand').value = command;
    bootstrap.Modal.getInstance(document.getElementById('commonCommandsModal')).hide();
}

async function showShellHistory() {
    try {
        const response = await api.get('/api/shell/history');
        
        if (response.success && response.history) {
            const listDiv = document.getElementById('shellHistoryList');
            
            if (response.history.length === 0) {
                listDiv.innerHTML = '<p class="text-muted">No command history</p>';
            } else {
                listDiv.innerHTML = `
                    <div class="list-group">
                        ${response.history.map((cmd, idx) => `
                            <div class="list-group-item">
                                <code>${cmd}</code>
                                <button class="btn btn-sm btn-outline-primary float-end" 
                                        onclick="useCommand('${cmd.replace(/'/g, "\\'")}')">
                                    Use
                                </button>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            const modal = new bootstrap.Modal(document.getElementById('shellHistoryModal'));
            modal.show();
        }
    } catch (error) {
        console.error('Error loading history:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

// ==================== ICON GENERATOR ====================

async function detectHiddenApps() {
    try {
        showToast('Detecting hidden apps...', 'info');
        
        const response = await api.post('/api/icons/detect', {});
        
        if (response.success && response.apps) {
            const listDiv = document.getElementById('hiddenAppsList');
            
            if (response.apps.length === 0) {
                listDiv.innerHTML = '<div class="alert alert-success">No hidden apps found</div>';
            } else {
                listDiv.innerHTML = `
                    <div class="alert alert-info">Found ${response.apps.length} hidden app(s)</div>
                    <div class="list-group" style="max-height: 300px; overflow-y: auto;">
                        ${response.apps.map(app => `
                            <div class="list-group-item d-flex justify-content-between align-items-center">
                                <small>${app}</small>
                                <button class="btn btn-sm btn-primary" onclick="generateIconForApp('${app}')">
                                    <i class="bi bi-plus"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button class="btn btn-success w-100 mt-2" onclick="batchGenerateIcons(${JSON.stringify(response.apps)})">
                        <i class="bi bi-stack"></i> Generate All
                    </button>
                `;
            }
            
            showToast(`Found ${response.apps.length} hidden app(s)`, 'success');
        } else {
            showToast('Failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error detecting hidden apps:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function generateSingleIcon() {
    const packageName = document.getElementById('iconPackage').value;
    const label = document.getElementById('iconLabel').value;
    
    if (!packageName) {
        showToast('Please enter a package name', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/icons/generate', {
            package: packageName,
            label: label || null
        });
        
        if (response.success) {
            showToast('Icon generated successfully', 'success');
            document.getElementById('iconPackage').value = '';
            document.getElementById('iconLabel').value = '';
        } else {
            showToast('Failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error generating icon:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

function generateIconForApp(packageName) {
    document.getElementById('iconPackage').value = packageName;
    generateSingleIcon();
}

async function batchGenerateIcons(packages) {
    if (!confirm(`Generate icons for ${packages.length} apps?`)) {
        return;
    }
    
    try {
        const response = await api.post('/api/icons/batch-generate', {
            packages: packages
        });
        
        if (response.success) {
            showToast(`Generated ${response.successful} icons, ${response.failed} failed`, 'success');
            document.getElementById('hiddenAppsList').innerHTML = '';
        } else {
            showToast('Failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error batch generating icons:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

// ==================== APP INSTALLER ====================

async function loadInstallableApps() {
    const category = document.getElementById('appCategory').value;
    
    try {
        const response = await api.get(`/api/installer/apps${category ? '?category=' + category : ''}`);
        
        if (response.success && response.apps) {
            const listDiv = document.getElementById('installableAppsList');
            
            if (response.apps.length === 0) {
                listDiv.innerHTML = '<div class="text-muted text-center py-3">No apps found</div>';
            } else {
                listDiv.innerHTML = response.apps.map(app => `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-1">${app.name}</h6>
                                <small class="text-muted">${app.description || ''}</small>
                            </div>
                            <button class="btn btn-sm btn-primary" onclick="installAppById('${app.id}', '${app.name}')">
                                <i class="bi bi-download"></i> Install
                            </button>
                        </div>
                    </div>
                `).join('');
            }
        } else {
            showToast('Failed to load apps: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error loading apps:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function installAppById(appId, appName) {
    if (!confirm(`Install ${appName}?`)) {
        return;
    }
    
    try {
        showToast(`Installing ${appName}...`, 'info');
        
        const response = await api.post('/api/installer/install', {
            app_id: appId
        });
        
        if (response.success) {
            showToast(`${appName} installed successfully`, 'success');
        } else {
            showToast('Installation failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error installing app:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

// ==================== UPDATE CHECKER ====================

async function checkForUpdates() {
    try {
        showToast('Checking for updates...', 'info');
        
        const response = await api.post('/api/updates/check', {});
        
        if (response.success) {
            document.getElementById('currentVersion').textContent = response.current_version;
            document.getElementById('latestVersion').textContent = response.latest_version;
            
            if (response.has_update) {
                document.getElementById('updateInfo').style.display = 'block';
                document.getElementById('noUpdate').style.display = 'none';
                showToast('Update available!', 'success');
            } else {
                document.getElementById('updateInfo').style.display = 'none';
                document.getElementById('noUpdate').style.display = 'block';
                showToast('You are up to date', 'success');
            }
        } else {
            showToast('Failed to check updates: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error checking updates:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function viewChangelog() {
    try {
        const response = await api.get('/api/updates/changelog');
        
        if (response.success && response.changelog) {
            document.getElementById('changelogContent').textContent = response.changelog;
            const modal = new bootstrap.Modal(document.getElementById('changelogModal'));
            modal.show();
        } else {
            showToast('No changelog available', 'warning');
        }
    } catch (error) {
        console.error('Error loading changelog:', error);
        showToast('Error: ' + error.message, 'error');
    }
}

async function getDownloadURL() {
    try {
        const response = await api.get('/api/updates/download-url');
        
        if (response.success && response.url) {
            window.open(response.url, '_blank');
            showToast('Opening download page...', 'info');
        } else {
            showToast('No download URL available', 'warning');
        }
    } catch (error) {
        console.error('Error getting download URL:', error);
        showToast('Error: ' + error.message, 'error');
    }
}
