// Enhanced WebSocketService: Handles real-time communication with robust error handling and reconnection
class WebSocketService {
    constructor() {
        this.ws = null;
        this.eventHandlers = {};
        this.connected = false;
        this.url = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.reconnectTimeout = null;
        this.heartbeatInterval = null;
        this.lastPingTime = null;
    }

    connect(url) {
        if (this.ws) {
            this.disconnect();
        }
        
        this.url = url;
        this.reconnectAttempts = 0;
        
        console.log(`[WebSocket] Attempting to connect to: ${url}`);
        this._createConnection();
    }

    _createConnection() {
        try {
            this.ws = new WebSocket(this.url);
            
            // Connection opened
            this.ws.onopen = () => {
                console.log('[WebSocket] Connection established');
                this.connected = true;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;
                
                // Start heartbeat
                this._startHeartbeat();
                
                this._emit('connected');
            };

            // Connection closed
            this.ws.onclose = (event) => {
                console.log(`[WebSocket] Connection closed: ${event.code} - ${event.reason}`);
                this.connected = false;
                this._stopHeartbeat();
                this._emit('disconnected', event);
                
                // Attempt reconnection if not manually disconnected
                if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
                    this._scheduleReconnect();
                }
            };

            // Connection error
            this.ws.onerror = (error) => {
                console.error('[WebSocket] Connection error:', error);
                this._emit('error', error);
            };

            // Message received
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    
                    // Handle ping/pong for heartbeat
                    if (data.type === 'ping') {
                        this._send({ type: 'pong', timestamp: Date.now() });
                        return;
                    }
                    
                    // Handle signal or other events
                    if (data.type) {
                        this._emit(data.type, data.data || data);
                    }
                } catch (error) {
                    console.error('[WebSocket] Failed to parse message:', error);
                    this._emit('parseError', error);
                }
            };

        } catch (error) {
            console.error('[WebSocket] Failed to create connection:', error);
            this._emit('error', error);
        }
    }

    _scheduleReconnect() {
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
        }
        
        this.reconnectAttempts++;
        const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000); // Max 30 seconds
        
        console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        this.reconnectTimeout = setTimeout(() => {
            console.log('[WebSocket] Attempting reconnection...');
            this._createConnection();
        }, delay);
    }

    _startHeartbeat() {
        this._stopHeartbeat();
        
        // Send ping every 30 seconds
        this.heartbeatInterval = setInterval(() => {
            if (this.connected && this.ws.readyState === WebSocket.OPEN) {
                this.lastPingTime = Date.now();
                this._send({ type: 'ping', timestamp: this.lastPingTime });
            }
        }, 30000);
    }

    _stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    disconnect() {
        console.log('[WebSocket] Disconnecting...');
        
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }
        
        this._stopHeartbeat();
        
        if (this.ws) {
            this.ws.close(1000, 'Manual disconnect');
            this.ws = null;
        }
        
        this.connected = false;
        this.reconnectAttempts = 0;
    }

    isConnected() {
        return this.connected && this.ws && this.ws.readyState === WebSocket.OPEN;
    }

    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    off(event, handler) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event] = this.eventHandlers[event].filter(h => h !== handler);
        }
    }

    _emit(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`[WebSocket] Error in event handler for ${event}:`, error);
                }
            });
        }
    }

    send(data) {
        if (this.isConnected()) {
            try {
                this.ws.send(JSON.stringify(data));
                return true;
            } catch (error) {
                console.error('[WebSocket] Failed to send message:', error);
                this._emit('sendError', error);
                return false;
            }
        } else {
            console.warn('[WebSocket] Cannot send message - not connected');
            return false;
        }
    }

    getConnectionState() {
        if (!this.ws) return 'disconnected';
        
        switch (this.ws.readyState) {
            case WebSocket.CONNECTING:
                return 'connecting';
            case WebSocket.OPEN:
                return 'connected';
            case WebSocket.CLOSING:
                return 'closing';
            case WebSocket.CLOSED:
                return 'closed';
            default:
                return 'unknown';
        }
    }

    getConnectionInfo() {
        return {
            connected: this.isConnected(),
            url: this.url,
            readyState: this.getConnectionState(),
            reconnectAttempts: this.reconnectAttempts,
            maxReconnectAttempts: this.maxReconnectAttempts
        };
    }
}

// Make available globally as wsService
window.wsService = new WebSocketService();
