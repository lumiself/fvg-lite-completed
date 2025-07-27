class ApiService {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async getMarketOverview() {
        try {
            const data = await this.request('/api/market/overview');
            return data;
        } catch (error) {
            console.error('Failed to fetch market overview:', error);
            return {
                volatility: 0,
                activePairs: 0,
                signalStrength: 0
            };
        }
    }

    async getSignalHistory(limit = 50) {
        try {
            const data = await this.request(`/api/signals/history?limit=${limit}`);
            return data.signals || [];
        } catch (error) {
            console.error('Failed to fetch signal history:', error);
            return [];
        }
    }

    async getSystemStatus() {
        try {
            const data = await this.request('/api/system/status');
            return data;
        } catch (error) {
            console.error('Failed to fetch system status:', error);
            return {
                status: 'error',
                message: 'Unable to connect to backend'
            };
        }
    }

    async getTradingPairs() {
        try {
            const data = await this.request('/api/market/pairs');
            return data.pairs || [];
        } catch (error) {
            console.error('Failed to fetch trading pairs:', error);
            return [];
        }
    }

    async getMarketData(symbol) {
        try {
            const data = await this.request(`/api/market/data/${symbol}`);
            return data;
        } catch (error) {
            console.error('Failed to fetch market data:', error);
            return null;
        }
    }
}

// Create global instance
window.apiService = new ApiService();
