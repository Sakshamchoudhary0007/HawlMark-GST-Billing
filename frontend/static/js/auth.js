document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const errorMsg = document.getElementById('errorMsg');
    const successMsg = document.getElementById('successMsg');

    const showError = (msg) => {
        if (errorMsg) {
            errorMsg.textContent = msg;
            errorMsg.style.display = 'block';
        }
        if (successMsg) {
            successMsg.style.display = 'none';
        }
    };

    const hideError = () => {
        if (errorMsg) {
            errorMsg.style.display = 'none';
        }
    };

    const showSuccess = (msg) => {
        if (successMsg) {
            successMsg.textContent = msg;
            successMsg.style.display = 'block';
        }
        if (errorMsg) {
            errorMsg.style.display = 'none';
        }
    };

    const hideSuccess = () => {
        if (successMsg) {
            successMsg.style.display = 'none';
        }
    };

    // Check query params on login page (e.g. ?registered=1)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('registered') === '1') {
        showSuccess('Registration successful! You can now log in.');
    }

    const checkAuthStatus = async () => {
        const token = localStorage.getItem('access_token');
        const path = window.location.pathname;
        const isAuthPage = path === '/login' || path === '/register' || path === '/';

        if (!token && !isAuthPage && !path.startsWith('/api')) {
            window.location.href = '/login';
            return;
        }

        if (token && isAuthPage) {
            try {
                // Verify token validity without triggering 401 interception redirect loops
                const res = await fetch('/api/auth/me', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    window.location.href = '/dashboard';
                    return;
                } else {
                    // Stale or expired token
                    API.clearTokens();
                }
            } catch (e) {
                API.clearTokens();
            }
        }
    };

    checkAuthStatus();

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            hideError();
            hideSuccess();
            
            const btn = document.getElementById('loginBtn');
            const originalText = btn.textContent;
            btn.disabled = true;
            btn.textContent = 'Logging in...';

            const formData = new FormData(loginForm);
            const data = Object.fromEntries(formData.entries());

            try {
                const res = await API.post('/auth/login', data);
                API.setToken(res.access_token, res.refresh_token);
                window.location.href = '/dashboard';
            } catch (error) {
                showError(error.message || 'Login failed. Please check your credentials.');
            } finally {
                btn.disabled = false;
                btn.textContent = originalText;
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            hideError();
            hideSuccess();
            
            const password = document.getElementById('password').value;
            const confirm = document.getElementById('confirm_password').value;
            
            if (password.length < 8) {
                showError("Password must be at least 8 characters long.");
                return;
            }

            if (password !== confirm) {
                showError("Passwords do not match.");
                return;
            }

            const btn = document.getElementById('registerBtn');
            const originalText = btn.textContent;
            btn.disabled = true;
            btn.textContent = 'Registering...';

            const formData = new FormData(registerForm);
            const data = Object.fromEntries(formData.entries());
            delete data.confirm_password; // don't send confirm_password to API

            try {
                const res = await API.post('/auth/register', data);
                // Auto-login or redirect to login
                if (res.access_token) {
                    API.setToken(res.access_token, res.refresh_token);
                    window.location.href = '/dashboard';
                } else {
                    window.location.href = '/login?registered=1';
                }
            } catch (error) {
                showError(error.message || 'Registration failed. Please try again.');
            } finally {
                btn.disabled = false;
                btn.textContent = originalText;
            }
        });
    }
});
