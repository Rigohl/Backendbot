/**
 * Tests para el sistema de temas
 */

import { applyTheme, getCurrentTheme, toggleTheme, initTheme } from '../components/theme.js';

// Mock de localStorage
global.localStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
};

// Mock de matchMedia
global.matchMedia = jest.fn().mockImplementation(query => ({
    matches: query === '(prefers-color-scheme: dark)',
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn()
}));

// Mock de document
global.document = {
    documentElement: {
        setAttribute: jest.fn(),
        getAttribute: jest.fn(),
        classList: {
            add: jest.fn(),
            remove: jest.fn(),
            contains: jest.fn()
        },
        style: {
            setProperty: jest.fn()
        }
    },
    addEventListener: jest.fn(),
    dispatchEvent: jest.fn()
};

// Mock de CustomEvent
global.CustomEvent = jest.fn((event, options) => ({
    type: event,
    detail: options.detail
}));

describe('Theme System', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        localStorage.getItem.mockClear();
        localStorage.setItem.mockClear();
        document.documentElement.setAttribute.mockClear();
        document.documentElement.getAttribute.mockClear();
    });

    describe('getCurrentTheme', () => {
        test('should return "light" when localStorage has "light"', () => {
            localStorage.getItem.mockReturnValue('light');

            const theme = getCurrentTheme();

            expect(theme).toBe('light');
        });

        test('should return "dark" when localStorage has "dark"', () => {
            localStorage.getItem.mockReturnValue('dark');

            const theme = getCurrentTheme();

            expect(theme).toBe('dark');
        });

        test('should return "auto" when localStorage has "auto"', () => {
            localStorage.getItem.mockReturnValue('auto');

            const theme = getCurrentTheme();

            expect(theme).toBe('auto');
        });

        test('should return "auto" when localStorage is empty', () => {
            localStorage.getItem.mockReturnValue(null);

            const theme = getCurrentTheme();

            expect(theme).toBe('auto');
        });

        test('should return "auto" when localStorage has invalid value', () => {
            localStorage.getItem.mockReturnValue('invalid');

            const theme = getCurrentTheme();

            expect(theme).toBe('auto');
        });
    });

    describe('applyTheme', () => {
        test('should apply light theme', () => {
            applyTheme('light');

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'light');
            expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'light');
        });

        test('should apply dark theme', () => {
            applyTheme('dark');

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
            expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
        });

        test('should apply auto theme and detect system preference', () => {
            global.matchMedia.mockReturnValue({
                matches: true,
                media: '(prefers-color-scheme: dark)',
                onchange: null,
                addListener: jest.fn(),
                removeListener: jest.fn(),
                addEventListener: jest.fn(),
                removeEventListener: jest.fn(),
                dispatchEvent: jest.fn()
            });

            applyTheme('auto');

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
            expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'auto');
        });

        test('should apply auto theme and detect light system preference', () => {
            global.matchMedia.mockReturnValue({
                matches: false,
                media: '(prefers-color-scheme: dark)',
                onchange: null,
                addListener: jest.fn(),
                removeListener: jest.fn(),
                addEventListener: jest.fn(),
                removeEventListener: jest.fn(),
                dispatchEvent: jest.fn()
            });

            applyTheme('auto');

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'light');
            expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'auto');
        });

        test('should dispatch theme change event', () => {
            applyTheme('dark');

            expect(document.dispatchEvent).toHaveBeenCalledWith(
                expect.objectContaining({
                    type: 'themeChanged',
                    detail: { theme: 'dark' }
                })
            );
        });

        test('should handle invalid theme gracefully', () => {
            applyTheme('invalid');

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'light');
            expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'invalid');
        });
    });

    describe('toggleTheme', () => {
        test('should toggle from light to dark', () => {
            localStorage.getItem.mockReturnValue('light');

            toggleTheme();

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
            expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
        });

        test('should toggle from dark to light', () => {
            localStorage.getItem.mockReturnValue('dark');

            toggleTheme();

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'light');
            expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'light');
        });

        test('should toggle from auto to light when system is light', () => {
            localStorage.getItem.mockReturnValue('auto');
            global.matchMedia.mockReturnValue({
                matches: false,
                media: '(prefers-color-scheme: dark)',
                onchange: null,
                addListener: jest.fn(),
                removeListener: jest.fn(),
                addEventListener: jest.fn(),
                removeEventListener: jest.fn(),
                dispatchEvent: jest.fn()
            });

            toggleTheme();

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
            expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
        });

        test('should toggle from auto to dark when system is dark', () => {
            localStorage.getItem.mockReturnValue('auto');
            global.matchMedia.mockReturnValue({
                matches: true,
                media: '(prefers-color-scheme: dark)',
                onchange: null,
                addListener: jest.fn(),
                removeListener: jest.fn(),
                addEventListener: jest.fn(),
                removeEventListener: jest.fn(),
                dispatchEvent: jest.fn()
            });

            toggleTheme();

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'light');
            expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'light');
        });
    });

    describe('initTheme', () => {
        test('should initialize theme from localStorage', () => {
            localStorage.getItem.mockReturnValue('dark');

            initTheme();

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
        });

        test('should initialize theme to auto when localStorage is empty', () => {
            localStorage.getItem.mockReturnValue(null);
            global.matchMedia.mockReturnValue({
                matches: true,
                media: '(prefers-color-scheme: dark)',
                onchange: null,
                addListener: jest.fn(),
                removeListener: jest.fn(),
                addEventListener: jest.fn(),
                removeEventListener: jest.fn(),
                dispatchEvent: jest.fn()
            });

            initTheme();

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
        });

        test('should add system theme change listener', () => {
            localStorage.getItem.mockReturnValue('auto');

            initTheme();

            expect(document.addEventListener).toHaveBeenCalledWith('change', expect.any(Function));
        });

        test('should handle system theme changes when theme is auto', () => {
            localStorage.getItem.mockReturnValue('auto');
            let mediaQueryCallback;

            global.matchMedia.mockImplementation(query => {
                const mediaQuery = {
                    matches: false,
                    media: query,
                    onchange: null,
                    addListener: jest.fn(),
                    removeListener: jest.fn(),
                    addEventListener: jest.fn(cb => { mediaQueryCallback = cb; }),
                    removeEventListener: jest.fn(),
                    dispatchEvent: jest.fn()
                };
                return mediaQuery;
            });

            initTheme();

            // Simulate system theme change to dark
            mediaQueryCallback({ matches: true });

            expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
        });

        test('should not respond to system theme changes when theme is not auto', () => {
            localStorage.getItem.mockReturnValue('light');
            let mediaQueryCallback;

            global.matchMedia.mockImplementation(query => {
                const mediaQuery = {
                    matches: false,
                    media: query,
                    onchange: null,
                    addListener: jest.fn(),
                    removeListener: jest.fn(),
                    addEventListener: jest.fn(cb => { mediaQueryCallback = cb; }),
                    removeEventListener: jest.fn(),
                    dispatchEvent: jest.fn()
                };
                return mediaQuery;
            });

            initTheme();

            // Simulate system theme change
            mediaQueryCallback({ matches: true });

            // Should not change theme since it's not auto
            expect(document.documentElement.setAttribute).toHaveBeenCalledTimes(1); // Only initial call
        });
    });

    describe('Theme persistence', () => {
        test('should persist theme changes to localStorage', () => {
            applyTheme('dark');

            expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
        });

        test('should persist toggle changes to localStorage', () => {
            localStorage.getItem.mockReturnValue('light');

            toggleTheme();

            expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
        });
    });
});
