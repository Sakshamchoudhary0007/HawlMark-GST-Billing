// Base API client for the GST Billing Application
const API = {
    baseUrl: '/api',
    
    // Get auth token from localStorage
    getToken() {
        return localStorage.getItem('access_token');
    },

    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },
    
    // Set auth token
    setToken(accessToken, refreshToken) {
        if (accessToken) localStorage.setItem('access_token', accessToken);
        if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
    },
    
    // Clear tokens (logout)
    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },
    
    // Get all tokens
    getTokens() {
        return {
            access_token: this.getToken(),
            refresh_token: this.getRefreshToken()
        };
    },

    // Core request method with auth headers, error handling, token refresh
    async request(method, endpoint, data = null, options = {}) {
        let cleanEndpoint = endpoint || '';
        if (cleanEndpoint.startsWith('/api/')) {
            cleanEndpoint = cleanEndpoint.substring(4);
        } else if (cleanEndpoint === '/api') {
            cleanEndpoint = '';
        }
        if (!cleanEndpoint.startsWith('/') && cleanEndpoint.length > 0) {
            cleanEndpoint = '/' + cleanEndpoint;
        }
        const url = `${this.baseUrl}${cleanEndpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            method,
            headers,
            ...options
        };

        if (data && (method !== 'GET' && method !== 'HEAD')) {
            config.body = JSON.stringify(data);
        }

        try {
            let response = await fetch(url, config);

            // Handle 401 Unauthorized (Token refresh logic for protected endpoints)
            const isAuthEndpoint = cleanEndpoint.startsWith('/auth/login') || 
                                   cleanEndpoint.startsWith('/auth/register') || 
                                   cleanEndpoint.startsWith('/auth/refresh');

            if (response.status === 401 && !options._retry && !isAuthEndpoint) {
                const isAuthPage = window.location.pathname === '/login' || window.location.pathname === '/register';
                const refreshToken = this.getRefreshToken();
                if (refreshToken) {
                    try {
                        const refreshRes = await fetch(`${this.baseUrl}/auth/refresh`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ refresh_token: refreshToken })
                        });

                        if (refreshRes.ok) {
                            const refreshData = await refreshRes.json();
                            this.setToken(refreshData.access_token, refreshData.refresh_token);
                            
                            // Retry original request
                            headers['Authorization'] = `Bearer ${refreshData.access_token}`;
                            config.headers = headers;
                            config._retry = true;
                            response = await fetch(url, config);
                        } else {
                            this.clearTokens();
                            if (!isAuthPage) {
                                window.location.href = '/login';
                            }
                            throw new Error('Session expired. Please login again.');
                        }
                    } catch (e) {
                        this.clearTokens();
                        if (!isAuthPage) {
                            window.location.href = '/login';
                        }
                        throw e;
                    }
                } else {
                    this.clearTokens();
                    if (!isAuthPage) {
                        window.location.href = '/login';
                    }
                    throw new Error('Authentication required.');
                }
            }

            const responseData = await response.json().catch(() => ({}));

            if (!response.ok) {
                let errorMsg = 'An error occurred';
                if (responseData.error && responseData.error.message) {
                    errorMsg = responseData.error.message;
                } else if (responseData.detail) {
                    if (Array.isArray(responseData.detail)) {
                        errorMsg = responseData.detail.map(err => {
                            const field = err.loc && err.loc.length > 0 ? err.loc[err.loc.length - 1] : '';
                            return field ? `${field}: ${err.msg}` : err.msg;
                        }).join(', ');
                    } else if (typeof responseData.detail === 'string') {
                        errorMsg = responseData.detail;
                    } else {
                        errorMsg = JSON.stringify(responseData.detail);
                    }
                } else if (responseData.message) {
                    errorMsg = responseData.message;
                }
                throw new Error(errorMsg);
            }

            return responseData;
        } catch (error) {
            console.error(`API Error [${method} ${endpoint}]:`, error);
            throw error;
        }
    },
    
    // Convenience methods
    async get(endpoint, params = {}) {
        const queryString = this.buildQueryString(params);
        return this.request('GET', `${endpoint}${queryString}`);
    },
    
    async post(endpoint, data) {
        return this.request('POST', endpoint, data);
    },
    
    async put(endpoint, data) {
        return this.request('PUT', endpoint, data);
    },
    
    async patch(endpoint, data) {
        return this.request('PATCH', endpoint, data);
    },
    
    async delete(endpoint) {
        return this.request('DELETE', endpoint);
    },
    
    // Build query string from params object
    buildQueryString(params) {
        if (!params || Object.keys(params).length === 0) return '';
        const searchParams = new URLSearchParams();
        for (const [key, value] of Object.entries(params)) {
            if (value !== undefined && value !== null && value !== '') {
                searchParams.append(key, value);
            }
        }
        const qs = searchParams.toString();
        return qs ? `?${qs}` : '';
    }
};
