class AuthModal {
    constructor() {
        this.modal = null;
        this.currentView = 'login';
        this.init();
    }

    init() {
        this.createModal();
        this.setupEventListeners();
    }

    createModal() {
        const modalHTML = `
            <div id="auth-modal" class="modal">
                <div class="modal-content auth-modal">
                    <span class="close">&times;</span>
                    <div class="auth-container">
                        <div class="auth-tabs">
                            <button class="auth-tab active" data-view="login">Login</button>
                            <button class="auth-tab" data-view="register">Register</button>
                            <button class="auth-tab" data-view="deriv">Deriv OAuth</button>
                        </div>
                        
                        <div class="auth-form-container">
                            <!-- Login Form -->
                            <form id="login-form" class="auth-form active">
                                <h2>Login to Your Account</h2>
                                <div class="form-group">
                                    <label for="login-username">Username</label>
                                    <input type="text" id="login-username" required>
                                </div>
                                <div class="form-group">
                                    <label for="login-password">Password</label>
                                    <input type="password" id="login-password" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Login</button>
                                <div class="form-message" id="login-message"></div>
                            </form>

                            <!-- Register Form -->
                            <form id="register-form" class="auth-form">
                                <h2>Create New Account</h2>
                                <div class="form-group">
                                    <label for="register-username">Username</label>
                                    <input type="text" id="register-username" required>
                                </div>
                                <div class="form-group">
                                    <label for="register-email">Email</label>
                                    <input type="email" id="register-email" required>
                                </div>
                                <div class="form-group">
                                    <label for="register-password">Password</label>
                                    <input type="password" id="register-password" required>
                                </div>
                                <div class="form-group">
                                    <label for="register-confirm-password">Confirm Password</label>
                                    <input type="password" id="register-confirm-password" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Register</button>
                                <div class="form-message" id="register-message"></div>
                            </form>

                            <!-- Deriv OAuth -->
                            <div id="deriv-form" class="auth-form">
                                <h2>Connect with Deriv</h2>
                                <p>Connect your Deriv account to start trading with real money.</p>
                                <button id="deriv-oauth-btn" class="btn btn-primary">
                                    <i class="fas fa-external-link-alt"></i>
                                    Connect Deriv Account
                                </button>
                                <div class="form-message" id="deriv-message"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('auth-modal');
    }

    setupEventListeners() {
        // Close modal
        const closeBtn = this.modal.querySelector('.close');
        closeBtn.addEventListener('click', () => this.hide());

        // Close on outside click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.hide();
        });

        // Tab switching
        const tabs = this.modal.querySelectorAll('.auth-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const view = e.target.dataset.view;
                this.switchView(view);
            });
        });

        // Form submissions
        this.setupFormSubmissions();
    }

    setupFormSubmissions() {
        // Login form
        const loginForm = document.getElementById('login-form');
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin();
        });

        // Register form
        const registerForm = document.getElementById('register-form');
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleRegister();
        });

        // Deriv OAuth
        const derivBtn = document.getElementById('deriv-oauth-btn');
        derivBtn.addEventListener('click', async () => {
            await this.handleDerivOAuth();
        });
    }

    switchView(view) {
        this.currentView = view;
        
        // Update tabs
        const tabs = this.modal.querySelectorAll('.auth-tab');
        tabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.view === view);
        });

        // Update forms
        const forms = this.modal.querySelectorAll('.auth-form');
        forms.forEach(form => {
            form.classList.toggle('active', form.id === `${view}-form` || form.id === `${view}`);
        });
    }

    async handleLogin() {
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        const messageEl = document.getElementById('login-message');

        messageEl.textContent = 'Logging in...';
        messageEl.className = 'form-message info';

        const result = await window.authService.login(username, password);

        if (result.success) {
            messageEl.textContent = 'Login successful!';
            messageEl.className = 'form-message success';
            
            setTimeout(() => {
                this.hide();
                window.location.reload();
            }, 1000);
        } else {
            messageEl.textContent = result.error || 'Login failed';
            messageEl.className = 'form-message error';
        }
    }

    async handleRegister() {
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('register-confirm-password').value;
        const messageEl = document.getElementById('register-message');

        if (password !== confirmPassword) {
            messageEl.textContent = 'Passwords do not match';
            messageEl.className = 'form-message error';
            return;
        }

        messageEl.textContent = 'Creating account...';
        messageEl.className = 'form-message info';

        const result = await window.authService.register(username, email, password);

        if (result.success) {
            messageEl.textContent = 'Registration successful! Please login.';
            messageEl.className = 'form-message success';
            
            // Switch to login form
            setTimeout(() => {
                this.switchView('login');
                document.getElementById('login-username').value = username;
            }, 1500);
        } else {
            messageEl.textContent = result.error || 'Registration failed';
            messageEl.className = 'form-message error';
        }
    }

    async handleDerivOAuth() {
        const messageEl = document.getElementById('deriv-message');
        messageEl.textContent = 'Preparing OAuth...';
        messageEl.className = 'form-message info';

        const oauthUrl = await window.authService.getDerivOAuthUrl();
        
        if (oauthUrl) {
            // Redirect to Deriv OAuth
            window.location.href = oauthUrl;
        } else {
            messageEl.textContent = 'Failed to get OAuth URL';
            messageEl.className = 'form-message error';
        }
    }

    show() {
        this.modal.style.display = 'block';
    }

    hide() {
        this.modal.style.display = 'none';
    }

    handleOAuthCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');

        if (code && state) {
            window.authService.handleDerivCallback(code, state).then(result => {
                if (result.success) {
                    // Clean URL
                    window.history.replaceState({}, document.title, window.location.pathname);
                    window.location.reload();
                }
            });
        }
    }
}

// Create global instance
window.authModal = new AuthModal();
