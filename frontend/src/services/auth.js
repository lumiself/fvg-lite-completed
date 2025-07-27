class AuthService {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
        this.currentUser = null;
        this.sessionToken = localStorage.getItem('fvg_session_token');
    }

    async login(username, password) {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            this.sessionToken = data.session_token;
            this.currentUser = data.user;
            
            localStorage.setItem('fvg_session_token', this.sessionToken);
            localStorage.setItem('fvg_user', JSON.stringify(this.currentUser));
            
            return { success: true, user: this.currentUser };
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: error.message };
        }
    }

    async register(username, email, password) {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password })
            });

            if (!response.ok) {
                throw new Error('Registration failed');
            }

            const data = await response.json();
            return { success: true, message: data.message };
        } catch (error) {
            console.error('Registration error:', error);
            return { success: false, error: error.message };
        }
    }

    async logout() {
        try {
            if (this.sessionToken) {
                await fetch(`${this.baseURL}/api/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.sessionToken}`
                    }
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.clearSession();
        }
    }

    async validateSession() {
        if (!this.sessionToken) return false;

        try {
            const response = await fetch(`${this.baseURL}/api/auth/validate`, {
                headers: {
                    'Authorization': `Bearer ${this.sessionToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.currentUser = data.user;
                localStorage.setItem('fvg_user', JSON.stringify(this.currentUser));
                return true;
            } else {
                this.clearSession();
                return false;
            }
        } catch (error) {
            console.error('Session validation error:', error);
            this.clearSession();
            return false;
        }
    }

    async getDerivOAuthUrl() {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/deriv/oauth-url`);
            const data = await response.json();
            return data.oauth_url;
        } catch (error) {
            console.error('Failed to get OAuth URL:', error);
            return null;
        }
    }

    async handleDerivCallback(code, state) {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/deriv/callback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code, state })
            });

            if (!response.ok) {
                throw new Error('OAuth callback failed');
            }

            const data = await response.json();
            this.sessionToken = data.session_token;
            this.currentUser = data.user;
            
            localStorage.setItem('fvg_session_token', this.sessionToken);
            localStorage.setItem('fvg_user', JSON.stringify(this.currentUser));
            
            return { success: true, user: this.currentUser };
        } catch (error) {
            console.error('OAuth callback error:', error);
            return { success: false, error: error.message };
        }
    }

    getCurrentUser() {
        if (!this.currentUser) {
            const stored = localStorage.getItem('fvg_user');
            if (stored) {
                this.currentUser = JSON.parse(stored);
            }
        }
        return this.currentUser;
    }

    isLoggedIn() {
        return !!this.sessionToken && !!this.getCurrentUser();
    }

    clearSession() {
        this.sessionToken = null;
        this.currentUser = null;
        localStorage.removeItem('fvg_session_token');
        localStorage.removeItem('fvg_user');
    }

    getAuthHeaders() {
        return this.sessionToken ? { 'Authorization': `Bearer ${this.sessionToken}` } : {};
    }
}

// Create global instance
window.authService = new AuthService();
