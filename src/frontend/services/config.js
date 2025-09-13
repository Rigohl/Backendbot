/**
 * Configuration Service
 * Handles frontend configuration persistence and management
 */

import { Utils } from '../utils/utils.js';

export class ConfigService {
    constructor() {
        this.config = this.getDefaultConfig();
        this.listeners = new Map();
        this.storageKey = 'backendbot_config';
        this.loadConfig();
    }

    /**
     * Get default configuration
     */
    getDefaultConfig() {
        return {
            theme: 'system',
            language: 'en',
            notifications: {
                enabled: true,
                sound: true,
                desktop: false
            },
            metrics: {
                refreshInterval: 5000,
                historyHours: 24
            },
            ui: {
                animations: true,
                compactMode: false,
                autoRefresh: true
            },
            ultra: {
                enabled: false,
                performanceMode: 'balanced'
            }
        };
    }

    /**
     * Load configuration from localStorage
     */
    loadConfig() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                const parsed = JSON.parse(stored);
                this.config = Utils.deepClone({ ...this.getDefaultConfig(), ...parsed });
            }
        } catch (error) {
            console.warn('Failed to load config from localStorage:', error);
            this.config = this.getDefaultConfig();
        }
    }

    /**
     * Save configuration to localStorage
     */
    saveConfig() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.config));
            this.notifyListeners('configSaved', this.config);
        } catch (error) {
            console.error('Failed to save config to localStorage:', error);
        }
    }

    /**
     * Get configuration value
     */
    get(key, defaultValue = null) {
        const keys = key.split('.');
        let value = this.config;

        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return defaultValue;
            }
        }

        return value;
    }

    /**
     * Set configuration value
     */
    set(key, value) {
        const keys = key.split('.');
        let obj = this.config;

        for (let i = 0; i < keys.length - 1; i++) {
            const k = keys[i];
            if (!(k in obj) || typeof obj[k] !== 'object') {
                obj[k] = {};
            }
            obj = obj[k];
        }

        const lastKey = keys[keys.length - 1];
        obj[lastKey] = value;

        this.saveConfig();
        this.notifyListeners('configChanged', { key, value, config: this.config });
    }

    /**
     * Update multiple configuration values
     */
    update(updates) {
        const flattenObject = (obj, prefix = '') => {
            const flattened = {};
            for (const [key, value] of Object.entries(obj)) {
                const newKey = prefix ? `${prefix}.${key}` : key;
                if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                    Object.assign(flattened, flattenObject(value, newKey));
                } else {
                    flattened[newKey] = value;
                }
            }
            return flattened;
        };

        const flattened = flattenObject(updates);
        for (const [key, value] of Object.entries(flattened)) {
            this.set(key, value);
        }
    }

    /**
     * Reset configuration to defaults
     */
    reset() {
        this.config = this.getDefaultConfig();
        this.saveConfig();
        this.notifyListeners('configReset', this.config);
    }

    /**
     * Export configuration
     */
    export() {
        return {
            version: '1.0',
            timestamp: new Date().toISOString(),
            config: Utils.deepClone(this.config)
        };
    }

    /**
     * Import configuration
     */
    import(data) {
        try {
            if (data.config && typeof data.config === 'object') {
                this.config = Utils.deepClone({ ...this.getDefaultConfig(), ...data.config });
                this.saveConfig();
                this.notifyListeners('configImported', this.config);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Failed to import config:', error);
            return false;
        }
    }

    /**
     * Get theme configuration
     */
    getTheme() {
        return this.get('theme', 'system');
    }

    /**
     * Set theme
     */
    setTheme(theme) {
        if (['light', 'dark', 'system'].includes(theme)) {
            this.set('theme', theme);
        }
    }

    /**
     * Get language configuration
     */
    getLanguage() {
        return this.get('language', 'en');
    }

    /**
     * Set language
     */
    setLanguage(language) {
        this.set('language', language);
    }

    /**
     * Get notifications configuration
     */
    getNotifications() {
        return this.get('notifications', {});
    }

    /**
     * Check if notifications are enabled
     */
    areNotificationsEnabled() {
        return this.get('notifications.enabled', true);
    }

    /**
     * Get metrics configuration
     */
    getMetrics() {
        return this.get('metrics', {});
    }

    /**
     * Get UI configuration
     */
    getUI() {
        return this.get('ui', {});
    }

    /**
     * Get ultra mode configuration
     */
    getUltra() {
        return this.get('ultra', {});
    }

    /**
     * Check if ultra mode is enabled
     */
    isUltraEnabled() {
        return this.get('ultra.enabled', false);
    }

    /**
     * Add event listener
     */
    addEventListener(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event).add(callback);
    }

    /**
     * Remove event listener
     */
    removeEventListener(event, callback) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).delete(callback);
        }
    }

    /**
     * Notify listeners
     */
    notifyListeners(event, data) {
        if (this.listeners.has(event)) {
            for (const callback of this.listeners.get(event)) {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in config listener:', error);
                }
            }
        }
    }

    /**
     * Cleanup
     */
    destroy() {
        this.listeners.clear();
    }
}

// Create global instance
export const configService = new ConfigService();