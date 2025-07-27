class TradePanel {
    constructor() {
        this.container = null;
        this.currentSignal = null;
        this.accountBalance = 0;
        this.tradingConfig = {};
        this.init();
    }

    init() {
        this.createPanel();
        this.setupEventListeners();
        this.loadTradingData();
    }

    createPanel() {
        const panelHTML = `
            <div id="trade-panel" class="trade-panel" style="display: none;">
                <div class="trade-panel-header">
                    <h3>Quick Trade</h3>
                    <button class="close-btn" onclick="window.tradePanel.hide()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="trade-panel-content">
                    <div class="signal-preview">
                        <h4>Signal Details</h4>
                        <div id="trade-signal-details"></div>
                    </div>
                    
                    <div class="trade-form">
                        <div class="form-group">
                            <label>Account Balance</label>
                            <div class="balance-display">
                                $<span id="trade-balance">0.00</span>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="trade-amount">Trade Amount ($)</label>
                            <input type="number" id="trade-amount" min="1" max="10000" value="100" step="1">
                        </div>
                        
                        <div class="form-group">
                            <label for="trade-duration">Duration</label>
                            <select id="trade-duration">
                                <option value="1">1 minute</option>
                                <option value="5" selected>5 minutes</option>
                                <option value="15">15 minutes</option>
                                <option value="30">30 minutes</option>
                                <option value="60">1 hour</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Risk Management</label>
                            <div class="risk-info">
                                <span>Max Risk: <span id="max-risk">$2.00</span> (2%)</span>
                            </div>
                        </div>
                        
                        <div class="trade-actions">
                            <button id="execute-trade-btn" class="btn btn-success">
                                <i class="fas fa-play"></i>
                                Execute Trade
                            </button>
                            <button id="cancel-trade-btn" class="btn btn-secondary">
                                <i class="fas fa-times"></i>
                                Cancel
                            </button>
                        </div>
                        
                        <div id="trade-status" class="trade-status"></div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', panelHTML);
        this.container = document.getElementById('trade-panel');
    }

    setupEventListeners() {
        // Execute trade
        const executeBtn = document.getElementById('execute-trade-btn');
        executeBtn.addEventListener('click', () => this.executeTrade());

        // Cancel trade
        const cancelBtn = document.getElementById('cancel-trade-btn');
        cancelBtn.addEventListener('click', () => this.hide());

        // Amount change
        const amountInput = document.getElementById('trade-amount');
        amountInput.addEventListener('input', () => this.updateRiskInfo());
    }

    async loadTradingData() {
        try {
            const [balanceResult, configResult] = await Promise.all([
                window.tradingService.getAccountBalance(),
                window.tradingService.getTradingConfig()
            ]);

            if (balanceResult.success) {
                this.accountBalance = balanceResult.balance.balance;
                document.getElementById('trade-balance').textContent = 
                    this.accountBalance.toFixed(2);
            }

            if (configResult.success) {
                this.tradingConfig = configResult.config;
            }
        } catch (error) {
            console.error('Failed to load trading data:', error);
        }
    }

    show(signal) {
        if (!window.authService.isLoggedIn()) {
            window.authModal.show();
            return;
        }

        this.currentSignal = signal;
        this.renderSignalDetails(signal);
        this.updateRiskInfo();
        this.container.style.display = 'block';
    }

    hide() {
        this.container.style.display = 'none';
        this.currentSignal = null;
        this.clearStatus();
    }

    renderSignalDetails(signal) {
        const detailsContainer = document.getElementById('trade-signal-details');
        detailsContainer.innerHTML = `
            <div class="signal-detail">
                <span>Symbol:</span>
                <span>${signal.symbol}</span>
            </div>
            <div class="signal-detail">
                <span>Type:</span>
                <span class="${signal.type.toLowerCase()}">${signal.type}</span>
            </div>
            <div class="signal-detail">
                <span>Price:</span>
                <span>${window.formatters.formatPrice(signal.price)}</span>
            </div>
            <div class="signal-detail">
                <span>Confidence:</span>
                <span>${signal.confidence}%</span>
            </div>
            ${signal.stop_loss ? `
            <div class="signal-detail">
                <span>Stop Loss:</span>
                <span>${window.formatters.formatPrice(signal.stop_loss)}</span>
            </div>
            ` : ''}
            ${signal.take_profit ? `
            <div class="signal-detail">
                <span>Take Profit:</span>
                <span>${window.formatters.formatPrice(signal.take_profit)}</span>
            </div>
            ` : ''}
        `;
    }

    updateRiskInfo() {
        const amount = parseFloat(document.getElementById('trade-amount').value) || 0;
        const maxRisk = amount * 0.02; // 2% risk
        document.getElementById('max-risk').textContent = `$${maxRisk.toFixed(2)}`;
    }

    async executeTrade() {
        if (!this.currentSignal) return;

        const amount = parseFloat(document.getElementById('trade-amount').value);
        const duration = parseInt(document.getElementById('trade-duration').value);

        if (!amount || amount <= 0) {
            this.showStatus('Please enter a valid amount', 'error');
            return;
        }

        if (amount > this.accountBalance) {
            this.showStatus('Insufficient balance', 'error');
            return;
        }

        // Validate signal
        const validation = await window.tradingService.validateTradeSignal(this.currentSignal);
        if (!validation.isValid) {
            this.showStatus(validation.errors.join(', '), 'error');
            return;
        }

        // Show loading
        this.showStatus('Executing trade...', 'info');
        document.getElementById('execute-trade-btn').disabled = true;

        const tradeParams = {
            amount,
            duration,
            durationUnit: 'm'
        };

        const result = await window.tradingService.executeTrade(this.currentSignal, tradeParams);

        if (result.success) {
            this.showStatus('Trade executed successfully!', 'success');
            
            // Update balance
            await this.loadTradingData();
            
            // Close panel after delay
            setTimeout(() => {
                this.hide();
            }, 2000);
        } else {
            this.showStatus(`Trade failed: ${result.error}`, 'error');
        }

        document.getElementById('execute-trade-btn').disabled = false;
    }

    showStatus(message, type) {
        const statusEl = document.getElementById('trade-status');
        statusEl.textContent = message;
        statusEl.className = `trade-status ${type}`;
        statusEl.style.display = 'block';
    }

    clearStatus() {
        const statusEl = document.getElementById('trade-status');
        statusEl.style.display = 'none';
        statusEl.textContent = '';
    }
}

// Create global instance
window.tradePanel = new TradePanel();
