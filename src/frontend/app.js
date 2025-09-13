/**
 * BackendBot Frontend Application
 * Main application coordinator
 */

import { ValidationSystem } from './components/validation.js';
import { NotificationSystem } from './components/notifications.js';
import { ConfigModal } from './components/config.js';
import { ThemeSystem } from './components/theme.js';
import { MetricsSystem } from './components/metrics.js';
import { AuthSystem } from './components/auth.js';
import { UltraSystem } from './components/ultra.js';
import { I18nService } from './services/i18n.js';

class BackendBotApp {
    constructor() {
        this.systems = {};
        this.initialized = false;
        this.i18n = new I18nService();
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            console.log('Initializing BackendBot Frontend...');

            // Initialize i18n first
            await this.i18n.init();

            // Initialize core systems
            this.systems.validation = new ValidationSystem();
            this.systems.notifications = new NotificationSystem();
            this.systems.config = new ConfigModal();
            this.systems.theme = new ThemeSystem();
            this.systems.metrics = new MetricsSystem();
            this.systems.auth = new AuthSystem();
            this.systems.ultra = new UltraSystem();

            // Initialize all systems
            for (const [name, system] of Object.entries(this.systems)) {
                if (typeof system.init === 'function') {
                    await system.init();
                    console.log(`✓ ${name} system initialized`);
                }
            }

            // Set up global error handling
            this.setupErrorHandling();

            // Set up system integration
            this.setupSystemIntegration();

            this.initialized = true;
            console.log('✓ BackendBot Frontend initialized successfully');

            // Show welcome notification
            this.systems.notifications.show('success', 'app_ready', {
                title: this.i18n.t('app.welcome')
            });

        } catch (error) {
            console.error('Failed to initialize BackendBot Frontend:', error);
            this.showInitError(error);
        }
    }

    /**
     * Set up global error handling
     */
    setupErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.systems.notifications.show('error', 'system_error', {
                message: event.error.message
            });
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.systems.notifications.show('error', 'system_error', {
                message: 'Unhandled promise rejection'
            });
        });
    }

    /**
     * Set up integration between systems
     */
    setupSystemIntegration() {
        // Theme system integration with config
        this.systems.config.on('configChanged', (config) => {
            if (config.theme) {
                this.systems.theme.setTheme(config.theme);
            }
        });

        // Metrics system integration with notifications
        this.systems.metrics.on('thresholdExceeded', (data) => {
            this.systems.notifications.show('warning', 'metrics_threshold', data);
        });

        // Auth system integration
        this.systems.auth.on('authStateChanged', (state) => {
            if (state.authenticated) {
                this.systems.notifications.show('success', 'auth_success');
            } else {
                this.systems.notifications.show('info', 'auth_logged_out');
            }
        });

        // Ultra system integration
        this.systems.ultra.on('ultraModeChanged', (enabled) => {
            if (enabled) {
                this.systems.notifications.show('info', 'ultra_enabled');
            } else {
                this.systems.notifications.show('info', 'ultra_disabled');
            }
        });
    }

    /**
     * Show initialization error
     */
    showInitError(error) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'init-error';
        errorDiv.innerHTML = `
            <h2>❌ Initialization Failed</h2>
            <p>${error.message}</p>
            <button onclick="location.reload()">Retry</button>
        `;
        document.body.appendChild(errorDiv);
    }

    /**
     * Get system by name
     */
    getSystem(name) {
        return this.systems[name];
    }

    /**
     * Check if app is initialized
     */
    isInitialized() {
        return this.initialized;
    }

    /**
     * Get i18n service
     */
    getI18n() {
        return this.i18n;
    }
}

// Create global app instance
window.BackendBotApp = new BackendBotApp();

// Export for modules
export { BackendBotApp };
export default window.BackendBotApp;