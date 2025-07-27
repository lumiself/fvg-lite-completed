class SignalRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.signals = [];
        this.settings = {
            maxSignals: 100,
            autoScroll: true,
            soundEnabled: true
        };
    }

    renderSignal(signal) {
        if (!signal || !signal.symbol) return;

        const signalDiv = document.createElement('div');
        signalDiv.className = 'signal-item';
        signalDiv.dataset.signalId = signal.id || Date.now();

        const signalType = window.formatters.formatSignalType(signal.type);
        const confidence = window.formatters.formatConfidence(signal.confidence);
        const timestamp = window.formatters.formatTimestamp(signal.timestamp);

        signalDiv.innerHTML = `
            <div class="signal-header">
                <span class="signal-pair">${signal.symbol}</span>
                <span class="signal-type ${signalType.class}">${signalType.text}</span>
            </div>
            <div class="signal-details">
                <div class="signal-detail">
                    <span>Price:</span>
                    <span>${window.formatters.formatPrice(signal.price)}</span>
                </div>
                <div class="signal-detail">
                    <span>Confidence:</span>
                    <span class="${confidence.class}">${confidence.text}</span>
                </div>
                <div class="signal-detail">
                    <span>Time:</span>
                    <span>${timestamp}</span>
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
                ${signal.volume ? `
                <div class="signal-detail">
                    <span>Volume:</span>
                    <span>${window.formatters.formatVolume(signal.volume)}</span>
                </div>
                ` : ''}
            </div>
            <div class="signal-actions">
                <button class="btn btn-success btn-sm trade-btn" onclick="window.tradePanel.show(${JSON.stringify(signal).replace(/"/g, '&quot;')})">
                    <i class="fas fa-play"></i> Trade
                </button>
            </div>
        `;

        return signalDiv;
    }

    addSignal(signal) {
        if (!this.container) return;

        // Remove loading message if present
        const loading = this.container.querySelector('.loading');
        if (loading) {
            loading.remove();
        }

        const signalElement = this.renderSignal(signal);
        
        // Add to beginning of container
        this.container.insertBefore(signalElement, this.container.firstChild);
        
        // Add to signals array
        this.signals.unshift(signal);
        
        // Limit number of signals
        if (this.signals.length > this.settings.maxSignals) {
            this.signals = this.signals.slice(0, this.settings.maxSignals);
            const lastChild = this.container.lastElementChild;
            if (lastChild) lastChild.remove();
        }

        // Auto-scroll if enabled
        if (this.settings.autoScroll) {
            this.container.scrollTop = 0;
        }

        // Play sound if enabled
        if (this.settings.soundEnabled) {
            this.playNotificationSound();
        }

        // Add animation
        signalElement.style.animation = 'fadeIn 0.3s ease-in-out';
    }

    clearSignals() {
        if (!this.container) return;
        
        this.signals = [];
        this.container.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Waiting for signals...</p>
            </div>
        `;
    }

    updateSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
    }

    playNotificationSound() {
        // Create a simple beep sound using Web Audio API
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
            console.warn('Could not play notification sound:', error);
        }
    }

    exportSignals() {
        const data = {
            exportedAt: new Date().toISOString(),
            signals: this.signals
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `signals-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    renderSignals(signals) {
        if (!this.container) return;

        this.clearSignals();
        
        if (!signals || signals.length === 0) {
            this.container.innerHTML = `
                <div class="loading">
                    <i class="fas fa-info-circle"></i>
                    <p>No signals available</p>
                </div>
            `;
            return;
        }

        signals.forEach(signal => {
            this.addSignal(signal);
        });
    }

    highlightSignal(signalId) {
        const element = this.container.querySelector(`[data-signal-id="${signalId}"]`);
        if (element) {
            element.style.backgroundColor = 'var(--primary-color)';
            element.style.color = 'white';
            setTimeout(() => {
                element.style.backgroundColor = '';
                element.style.color = '';
            }, 2000);
        }
    }
}

// Create global instance
window.signalRenderer = new SignalRenderer('signal-feed');
