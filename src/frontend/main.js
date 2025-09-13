/**
 * BackendBot Frontend Main Entry Point
 * Initializes the application when DOM is ready
 */

import BackendBotApp from './app.js';

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Show loading overlay
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }

        // Initialize the application
        await BackendBotApp.init();

        // Hide loading overlay
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }

        console.log('BackendBot Frontend loaded successfully');

    } catch (error) {
        console.error('Failed to load BackendBot Frontend:', error);

        // Show error in loading overlay
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            const spinner = loadingOverlay.querySelector('.loading-spinner');
            if (spinner) {
                spinner.innerHTML = `
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load application</p>
                    <small>${error.message}</small>
                    <button onclick="location.reload()" class="retry-btn">Retry</button>
                `;
            }
        }
    }
});

// Global error handler for unhandled errors
window.addEventListener('error', (event) => {
    console.error('Unhandled error:', event.error);
});

// Global handler for unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});

// Export app instance globally for debugging
window.BackendBot = BackendBotApp;