export class ApiService {
    constructor(baseUrl) {
        // Use the /api proxy path instead of direct localhost:8000
        this.baseUrl = '/api';
    }
    
    async getInfo() {
        return this.fetchJSON('/');
    }
    
    async getHealth() {
        return this.fetchJSON('/health');
    }
    
    async getStatistics() {
        return this.fetchJSON('/statistics');
    }
    
    async matchAddress(addressData) {
        return this.fetchJSON('/match_address', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(addressData)
        });
    }
    
    async fetchJSON(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, options);
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
}
