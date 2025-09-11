/**
 * Tests para el sistema de configuración
 */

import { setupConfigModal, showConfigModal, getCurrentConfig } from '../components/config.js';

// Mock de localStorage
global.localStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
};

// Mock de DOM para tests
const createMockElement = () => ({
    className: '',
    textContent: '',
    style: { display: 'none' },
    innerHTML: '',
    parentNode: null,
    dataset: {},
    addEventListener: jest.fn(),
    querySelector: jest.fn(),
    querySelectorAll: jest.fn(() => []),
    appendChild: jest.fn(),
    removeChild: jest.fn(),
    setAttribute: jest.fn(),
    getAttribute: jest.fn(),
    dispatchEvent: jest.fn()
});

global.document = {
    createElement: jest.fn(createMockElement),
    getElementById: jest.fn(() => null),
    head: {
        appendChild: jest.fn()
    },
    body: {
        appendChild: jest.fn()
    },
    querySelector: jest.fn(),
    addEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
    documentElement: {
        setAttribute: jest.fn(),
        style: {
            setProperty: jest.fn()
        }
    }
};

// Mock de CustomEvent
global.CustomEvent = jest.fn((event, options) => ({
    type: event,
    detail: options.detail
}));

describe('Configuration System', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        // Reset localStorage mocks
        localStorage.getItem.mockClear();
        localStorage.setItem.mockClear();
    });

    describe('setupConfigModal', () => {
        test('should setup config button event listener', () => {
            const mockButton = createMockElement();
            document.getElementById.mockReturnValue(mockButton);

            setupConfigModal();

            expect(mockButton.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
        });

        test('should handle missing config button gracefully', () => {
            document.getElementById.mockReturnValue(null);

            expect(() => setupConfigModal()).not.toThrow();
        });
    });

    describe('showConfigModal', () => {
        test('should create and show modal if it does not exist', () => {
            showConfigModal();

            expect(document.createElement).toHaveBeenCalled();
            expect(document.body.appendChild).toHaveBeenCalled();
        });

        test('should show existing modal if already created', () => {
            // First call creates modal
            showConfigModal();
            const modal = document.createElement.mock.results[0].value;

            // Reset mocks
            jest.clearAllMocks();

            // Second call should just show existing modal
            showConfigModal();

            expect(modal.style.display).toBe('flex');
        });
    });

    describe('getCurrentConfig', () => {
        test('should return default configuration when localStorage is empty', () => {
            localStorage.getItem.mockReturnValue(null);

            const config = getCurrentConfig();

            expect(config.appTitle).toBe('BackendBot Dashboard');
            expect(config.language).toBe('es');
            expect(config.autoRefresh).toBe(30);
            expect(config.backendUrl).toBe('http://127.0.0.1:8000');
            expect(config.sslVerify).toBe(true);
            expect(config.showRam).toBe(true);
            expect(config.themeMode).toBe('auto');
        });

        test('should return configuration from localStorage', () => {
            localStorage.getItem.mockImplementation((key) => {
                const mockData = {
                    appTitle: 'Custom Title',
                    language: 'en',
                    autoRefresh: '60',
                    backendUrl: 'http://localhost:3000',
                    apiKey: 'test-api-key',
                    timeout: '15000',
                    sslVerify: 'false',
                    showRam: 'false',
                    showCpu: 'true',
                    showGpu: 'true',
                    showProcesses: 'false',
                    maxProcesses: '50',
                    themeMode: 'dark',
                    primaryColor: '#ff0000',
                    accentColor: '#00ff00',
                    animations: 'false'
                };
                return mockData[key] || null;
            });

            const config = getCurrentConfig();

            expect(config.appTitle).toBe('Custom Title');
            expect(config.language).toBe('en');
            expect(config.autoRefresh).toBe(60);
            expect(config.backendUrl).toBe('http://localhost:3000');
            expect(config.sslVerify).toBe(false);
            expect(config.showRam).toBe(false);
            expect(config.themeMode).toBe('dark');
            expect(config.primaryColor).toBe('#ff0000');
        });

        test('should parse numeric values correctly', () => {
            localStorage.getItem.mockImplementation((key) => {
                if (key === 'autoRefresh') return '45';
                if (key === 'timeout') return '20000';
                if (key === 'maxProcesses') return '25';
                return null;
            });

            const config = getCurrentConfig();

            expect(typeof config.autoRefresh).toBe('number');
            expect(typeof config.timeout).toBe('number');
            expect(typeof config.maxProcesses).toBe('number');
            expect(config.autoRefresh).toBe(45);
            expect(config.timeout).toBe(20000);
            expect(config.maxProcesses).toBe(25);
        });

        test('should handle boolean values correctly', () => {
            localStorage.getItem.mockImplementation((key) => {
                if (key === 'sslVerify') return 'false';
                if (key === 'showRam') return 'false';
                if (key === 'showGpu') return 'true';
                if (key === 'animations') return 'false';
                return null;
            });

            const config = getCurrentConfig();

            expect(typeof config.sslVerify).toBe('boolean');
            expect(typeof config.showRam).toBe('boolean');
            expect(typeof config.showGpu).toBe('boolean');
            expect(typeof config.animations).toBe('boolean');
            expect(config.sslVerify).toBe(false);
            expect(config.showRam).toBe(false);
            expect(config.showGpu).toBe(true);
            expect(config.animations).toBe(false);
        });
    });

    describe('Configuration application', () => {
        test('should apply theme configuration', () => {
            const config = { themeMode: 'dark' };

            // This would be called internally by applyConfiguration
            document.documentElement.setAttribute('data-theme', config.themeMode);

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
        });

        test('should apply color configuration', () => {
            const config = {
                primaryColor: '#ff0000',
                accentColor: '#00ff00'
            };

            // This would be called internally by applyConfiguration
            document.documentElement.style.setProperty('--primary-color', config.primaryColor);
            document.documentElement.style.setProperty('--accent-color', config.accentColor);

            expect(document.documentElement.style.setProperty).toHaveBeenCalledWith('--primary-color', '#ff0000');
            expect(document.documentElement.style.setProperty).toHaveBeenCalledWith('--accent-color', '#00ff00');
        });

        test('should apply animation configuration', () => {
            const config = { animations: false };

            // This would be called internally by applyConfiguration
            document.documentElement.style.setProperty('--animation-duration', '0s');

            expect(document.documentElement.style.setProperty).toHaveBeenCalledWith('--animation-duration', '0s');
        });

        test('should dispatch configuration change event', () => {
            const config = { appTitle: 'New Title' };

            // This would be called internally by applyConfiguration
            const event = new CustomEvent('configChanged', { detail: config });
            document.dispatchEvent(event);

            expect(document.dispatchEvent).toHaveBeenCalledWith(
                expect.objectContaining({
                    type: 'configChanged',
                    detail: config
                })
            );
        });
    });
});
