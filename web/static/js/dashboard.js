class Dashboard {
    constructor() {
        this.connected = false;
        this.metricsInterval = null;
        this.charts = {};
    }
    
    init() {
        this.setupEventListeners();
        this.initCharts();
        this.checkConnection();
    }
    
    setupEventListeners() {
        const connectForm = document.getElementById('connectForm');
        if (connectForm) {
            connectForm.addEventListener('submit', (e) => this.handleConnect(e));
        }
        
        const scanBtn = document.getElementById('scanBtn');
        if (scanBtn) {
            scanBtn.addEventListener('click', () => this.handleScan());
        }
    }
    
    async checkConnection() {
        try {
            const result = await api.getCurrentDevice();
            if (result.success && result.device) {
                this.onDeviceConnected(result.device);
            }
        } catch (error) {
            console.log('No device connected');
        }
    }
    
    async handleConnect(e) {
        e.preventDefault();
        
        const ipAddress = document.getElementById('ipAddress').value;
        const port = document.getElementById('port').value || 5555;
        const connectBtn = document.getElementById('connectBtn');
        
        connectBtn.disabled = true;
        connectBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Connecting...';
        
        try {
            const result = await api.connectDevice(ipAddress, port);
            
            if (result.success) {
                showToast('Connected successfully!', 'success');
                this.onDeviceConnected(result.device);
            }
        } catch (error) {
            showToast(error.message || 'Connection failed', 'error');
        } finally {
            connectBtn.disabled = false;
            connectBtn.innerHTML = '<i class="bi bi-plug"></i> Connect';
        }
    }
    
    async handleScan() {
        try {
            showToast('Scanning network for devices...', 'info');
            
            const response = await api.post('/api/network/scan', {});
            
            if (response.success && response.devices) {
                if (response.devices.length === 0) {
                    showToast('No devices found on network', 'warning');
                } else {
                    showToast(`Found ${response.devices.length} device(s)`, 'success');
                    
                    // Display devices in a modal or list
                    displayScannedDevices(response.devices);
                }
            } else {
                showToast('Network scan failed: ' + (response.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Network scan error:', error);
            showToast('Error scanning network: ' + error.message, 'error');
        }
    }
    
    onDeviceConnected(device) {
        this.connected = true;
        updateDeviceStatus(true, device);
        
        const deviceInfo = document.getElementById('deviceInfo');
        if (deviceInfo) {
            deviceInfo.innerHTML = `
                <dl class="row mb-0">
                    <dt class="col-sm-4">Manufacturer:</dt>
                    <dd class="col-sm-8">${device.manufacturer}</dd>
                    
                    <dt class="col-sm-4">Model:</dt>
                    <dd class="col-sm-8">${device.model}</dd>
                    
                    <dt class="col-sm-4">Android:</dt>
                    <dd class="col-sm-8">${device.android_version}</dd>
                    
                    <dt class="col-sm-4">IP Address:</dt>
                    <dd class="col-sm-8">${device.ip_address}:${device.port}</dd>
                </dl>
                <button class="btn btn-sm btn-danger mt-2" id="disconnectBtn">
                    <i class="bi bi-plug"></i> Disconnect
                </button>
            `;
            
            const disconnectBtn = document.getElementById('disconnectBtn');
            if (disconnectBtn) {
                disconnectBtn.addEventListener('click', () => this.handleDisconnect());
            }
        }
        
        document.getElementById('metricsSection').style.display = 'flex';
        document.getElementById('processesSection').style.display = 'block';
        
        this.startMetricsPolling();
    }
    
    async handleDisconnect() {
        try {
            await api.disconnectDevice();
            showToast('Disconnected', 'info');
            this.onDeviceDisconnected();
        } catch (error) {
            showToast('Disconnect failed', 'error');
        }
    }
    
    onDeviceDisconnected() {
        this.connected = false;
        updateDeviceStatus(false);
        
        const deviceInfo = document.getElementById('deviceInfo');
        if (deviceInfo) {
            deviceInfo.innerHTML = '<p class="text-muted">No device connected</p>';
        }
        
        document.getElementById('metricsSection').style.display = 'none';
        document.getElementById('processesSection').style.display = 'none';
        
        this.stopMetricsPolling();
    }
    
    startMetricsPolling() {
        if (this.metricsInterval) {
            clearInterval(this.metricsInterval);
        }
        
        this.fetchMetrics();
        this.fetchHistory();
        
        this.metricsInterval = setInterval(() => {
            this.fetchMetrics();
            this.fetchHistory();
        }, 2000);
    }
    
    stopMetricsPolling() {
        if (this.metricsInterval) {
            clearInterval(this.metricsInterval);
            this.metricsInterval = null;
        }
    }
    
    async fetchMetrics() {
        try {
            const result = await api.getMetrics();
            
            if (result.success) {
                this.updateMetrics(result.metrics);
            }
        } catch (error) {
            console.error('Failed to fetch metrics:', error);
            if (error.status === 400) {
                this.onDeviceDisconnected();
            }
        }
    }
    
    updateMetrics(metrics) {
        if (metrics.cpu && metrics.cpu.usage) {
            document.getElementById('cpuUsage').textContent = metrics.cpu.usage;
        }
        
        if (metrics.memory) {
            const mem = metrics.memory;
            if (mem.used_percent) {
                document.getElementById('memoryUsage').textContent = mem.used_percent + '%';
            }
            if (mem.used && mem.total) {
                const usedMB = (parseInt(mem.used) / 1024).toFixed(0);
                const totalMB = (parseInt(mem.total) / 1024).toFixed(0);
                document.getElementById('memoryDetails').textContent = `${usedMB} / ${totalMB} MB`;
            }
        }
        
        if (metrics.storage && metrics.storage.length > 0) {
            // Prefer /data, then /sdcard, then first non-tmpfs partition
            const preferred = ['/data', '/sdcard', '/storage/emulated/0', '/'];
            let partition = null;
            for (const mount of preferred) {
                partition = metrics.storage.find(s => s.mounted === mount);
                if (partition) break;
            }
            // Fallback: first non-tmpfs with actual size
            if (!partition) {
                partition = metrics.storage.find(s => 
                    s.filesystem !== 'tmpfs' && s.size !== '0' && s.size !== '0B'
                );
            }
            if (partition) {
                document.getElementById('storageUsage').textContent = partition.use_percent;
                document.getElementById('storageDetails').textContent = 
                    `${partition.used} / ${partition.size}`;
            }
        }
        
        if (metrics.battery && Object.keys(metrics.battery).length > 0) {
            const battery = metrics.battery;
            // Show battery card and chart
            const batteryCard = document.getElementById('batteryCard');
            const batteryChartCol = document.getElementById('batteryChartCol');
            if (batteryCard) batteryCard.style.display = '';
            if (batteryChartCol) batteryChartCol.style.display = '';
            
            if (battery.level) {
                document.getElementById('batteryLevel').textContent = battery.level + '%';
            }
            if (battery.status) {
                document.getElementById('batteryStatus').textContent = battery.status;
            }
        } else {
            // Hide battery card and chart - device has no battery (TV, stick, etc.)
            const batteryCard = document.getElementById('batteryCard');
            const batteryChartCol = document.getElementById('batteryChartCol');
            if (batteryCard) batteryCard.style.display = 'none';
            if (batteryChartCol) batteryChartCol.style.display = 'none';
        }
        
        if (metrics.processes && metrics.processes.length > 0) {
            this.updateProcessesTable(metrics.processes);
        }
    }
    
    updateProcessesTable(processes) {
        const tbody = document.getElementById('processesTable');
        if (!tbody) return;
        
        tbody.innerHTML = processes.map(proc => `
            <tr>
                <td>${proc.pid}</td>
                <td><small>${proc.name}</small></td>
                <td>${proc.cpu}</td>
                <td>${proc.mem}</td>
            </tr>
        `).join('');
    }
    
    initCharts() {
        const chartConfig = (label, color) => ({
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: label,
                    data: [],
                    borderColor: color,
                    backgroundColor: color + '20',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    },
                    x: {
                        display: false
                    }
                }
            }
        });
        
        const cpuCanvas = document.getElementById('cpuChart');
        const memoryCanvas = document.getElementById('memoryChart');
        const storageCanvas = document.getElementById('storageChart');
        const batteryCanvas = document.getElementById('batteryChart');
        
        if (cpuCanvas) {
            this.charts.cpu = new Chart(cpuCanvas, chartConfig('CPU Usage (%)', '#0d6efd'));
        }
        
        if (memoryCanvas) {
            this.charts.memory = new Chart(memoryCanvas, chartConfig('Memory Usage (%)', '#198754'));
        }
        
        if (storageCanvas) {
            this.charts.storage = new Chart(storageCanvas, chartConfig('Storage Usage (%)', '#ffc107'));
        }
        
        if (batteryCanvas) {
            this.charts.battery = new Chart(batteryCanvas, chartConfig('Battery Level (%)', '#0dcaf0'));
        }
    }
    
    async fetchHistory() {
        try {
            const response = await api.get('/api/monitor/history');
            
            if (response.success && response.history) {
                this.updateCharts(response.history);
            }
        } catch (error) {
            console.error('Failed to fetch history:', error);
        }
    }
    
    updateCharts(history) {
        const formatTime = (timestamp) => {
            const date = new Date(timestamp);
            return date.toLocaleTimeString();
        };
        
        const labels = history.timestamps.map(formatTime);
        
        if (this.charts.cpu) {
            this.charts.cpu.data.labels = labels;
            this.charts.cpu.data.datasets[0].data = history.cpu;
            this.charts.cpu.update('none');
        }
        
        if (this.charts.memory) {
            this.charts.memory.data.labels = labels;
            this.charts.memory.data.datasets[0].data = history.memory;
            this.charts.memory.update('none');
        }
        
        if (this.charts.storage) {
            this.charts.storage.data.labels = labels;
            this.charts.storage.data.datasets[0].data = history.storage;
            this.charts.storage.update('none');
        }
        
        if (this.charts.battery) {
            this.charts.battery.data.labels = labels;
            this.charts.battery.data.datasets[0].data = history.battery;
            this.charts.battery.update('none');
        }
    }
}

const dashboard = new Dashboard();

// Display scanned devices in a list
function displayScannedDevices(devices) {
    // Check if we're on the dashboard page
    const scanResultsDiv = document.getElementById('scanResults');
    
    if (!scanResultsDiv) {
        // If no scan results div, show devices in a simple alert or modal
        const deviceList = devices.map(d => `${d.ip}:${d.port || 5555}`).join('\n');
        alert(`Found ${devices.length} device(s):\n\n${deviceList}\n\nGo to the Tools page to connect to these devices.`);
        return;
    }
    
    // Display in the scan results div
    scanResultsDiv.innerHTML = `
        <div class="alert alert-success">
            <h6>Found ${devices.length} device(s):</h6>
            <div class="list-group mt-2">
                ${devices.map(device => `
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        <span>${device.ip}:${device.port || 5555}</span>
                        <button class="btn btn-sm btn-primary" onclick="connectToDevice('${device.ip}', ${device.port || 5555})">
                            Connect
                        </button>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Connect to a scanned device
async function connectToDevice(ip, port) {
    try {
        showToast(`Connecting to ${ip}:${port}...`, 'info');
        
        // Ensure port is a number
        const portNum = parseInt(port) || 5555;
        
        const response = await api.post('/api/devices/connect', { 
            ip_address: ip, 
            port: portNum 
        });
        
        if (response.success) {
            showToast('Connected successfully!', 'success');
            // Reload the page to update device info
            setTimeout(() => location.reload(), 1000);
        } else {
            const errorMsg = response.message || response.error || 'Unknown error';
            showToast('Connection failed: ' + errorMsg, 'error');
        }
    } catch (error) {
        console.error('Connection error:', error);
        let errorMsg = 'Error connecting';
        
        if (error.message) {
            errorMsg += ': ' + error.message;
        }
        if (error.code) {
            errorMsg += ' (Code: ' + error.code + ')';
        }
        
        showToast(errorMsg, 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    dashboard.init();
});
