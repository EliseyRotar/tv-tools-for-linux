class App {
    constructor() {
        this.currentDevice = null;
        this.metricsInterval = null;
    }
    
    async init() {
        console.log('Initializing TV Tools for Linux Web UI...');
        
        await this.checkCurrentDevice();
        
        this.setupEventListeners();
    }
    
    async checkCurrentDevice() {
        try {
            const result = await api.getCurrentDevice();
            if (result.success && result.device) {
                this.currentDevice = result.device;
                updateDeviceStatus(true, result.device);
                console.log('Connected to device:', result.device);
            }
        } catch (error) {
            console.log('No device currently connected');
            updateDeviceStatus(false);
        }
    }
    
    setupEventListeners() {
        console.log('Event listeners setup complete');
    }
    
    startMetricsPolling(interval = 2000) {
        if (this.metricsInterval) {
            clearInterval(this.metricsInterval);
        }
        
        this.metricsInterval = setInterval(async () => {
            try {
                const result = await api.getMetrics();
                if (result.success) {
                    this.updateMetricsDisplay(result.metrics);
                }
            } catch (error) {
                console.error('Failed to fetch metrics:', error);
            }
        }, interval);
    }
    
    stopMetricsPolling() {
        if (this.metricsInterval) {
            clearInterval(this.metricsInterval);
            this.metricsInterval = null;
        }
    }
    
    updateMetricsDisplay(metrics) {
        console.log('Metrics updated:', metrics);
    }
}

const app = new App();

document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
