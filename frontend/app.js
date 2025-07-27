// Enhanced Application Controller with robust WebSocket handling
class AppController {
    constructor() {
        this.settings = this.loadSettings();
        this.isDarkTheme = false;
        this.soundEnabled = true;
        this.connectionStatus = 'disconnected';
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSettings();
        this.applyTheme();
        this.checkAuthState();
        this.setupWebSocketHandlers();
        this.connectWebSocket();
        this.loadMarketData();
        this.handleOAuthCallback();
    }

    setupEventListeners() {
        // Connect button
        const connectBtn = document.getElementById('connect-btn');
        if (connectBtn) {
            connectBtn.addEventListener('click', () => this.toggleConnection());
        }

        // Clear button
        const clearBtn = document.getElementById('clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearSignals());
        }

        // Settings modal
        const settingsBtn = document.querySelector('.action-btn[onclick="showSettings()"]');
        const settingsModal = document.getElementById('settings-modal');
        const closeBtn = document.querySelector('.close');

        if (settingsBtn && settingsModal) {
            settingsBtn.addEventListener('click', () => this.showSettings());
        }
        if (closeBtn && settingsModal) {
            closeBtn.addEventListener('click', () => this.hideSettings());
        }
        if (settingsModal) {
            settingsModal.addEventListener('click', (e) => {
                if (e.target === settingsModal) this.hideSettings();
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'k':
                        e.preventDefault();
                        this.clearSignals();
                        break;
                    case ',':
                        e.preventDefault();
                        this.showSettings();
                        break;
                }
            }
        });
    }

    setupWebSocketHandlers() {
        // Enhanced WebSocket event listeners
        window.wsService.on('connected', () => {
            this.connectionStatus = 'connected';
            this.updateConnectionButton(true);
            this.showConnectionStatus('Connected', 'success');
            this.loadInitialData();
        });

        window.wsService.on('disconnected', (event) => {
            this.connectionStatus = 'disconnected';
            this.updateConnectionButton(false);
            if (!event.wasClean) {
                this.showConnectionStatus('Disconnected - Reconnecting...', 'warning');
            }
        });

        window.wsService.on('error', (error) => {
            this.connectionStatus = 'error';
            this.updateConnectionButton(false);
            this.showConnectionStatus('Connection Error', 'error');
            console.error('WebSocket error:', error);
        });

        window.wsService.on('signal', (signal) => {
            window.signalRenderer.addSignal(signal);
            this.updateMarketData();
        });

        window.wsService.on('parseError', (error) => {
            console.error('Failed to parse WebSocket message:', error);
            this.showConnectionStatus('Message Parse Error', 'error');
        });
    }

    toggleConnection() {
        if (window.wsService.isConnected()) {
            window.wsService.disconnect();
            this.showConnectionStatus('Disconnected', 'info');
        } else {
            const wsUrl = this.settings.wsUrl || 'ws://localhost:8765';
            this.showConnectionStatus('Connecting...', 'info');
            window.wsService.connect(wsUrl);
        }
    }

    updateConnectionButton(isConnected) {
        const connectBtn = document.getElementById('connect-btn');
        if (connectBtn) {
            if (isConnected) {
                connectBtn.innerHTML = '<i class="fas fa-plug"></i> Disconnect';
                connectBtn.className = 'btn btn-secondary';
                connectBtn.disabled = false;
            } else {
                connectBtn.innerHTML = '<i class="fas fa-plug"></i> Connect';
                connectBtn.className = 'btn btn-primary';
                connectBtn.disabled = false;
            }
        }
    }

    showConnectionStatus(message, type) {
        const indicator = document.getElementById('connection-indicator');
        const statusText = document.getElementById('connection-status-text');
        
        if (indicator) {
            indicator.className = `status-${type}`;
            indicator.innerHTML = `<i class="fas fa-circle"></i> ${message}`;
        }
        
        if (statusText) {
            statusText.textContent = message;
            statusText.className = `connection-status-text ${type}`;
            
            // Auto-hide after 3 seconds for success/info messages
            if (type === 'success' || type === 'info') {
                setTimeout(() => {
                    statusText.textContent = '';
                }, 3000);
            }
        }
        
        console.log(`[Connection] ${message}`);
    }

    clearSignals() {
        window.signalRenderer.clearSignals();
    }

    async loadMarketData() {
        try {
            const marketData = await window.apiService.getMarketOverview();
            this.updateMarketDisplay(marketData);
        } catch (error) {
            console.error('Failed to load market data:', error);
            this.showConnectionStatus('Failed to load market data', 'error');
        }
    }

    updateMarketDisplay(data) {
        const volatilityEl = document.getElementById('volatility-value');
        const activePairsEl = document.getElementById('active-pairs');
        const signalStrengthEl = document.getElementById('signal-strength');

        if (volatilityEl) {
            volatilityEl.textContent = data.volatility ? `${data.volatility}%` : '--';
        }
        if (activePairsEl) {
            activePairsEl.textContent = data.activePairs || '--';
        }
        if (signalStrengthEl) {
            signalStrengthEl.textContent = data.signalStrength ? `${data.signalStrength}%` : '--';
        }
    }

    async updateMarketData() {
        // Update market data every 30 seconds
        setInterval(() => {
            this.loadMarketData();
        }, 30000);
    }

    showSettings() {
        const modal = document.getElementById('settings-modal');
        if (modal) {
            // Load current settings
            document.getElementById('sound-enabled').checked = this.settings.soundEnabled;
            document.getElementById('auto-scroll').checked = this.settings.autoScroll;
            document.getElementById('ws-url').value = this.settings.wsUrl || 'ws://localhost:8765';
            
            modal.style.display = 'block';
        }
    }

    hideSettings() {
        const modal = document.getElementById('settings-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    saveSettings() {
        const newSettings = {
            soundEnabled: document.getElementById('sound-enabled').checked,
            autoScroll: document.getElementById('auto-scroll').checked,
            wsUrl: document.getElementById('ws-url').value
        };

        // Check if WebSocket URL changed
        const urlChanged = newSettings.wsUrl !== this.settings.wsUrl;
        
        this.settings = newSettings;
        localStorage.setItem('fvg-lite-settings', JSON.stringify(this.settings));
        
        // Update signal renderer settings
        if (window.signalRenderer) {
            window.signalRenderer.updateSettings({
                autoScroll: this.settings.autoScroll,
                soundEnabled: this.settings.soundEnabled
            });
        }

        // Reconnect if URL changed
        if (urlChanged && window.wsService.isConnected()) {
            window.wsService.disconnect();
            setTimeout(() => {
                this.connectWebSocket();
            }, 100);
        }

        this.hideSettings();
    }

    loadSettings() {
        const saved = localStorage.getItem('fvg-lite-settings');
        const defaults = {
            soundEnabled: true,
            autoScroll: true,
            wsUrl: 'ws://localhost:8765'
        };

        try {
            return saved ? { ...defaults, ...JSON.parse(saved) } : defaults;
        } catch {
            return defaults;
        }
    }

    connectWebSocket() {
        const wsUrl = this.settings.wsUrl || 'ws://localhost:8765';
        console.log(`[App] Connecting to WebSocket: ${wsUrl}`);
        window.wsService.connect(wsUrl);
    }

    async loadInitialData() {
        try {
            // Only load data if connected
            if (window.wsService.isConnected()) {
                // Load historical signals
                const history = await window.apiService.getSignalHistory(20);
                if (window.signalRenderer) {
                    window.signalRenderer.renderSignals(history);
                }
                
                // Load market data
                await this.loadMarketData();
            } else {
                console.log('[App] Skipping initial data load - WebSocket not connected');
            }
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showConnectionStatus('Failed to load initial data', 'error');
        }
    }

    toggleSound() {
        this.settings.soundEnabled = !this.settings.soundEnabled;
        if (window.signalRenderer) {
            window.signalRenderer.updateSettings({ soundEnabled: this.settings.soundEnabled });
        }
        this.saveSettings();
        
        // Update button appearance
        const btn = event.target.closest('.action-btn');
        if (btn) {
            const icon = btn.querySelector('i');
            if (this.settings.soundEnabled) {
                icon.className = 'fas fa-volume-up';
            } else {
                icon.className = 'fas fa-volume-mute';
            }
        }
    }

    toggleTheme() {
        this.isDarkTheme = !this.isDarkTheme;
        this.applyTheme();
        
        // Update button appearance
        const btn = event.target.closest('.action-btn');
        if (btn) {
            const icon = btn.querySelector('i');
            const span = btn.querySelector('span');
            if (this.isDarkTheme) {
                icon.className = 'fas fa-sun';
                span.textContent = 'Light';
            } else {
                icon.className = 'fas fa-moon';
                span.textContent = 'Dark';
            }
        }
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.isDarkTheme ? 'dark' : 'light');
        localStorage.setItem('fvg-lite-theme', this.isDarkTheme ? 'dark' : 'light');
    }

    exportSignals() {
        if (window.signalRenderer) {
            window.signalRenderer.exportSignals();
        }
    }

    checkAuthState() {
        const user = window.authService ? window.authService.getCurrentUser() : null;
        this.updateAuthUI(!!user);
    }

    updateAuthUI(isLoggedIn) {
        const loginBtn = document.getElementById('login-btn');
        const userInfo = document.getElementById('user-info');
        const usernameDisplay = document.getElementById('username-display');

        if (isLoggedIn) {
            const user = window.authService ? window.authService.getCurrentUser() : null;
            if (loginBtn) loginBtn.style.display = 'none';
            if (userInfo) userInfo.style.display = 'flex';
            if (usernameDisplay) usernameDisplay.textContent = user?.username || 'User';
        } else {
            if (loginBtn) loginBtn.style.display = 'block';
            if (userInfo) userInfo.style.display = 'none';
        }
    }

    handleOAuthCallback() {
        if (window.authModal) {
            window.authModal.handleOAuthCallback();
        }
    }
}

// Global utility functions
function toggleSound() {
    if (window.app) window.app.toggleSound();
}

function toggleTheme() {
    if (window.app) window.app.toggleTheme();
}

function exportSignals() {
    if (window.app) window.app.exportSignals();
}

function showSettings() {
    if (window.app) window.app.showSettings();
}

function saveSettings() {
    if (window.app) window.app.saveSettings();
}

function logout() {
    if (window.authService) {
        window.authService.logout().then(() => {
            if (window.app) window.app.updateAuthUI(false);
            window.location.reload();
        });
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AppController();
});

// Handle page visibility
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.app) {
        window.app.loadMarketData();
    }
});
