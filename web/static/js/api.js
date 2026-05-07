class APIClient {
    constructor() {
        this.baseURL = '';
    }
    
    getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.content : '';
    }
    
    async request(method, endpoint, data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        const csrfToken = this.getCsrfToken();
        if (csrfToken) {
            options.headers['X-CSRF-Token'] = csrfToken;
        }
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(this.baseURL + endpoint, options);
            
            // Try to parse JSON response
            let result;
            try {
                result = await response.json();
            } catch (jsonError) {
                // If JSON parsing fails, throw a more specific error
                throw new APIError(
                    'INVALID_RESPONSE',
                    `Server returned invalid JSON response (Status: ${response.status})`,
                    response.status
                );
            }
            
            if (!response.ok) {
                throw new APIError(
                    result.error || 'Request failed',
                    result.message || 'An error occurred',
                    response.status
                );
            }
            
            return result;
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            
            // More specific error messages
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new APIError(
                    'NETWORK_ERROR',
                    'Cannot connect to server. Please ensure the web server is running.',
                    0
                );
            }
            
            throw new APIError(
                'NETWORK_ERROR',
                'Network request failed: ' + error.message,
                0
            );
        }
    }
    
    async get(endpoint) {
        return this.request('GET', endpoint);
    }
    
    async post(endpoint, data) {
        return this.request('POST', endpoint, data);
    }
    
    async put(endpoint, data) {
        return this.request('PUT', endpoint, data);
    }
    
    async delete(endpoint) {
        return this.request('DELETE', endpoint);
    }
    
    async connectDevice(ipAddress, port = 5555) {
        return this.post('/api/devices/connect', { ip_address: ipAddress, port: port });
    }
    
    async disconnectDevice() {
        return this.post('/api/devices/disconnect');
    }
    
    async getCurrentDevice() {
        return this.get('/api/devices/current');
    }
    
    async getMetrics() {
        return this.get('/api/monitor/metrics');
    }
    
    async getDeviceInfo() {
        return this.get('/api/device/info');
    }
}

class APIError extends Error {
    constructor(code, message, status) {
        super(message);
        this.name = 'APIError';
        this.code = code;
        this.status = status;
    }
}

const api = new APIClient();
