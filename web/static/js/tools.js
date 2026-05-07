// Tools & Utilities JavaScript

// ==================== BLOATWARE REMOVAL ====================

async function listBloatware() {
    const category = document.getElementById('bloatwareCategory').value;
    
    try {
        const response = await api.get(`/api/bloatware/list?category=${category}`);
        
        if (response.success && response.packages) {
            displayBloatwareList(response.packages, category);
        } else {
            showToast('Failed to load bloatware list', 'error');
        }
    } catch (error) {
        console.error('Error loading bloatware:', error);
        showToast('Error loading bloatware: ' + error.message, 'error');
    }
}

function displayBloatwareList(packages, category) {
    const listDiv = document.getElementById('bloatwareList');
    
    if (packages.length === 0) {
        listDiv.innerHTML = '<p class="text-muted">No bloatware packages found</p>';
    } else {
        listDiv.innerHTML = `
            <div class="alert alert-info">
                <strong>Category:</strong> ${category.toUpperCase()}<br>
                <strong>Packages:</strong> ${packages.length}
            </div>
            <div class="list-group">
                ${packages.map(pkg => `
                    <div class="list-group-item">
                        <h6>${pkg.name || pkg.package}</h6>
                        <small class="text-muted">${pkg.package}</small>
                        ${pkg.description ? `<p class="mb-0 mt-1"><small>${pkg.description}</small></p>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('bloatwareModal'));
    modal.show();
}

async function removeBloatware() {
    const category = document.getElementById('bloatwareCategory').value;
    
    if (!confirm(`Are you sure you want to remove all ${category} bloatware? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await api.post('/api/bloatware/remove', {
            category: category
        });
        
        if (response.success) {
            showToast(response.message || 'Bloatware removed successfully', 'success');
        } else {
            showToast('Failed to remove bloatware: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error removing bloatware:', error);
        showToast('Error removing bloatware: ' + error.message, 'error');
    }
}

// ==================== APP LAUNCHER ====================

async function launchCommonApp() {
    const appKey = document.getElementById('commonApp').value;
    
    if (!appKey) {
        showToast('Please select an app', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/launcher/common', {
            app_key: appKey
        });
        
        if (response.success) {
            showToast('App launched successfully', 'success');
        } else {
            showToast('Failed to launch app: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error launching app:', error);
        showToast('Error launching app: ' + error.message, 'error');
    }
}

async function openSettingsPage() {
    const settingsKey = document.getElementById('settingsPage').value;
    
    if (!settingsKey) {
        showToast('Please select a settings page', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/launcher/settings', {
            settings_key: settingsKey
        });
        
        if (response.success) {
            showToast('Settings page opened successfully', 'success');
        } else {
            showToast('Failed to open settings: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error opening settings:', error);
        showToast('Error opening settings: ' + error.message, 'error');
    }
}

// ==================== KEYBOARD REMOTE ====================

async function sendKey(keycode) {
    try {
        const response = await api.post('/api/remote/sendkey', {
            keycode: keycode
        });
        
        if (!response.success) {
            showToast('Failed to send key: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error sending key:', error);
        showToast('Error sending key: ' + error.message, 'error');
    }
}

// ==================== POWER MANAGEMENT ====================

async function wakeDevice() {
    try {
        const response = await api.post('/api/power/wake', {});
        
        if (response.success) {
            showToast('Wake command sent', 'success');
        } else {
            showToast('Failed to wake device: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error waking device:', error);
        showToast('Error waking device: ' + error.message, 'error');
    }
}

async function sleepDevice() {
    try {
        const response = await api.post('/api/power/sleep', {});
        
        if (response.success) {
            showToast('Sleep command sent', 'success');
        } else {
            showToast('Failed to sleep device: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error sleeping device:', error);
        showToast('Error sleeping device: ' + error.message, 'error');
    }
}

async function rebootDevice() {
    if (!confirm('Are you sure you want to reboot the device?')) {
        return;
    }
    
    try {
        const response = await api.post('/api/power/reboot', {});
        
        if (response.success) {
            showToast('Reboot command sent', 'success');
        } else {
            showToast('Failed to reboot device: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error rebooting device:', error);
        showToast('Error rebooting device: ' + error.message, 'error');
    }
}

async function getBatteryInfo() {
    try {
        const response = await api.get('/api/power/battery');
        
        if (response.success && response.battery) {
            const battery = response.battery;
            const level = battery.level || 'Unknown';
            const status = battery.status || 'Unknown';
            const health = battery.health || 'Unknown';
            
            showToast(`Battery: ${level}% | Status: ${status} | Health: ${health}`, 'info');
        } else {
            showToast('Failed to get battery info: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error getting battery info:', error);
        showToast('Error getting battery info: ' + error.message, 'error');
    }
}

// ==================== NETWORK SCANNER ====================

async function scanNetwork() {
    try {
        document.getElementById('scanProgress').style.display = 'block';
        document.getElementById('scanResults').innerHTML = '';
        
        const response = await api.post('/api/network/scan', {});
        
        if (response.success) {
            displayScanResults(response.devices);
            showToast(`Found ${response.devices.length} device(s)`, 'success');
        } else {
            showToast('Network scan failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error scanning network:', error);
        showToast('Error scanning network: ' + error.message, 'error');
    } finally {
        document.getElementById('scanProgress').style.display = 'none';
    }
}

function displayScanResults(devices) {
    const resultsDiv = document.getElementById('scanResults');
    
    if (devices.length === 0) {
        resultsDiv.innerHTML = '<p class="text-muted">No devices found</p>';
        return;
    }
    
    resultsDiv.innerHTML = `
        <div class="list-group">
            ${devices.map(device => `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${device.ip}:${device.port}</h6>
                        <button class="btn btn-sm btn-primary" onclick="connectToScannedDevice('${device.ip}', ${device.port})">
                            Connect
                        </button>
                    </div>
                    <small class="text-muted">${device.hostname}</small>
                </div>
            `).join('')}
        </div>
    `;
}

async function connectToScannedDevice(ip, port) {
    try {
        const response = await api.post('/api/devices/connect', {
            ip_address: ip,
            port: port
        });
        
        if (response.success) {
            showToast('Connected successfully', 'success');
            updateDeviceStatus(true, response.device);
        } else {
            showToast('Connection failed: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error connecting:', error);
        showToast('Error connecting: ' + error.message, 'error');
    }
}

// ==================== OPTIMIZATION ====================

async function disableAnimations() {
    if (!confirm('This will disable all animations on the device. Continue?')) {
        return;
    }
    
    try {
        const response = await api.post('/api/optimization/disable-animations', {});
        
        if (response.success) {
            showToast('Animations disabled successfully', 'success');
        } else {
            showToast('Failed to disable animations: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error disabling animations:', error);
        showToast('Error disabling animations: ' + error.message, 'error');
    }
}

async function clearAppCache() {
    if (!confirm('This will clear cache for all apps. Continue?')) {
        return;
    }
    
    try {
        const response = await api.post('/api/optimization/clear-app-cache', {});
        
        if (response.success) {
            showToast('App cache cleared successfully', 'success');
        } else {
            showToast('Failed to clear app cache: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error clearing app cache:', error);
        showToast('Error clearing app cache: ' + error.message, 'error');
    }
}

async function clearSystemCache() {
    if (!confirm('This will clear system cache. The device may need to reboot. Continue?')) {
        return;
    }
    
    try {
        const response = await api.post('/api/optimization/clear-system-cache', {});
        
        if (response.success) {
            showToast('System cache cleared successfully', 'success');
        } else {
            showToast('Failed to clear system cache: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error clearing system cache:', error);
        showToast('Error clearing system cache: ' + error.message, 'error');
    }
}


// ==================== VOICE COMMANDS ====================

async function triggerVoiceInput() {
    try {
        const response = await api.post('/api/voice/trigger', {});
        
        if (response.success) {
            showToast('Voice input triggered', 'success');
        } else {
            showToast('Failed to trigger voice input: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error triggering voice input:', error);
        showToast('Error triggering voice input: ' + error.message, 'error');
    }
}

async function voiceSearch() {
    const query = document.getElementById('voiceSearchQuery').value;
    
    if (!query) {
        showToast('Please enter a search query', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/voice/search', {
            query: query
        });
        
        if (response.success) {
            showToast('Voice search initiated', 'success');
        } else {
            showToast('Failed to search: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error with voice search:', error);
        showToast('Error with voice search: ' + error.message, 'error');
    }
}

async function youtubeSearch() {
    const query = document.getElementById('voiceSearchQuery').value;
    
    if (!query) {
        showToast('Please enter a search query', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/voice/youtube-search', {
            query: query
        });
        
        if (response.success) {
            showToast('YouTube search opened', 'success');
        } else {
            showToast('Failed to open YouTube: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error with YouTube search:', error);
        showToast('Error with YouTube search: ' + error.message, 'error');
    }
}

async function triggerAssistant() {
    try {
        const response = await api.post('/api/voice/assistant', {});
        
        if (response.success) {
            showToast('Google Assistant triggered', 'success');
        } else {
            showToast('Failed to trigger Assistant: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error triggering Assistant:', error);
        showToast('Error triggering Assistant: ' + error.message, 'error');
    }
}

async function sendTextInput() {
    const text = document.getElementById('textInput').value;
    
    if (!text) {
        showToast('Please enter text to send', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/voice/text-input', {
            text: text
        });
        
        if (response.success) {
            showToast('Text sent successfully', 'success');
            document.getElementById('textInput').value = '';
        } else {
            showToast('Failed to send text: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error sending text:', error);
        showToast('Error sending text: ' + error.message, 'error');
    }
}

// ==================== PERMISSION MANAGER ====================

async function listPermissions() {
    const packageName = document.getElementById('permPackage').value;
    
    if (!packageName) {
        showToast('Please enter a package name', 'warning');
        return;
    }
    
    try {
        const response = await api.get(`/api/permissions/list?package=${packageName}`);
        
        if (response.success && response.permissions) {
            displayPermissions(response.permissions, packageName);
        } else {
            showToast('Failed to list permissions: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error listing permissions:', error);
        showToast('Error listing permissions: ' + error.message, 'error');
    }
}

function displayPermissions(permissions, packageName) {
    const listDiv = document.getElementById('permissionsList');
    
    const granted = permissions.granted || [];
    const denied = permissions.denied || [];
    
    listDiv.innerHTML = `
        <div class="alert alert-info">
            <strong>Package:</strong> ${packageName}<br>
            <strong>Granted:</strong> ${granted.length} | <strong>Denied:</strong> ${denied.length}
        </div>
        
        ${granted.length > 0 ? `
            <h6 class="text-success">Granted Permissions</h6>
            <div class="list-group mb-3">
                ${granted.map(perm => `
                    <div class="list-group-item">
                        <i class="bi bi-check-circle text-success"></i> ${perm}
                    </div>
                `).join('')}
            </div>
        ` : ''}
        
        ${denied.length > 0 ? `
            <h6 class="text-danger">Denied Permissions</h6>
            <div class="list-group">
                ${denied.map(perm => `
                    <div class="list-group-item">
                        <i class="bi bi-x-circle text-danger"></i> ${perm}
                    </div>
                `).join('')}
            </div>
        ` : ''}
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('permissionsModal'));
    modal.show();
}

async function grantPermission() {
    const packageName = document.getElementById('permPackage').value;
    const permission = document.getElementById('permissionName').value;
    
    if (!packageName || !permission) {
        showToast('Please enter package name and permission', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/permissions/grant', {
            package: packageName,
            permission: permission
        });
        
        if (response.success) {
            showToast('Permission granted successfully', 'success');
        } else {
            showToast('Failed to grant permission: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error granting permission:', error);
        showToast('Error granting permission: ' + error.message, 'error');
    }
}

async function revokePermission() {
    const packageName = document.getElementById('permPackage').value;
    const permission = document.getElementById('permissionName').value;
    
    if (!packageName || !permission) {
        showToast('Please enter package name and permission', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/permissions/revoke', {
            package: packageName,
            permission: permission
        });
        
        if (response.success) {
            showToast('Permission revoked successfully', 'success');
        } else {
            showToast('Failed to revoke permission: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error revoking permission:', error);
        showToast('Error revoking permission: ' + error.message, 'error');
    }
}

// ==================== STORAGE MANAGER ====================

async function getStorageInfo() {
    try {
        const response = await api.get('/api/storage/info');
        
        if (response.success && response.storage) {
            const storage = response.storage;
            document.getElementById('storageInfo').innerHTML = `
                <div class="alert alert-info">
                    <strong>Total:</strong> ${storage.total || 'Unknown'}<br>
                    <strong>Used:</strong> ${storage.used || 'Unknown'} (${storage.percentage || 'Unknown'})<br>
                    <strong>Available:</strong> ${storage.available || 'Unknown'}
                </div>
            `;
            showToast('Storage info retrieved', 'success');
        } else {
            showToast('Failed to get storage info: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error getting storage info:', error);
        showToast('Error getting storage info: ' + error.message, 'error');
    }
}

async function clearAllCache() {
    if (!confirm('This will clear cache for all apps. Continue?')) {
        return;
    }
    
    try {
        const response = await api.post('/api/storage/clear-cache', {});
        
        if (response.success) {
            showToast('Cache cleared successfully', 'success');
            getStorageInfo(); // Refresh storage info
        } else {
            showToast('Failed to clear cache: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error clearing cache:', error);
        showToast('Error clearing cache: ' + error.message, 'error');
    }
}

async function clearAppDataByPackage() {
    const packageName = document.getElementById('clearDataPackage').value;
    
    if (!packageName) {
        showToast('Please enter a package name', 'warning');
        return;
    }
    
    if (!confirm(`This will delete ALL data for ${packageName}. This cannot be undone. Continue?`)) {
        return;
    }
    
    try {
        const response = await api.post('/api/storage/clear-app-data', {
            package: packageName
        });
        
        if (response.success) {
            showToast('App data cleared successfully', 'success');
            document.getElementById('clearDataPackage').value = '';
        } else {
            showToast('Failed to clear app data: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error clearing app data:', error);
        showToast('Error clearing app data: ' + error.message, 'error');
    }
}

// ==================== SYSTEM DIAGNOSTICS ====================

async function viewLogcat() {
    try {
        const response = await api.get('/api/diagnostics/logcat?lines=200');
        
        if (response.success && response.logs) {
            document.getElementById('logcatContent').textContent = response.logs;
            const modal = new bootstrap.Modal(document.getElementById('logcatModal'));
            modal.show();
        } else {
            showToast('Failed to get logs: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error viewing logcat:', error);
        showToast('Error viewing logcat: ' + error.message, 'error');
    }
}

async function clearLogs() {
    if (!confirm('Clear all device logs?')) {
        return;
    }
    
    try {
        const response = await api.post('/api/diagnostics/clear-logs', {});
        
        if (response.success) {
            showToast('Logs cleared successfully', 'success');
        } else {
            showToast('Failed to clear logs: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error clearing logs:', error);
        showToast('Error clearing logs: ' + error.message, 'error');
    }
}

async function listProcesses() {
    try {
        const response = await api.get('/api/diagnostics/processes');
        
        if (response.success && response.processes) {
            displayProcesses(response.processes);
        } else {
            showToast('Failed to list processes: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error listing processes:', error);
        showToast('Error listing processes: ' + error.message, 'error');
    }
}

function displayProcesses(processes) {
    const listDiv = document.getElementById('processesList');
    
    listDiv.innerHTML = `
        <div class="alert alert-info">
            <strong>Total Processes:</strong> ${processes.length}
        </div>
        <div class="table-responsive">
            <table class="table table-striped table-sm">
                <thead>
                    <tr>
                        <th>PID</th>
                        <th>User</th>
                        <th>Name</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${processes.slice(0, 50).map(proc => `
                        <tr>
                            <td>${proc.pid}</td>
                            <td>${proc.user}</td>
                            <td><small>${proc.name}</small></td>
                            <td>
                                <button class="btn btn-sm btn-danger" onclick="killProcess('${proc.pid}')">
                                    <i class="bi bi-x"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        ${processes.length > 50 ? `<p class="text-muted">Showing first 50 of ${processes.length} processes</p>` : ''}
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('processesModal'));
    modal.show();
}

async function killProcess(pid) {
    if (!confirm(`Kill process ${pid}?`)) {
        return;
    }
    
    try {
        const response = await api.post('/api/diagnostics/kill-process', {
            pid: pid
        });
        
        if (response.success) {
            showToast('Process killed', 'success');
            listProcesses(); // Refresh list
        } else {
            showToast('Failed to kill process: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error killing process:', error);
        showToast('Error killing process: ' + error.message, 'error');
    }
}

// ==================== WIRELESS ADB ====================

async function getWirelessStatus() {
    try {
        const response = await api.get('/api/wireless/status');
        
        if (response.success) {
            const statusDiv = document.getElementById('wirelessStatus');
            if (response.mode === 'Wireless') {
                statusDiv.innerHTML = `
                    <div class="alert alert-success">
                        <strong>Status:</strong> Wireless ADB Enabled<br>
                        <strong>Port:</strong> ${response.port}
                    </div>
                `;
            } else {
                statusDiv.innerHTML = `
                    <div class="alert alert-info">
                        <strong>Status:</strong> USB Only
                    </div>
                `;
            }
        } else {
            showToast('Failed to get wireless status: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error getting wireless status:', error);
        showToast('Error getting wireless status: ' + error.message, 'error');
    }
}

async function enableWireless() {
    const port = document.getElementById('wirelessPort').value;
    
    try {
        const response = await api.post('/api/wireless/enable', {
            port: parseInt(port)
        });
        
        if (response.success) {
            showToast(response.message, 'success');
            getWirelessStatus();
        } else {
            showToast('Failed to enable wireless: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error enabling wireless:', error);
        showToast('Error enabling wireless: ' + error.message, 'error');
    }
}

async function disableWireless() {
    if (!confirm('Disable wireless ADB? You will need USB connection to reconnect.')) {
        return;
    }
    
    try {
        const response = await api.post('/api/wireless/disable', {});
        
        if (response.success) {
            showToast('Wireless ADB disabled', 'success');
            getWirelessStatus();
        } else {
            showToast('Failed to disable wireless: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error disabling wireless:', error);
        showToast('Error disabling wireless: ' + error.message, 'error');
    }
}

// ==================== IME MANAGER ====================

async function listIMEs() {
    try {
        const response = await api.get('/api/ime/list');
        
        if (response.success && response.imes) {
            displayIMEs(response.imes);
        } else {
            showToast('Failed to list IMEs: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error listing IMEs:', error);
        showToast('Error listing IMEs: ' + error.message, 'error');
    }
}

function displayIMEs(imes) {
    const listDiv = document.getElementById('imeList');
    
    listDiv.innerHTML = `
        <div class="alert alert-info">
            <strong>Total Input Methods:</strong> ${imes.length}
        </div>
        <div class="list-group">
            ${imes.map(ime => `
                <div class="list-group-item">
                    <small>${ime}</small>
                    <button class="btn btn-sm btn-primary float-end" onclick="setIMEById('${ime}')">
                        Set as Default
                    </button>
                </div>
            `).join('')}
        </div>
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('imeModal'));
    modal.show();
}

async function getCurrentIME() {
    try {
        const response = await api.get('/api/ime/current');
        
        if (response.success && response.ime) {
            showToast(`Current IME: ${response.ime}`, 'info');
            document.getElementById('imeId').value = response.ime;
        } else {
            showToast('Failed to get current IME: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error getting current IME:', error);
        showToast('Error getting current IME: ' + error.message, 'error');
    }
}

async function setIME() {
    const imeId = document.getElementById('imeId').value;
    
    if (!imeId) {
        showToast('Please enter an IME ID', 'warning');
        return;
    }
    
    await setIMEById(imeId);
}

async function setIMEById(imeId) {
    try {
        const response = await api.post('/api/ime/set', {
            ime_id: imeId
        });
        
        if (response.success) {
            showToast('IME set successfully', 'success');
        } else {
            showToast('Failed to set IME: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error setting IME:', error);
        showToast('Error setting IME: ' + error.message, 'error');
    }
}

async function enableIME() {
    const imeId = document.getElementById('imeId').value;
    
    if (!imeId) {
        showToast('Please enter an IME ID', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/ime/enable', {
            ime_id: imeId
        });
        
        if (response.success) {
            showToast('IME enabled successfully', 'success');
        } else {
            showToast('Failed to enable IME: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error enabling IME:', error);
        showToast('Error enabling IME: ' + error.message, 'error');
    }
}

async function disableIME() {
    const imeId = document.getElementById('imeId').value;
    
    if (!imeId) {
        showToast('Please enter an IME ID', 'warning');
        return;
    }
    
    try {
        const response = await api.post('/api/ime/disable', {
            ime_id: imeId
        });
        
        if (response.success) {
            showToast('IME disabled successfully', 'success');
        } else {
            showToast('Failed to disable IME: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error disabling IME:', error);
        showToast('Error disabling IME: ' + error.message, 'error');
    }
}
