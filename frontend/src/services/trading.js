class TradingService {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }

    async executeTrade(signal, tradeParams = {}) {
        try {
            const headers = {
                'Content-Type': 'application/json',
                ...window.authService.getAuthHeaders()
            };

            const tradeRequest = {
                symbol: signal.symbol,
                action: signal.type.toLowerCase(),
                amount: tradeParams.amount || 100,
                contract_type: tradeParams.contractType || 'CALL',
                duration: tradeParams.duration || 5,
                duration_unit: tradeParams.durationUnit || 'm',
                barrier: signal.price,
                basis: tradeParams.basis || 'stake',
                currency: tradeParams.currency || 'USD'
            };

            const response = await fetch(`${this.baseURL}/api/trading/execute`, {
                method: 'POST',
                headers,
                body: JSON.stringify(tradeRequest)
            });

            if (!response.ok) {
                throw new Error(`Trade execution failed: ${response.status}`);
            }

            const result = await response.json();
            return { success: true, trade: result };
        } catch (error) {
            console.error('Trade execution error:', error);
            return { success: false, error: error.message };
        }
    }

    async getAccountBalance() {
        try {
            const headers = {
                ...window.authService.getAuthHeaders()
            };

            const response = await fetch(`${this.baseURL}/api/trading/balance`, {
                headers
            });

            if (!response.ok) {
                throw new Error('Failed to get balance');
            }

            const data = await response.json();
            return { success: true, balance: data.balance };
        } catch (error) {
            console.error('Balance fetch error:', error);
            return { success: false, error: error.message };
        }
    }

    async getOpenPositions() {
        try {
            const headers = {
                ...window.authService.getAuthHeaders()
            };

            const response = await fetch(`${this.baseURL}/api/trading/positions`, {
                headers
            });

            if (!response.ok) {
                throw new Error('Failed to get positions');
            }

            const data = await response.json();
            return { success: true, positions: data.positions || [] };
        } catch (error) {
            console.error('Positions fetch error:', error);
            return { success: false, error: error.message };
        }
    }

    async closePosition(contractId) {
        try {
            const headers = {
                'Content-Type': 'application/json',
                ...window.authService.getAuthHeaders()
            };

            const response = await fetch(`${this.baseURL}/api/trading/positions/${contractId}/close`, {
                method: 'POST',
                headers
            });

            if (!response.ok) {
                throw new Error('Failed to close position');
            }

            const result = await response.json();
            return { success: true, result };
        } catch (error) {
            console.error('Position close error:', error);
            return { success: false, error: error.message };
        }
    }

    async getTradeHistory(limit = 50) {
        try {
            const headers = {
                ...window.authService.getAuthHeaders()
            };

            const response = await fetch(`${this.baseURL}/api/trading/history?limit=${limit}`, {
                headers
            });

            if (!response.ok) {
                throw new Error('Failed to get trade history');
            }

            const data = await response.json();
            return { success: true, trades: data.trades || [] };
        } catch (error) {
            console.error('Trade history error:', error);
            return { success: false, error: error.message };
        }
    }

    async validateTradeSignal(signal) {
        // Validate if signal is suitable for trading
        const validation = {
            isValid: true,
            warnings: [],
            errors: []
        };

        if (!signal || !signal.symbol || !signal.type) {
            validation.isValid = false;
            validation.errors.push('Invalid signal format');
            return validation;
        }

        if (signal.confidence < 60) {
            validation.warnings.push('Low confidence signal');
        }

        if (!['BUY', 'SELL'].includes(signal.type.toUpperCase())) {
            validation.isValid = false;
            validation.errors.push('Invalid signal type for trading');
        }

        return validation;
    }

    calculatePositionSize(balance, riskPercentage = 2) {
        // Calculate position size based on risk management
        const maxRiskAmount = balance * (riskPercentage / 100);
        return Math.max(1, Math.floor(maxRiskAmount));
    }

    async getTradingConfig() {
        try {
            const headers = {
                ...window.authService.getAuthHeaders()
            };

            const response = await fetch(`${this.baseURL}/api/trading/config`, {
                headers
            });

            if (!response.ok) {
                throw new Error('Failed to get trading config');
            }

            const data = await response.json();
            return { success: true, config: data };
        } catch (error) {
            console.error('Trading config error:', error);
            return { success: false, error: error.message };
        }
    }
}

// Create global instance
window.tradingService = new TradingService();
