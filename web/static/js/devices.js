// Multi-Device Management JavaScript

let devices = [];

document.addEventListener('DOMContentLoaded', function() {
    loadDevices();
    
    document.getElementById('addDeviceForm').addEventListener('submit', handleAddDevice);
});

async function loadDevices() {
    try {
        document.getElementById('loadingDevices').style.display = 'block';
        document.getElementById('devicesContainer').style.display = 'none';
        document.getElementById('noDevices').style.display = 'none';
        
        const response = await api.get('/api/devices/list');
        
        if (response.success) {
            devices = response.devices;
            displayDevices();
        }
    } catch (error) {
        console.error('Error loading devices:', error);
        showToast('Error loading devices: ' + error.message, 'error');
    } finally {
        document.getElementById('loadingDevices').style.display = 'none';
    }
}

function displayDevices() {
    const container = document.getElementById('devicesList');
    
    if (devices.length === 0) {
        document.getElementById('devicesContainer').style.display = 'none';
        document.getElementById('noDevices').style.display = 'block';
        return;
    }
    
    document.getElementById('devicesContainer').style.display = 'block';
    document.getElementById('noDevices').style.display = 'none';
    
    container.innerHTML = '';
    
    devices.forEach(device => {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-3';
        
        const currentBadge = device.is_current ? 
            '<span class="badge bg-success">Current</span>' : '';
        
        col.innerHTML = `
            <div class="card ${device.is_current ? 'border-success' : ''}">
                <div class="card-body">
                    <h5 class="card-title">
                        ${escapeHtml(device.manufacturer)} ${escapeHtml(device.model)}
                        ${currentBadge}
                    </h5>
                    <p class="card-text">
                        <small class="text-muted">
                            <i class="bi bi-hdd"></i> ${escapeHtml(device.device_id)}<br>
                            <i class="bi bi-android2"></i> Android ${escapeHtml(device.android_version)}<br>
                            <i class="bi bi-clock"></i> Connected: ${formatDate(device.connected_at)}
                        </small>
                    </p>
                    <div class="btn-group w-100" role="group">
                        ${!device.is_current ? 
                            `<button class="btn btn-sm btn-primary" onclick="switchDevice('${device.device_id}')">
                                <i class="bi bi-arrow-repeat"></i> Switch
                            </button>` : 
                            '<button class="btn btn-sm btn-success" disabled><i class="bi bi-check-circle"></i> Active</button>'
                        }
                        <button class="btn btn-sm btn-danger" onclick="removeDevice('${device.device_id}')">
                            <i class="bi bi-trash"></i> Remove
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(col);
    });
}

async function handleAddDevice(e) {
    e.preventDefault();
    
    const ipAddress = document.getElementById('newIpAddress').value;
    const port = document.getElementById('newPort').value || 5555;
    
    try {
        const response = await api.post('/api/devices/connect', {
            ip_address: ipAddress,
            port: parseInt(port)
        });
        
        if (response.success) {
            showToast('Device added successfully', 'success');
            document.getElementById('addDeviceForm').reset();
            await loadDevices();
        } else {
            showToast('Failed to add device: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error adding device:', error);
        showToast('Error adding device: ' + error.message, 'error');
    }
}

async function switchDevice(deviceId) {
    try {
        const response = await api.post('/api/devices/switch', {
            device_id: deviceId
        });
        
        if (response.success) {
            showToast('Switched to device successfully', 'success');
            await loadDevices();
            updateDeviceStatus(true, response.device);
        } else {
            showToast('Failed to switch device: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error switching device:', error);
        showToast('Error switching device: ' + error.message, 'error');
    }
}

async function removeDevice(deviceId) {
    if (!confirm('Are you sure you want to remove this device?')) {
        return;
    }
    
    try {
        const response = await api.post('/api/devices/remove', {
            device_id: deviceId
        });
        
        if (response.success) {
            showToast('Device removed successfully', 'success');
            await loadDevices();
        } else {
            showToast('Failed to remove device: ' + response.error, 'error');
        }
    } catch (error) {
        console.error('Error removing device:', error);
        showToast('Error removing device: ' + error.message, 'error');
    }
}

function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
