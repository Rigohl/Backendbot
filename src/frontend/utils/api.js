/**
 * API Utilities
 * Helper functions for backend communication
 */

export class APIUtils {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    /**
     * Make a GET request
     */
    async get(endpoint, params = {}) {
        const url = new URL(`${this.baseURL}${endpoint}`, window.location.origin);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

        const response = await fetch(url, {
            method: 'GET',
            headers: this.defaultHeaders
        });

        return this.handleResponse(response);
    }

    /**
     * Make a POST request
     */
    async post(endpoint, data = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers: this.defaultHeaders,
            body: JSON.stringify(data)
        });

        return this.handleResponse(response);
    }

    /**
     * Make a PUT request
     */
    async put(endpoint, data = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'PUT',
            headers: this.defaultHeaders,
            body: JSON.stringify(data)
        });

        return this.handleResponse(response);
    }

    /**
     * Make a DELETE request
     */
    async delete(endpoint) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'DELETE',
            headers: this.defaultHeaders
        });

        return this.handleResponse(response);
    }

    /**
     * Handle API response
     */
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Network error' }));
            throw new Error(error.message || `HTTP ${response.status}`);
        }

        // Handle empty responses
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return await response.text();
        }
    }

    /**
     * Set authorization token
     */
    setAuthToken(token) {
        if (token) {
            this.defaultHeaders['Authorization'] = `Bearer ${token}`;
        } else {
            delete this.defaultHeaders['Authorization'];
        }
    }

    /**
     * Add custom header
     */
    addHeader(key, value) {
        this.defaultHeaders[key] = value;
    }

    /**
     * Remove header
     */
    removeHeader(key) {
        delete this.defaultHeaders[key];
    }

    /**
     * Test backend connection
     */
    async testConnection() {
        try {
            await this.get('/health');
            return true;
        } catch (error) {
            console.warn('Backend connection test failed:', error);
            return false;
        }
    }

    /**
     * Retry failed requests
     */
    async retryRequest(requestFn, maxRetries = 3, delay = 1000) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                return await requestFn();
            } catch (error) {
                if (i === maxRetries - 1) {
                    throw error;
                }
                await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
            }
        }
    }
}

// Create global API instance
export const api = new APIUtils();