/**
 * Setup file for Jest tests
 */

// Mock de console para reducir ruido en tests
global.console = {
    ...console,
    // Mantener logs de error para debugging pero silenciar otros
    log: jest.fn(),
    debug: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    // Mantener error y trace para debugging
    error: console.error,
    trace: console.trace
};

// Mock de localStorage
global.localStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
};

// Mock de sessionStorage
global.sessionStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
};

// Mock de document
global.document = {
    ...document,
    createElement: jest.fn().mockImplementation(tag => ({
        tagName: tag.toUpperCase(),
        classList: {
            add: jest.fn(),
            remove: jest.fn(),
            contains: jest.fn(),
            toggle: jest.fn()
        },
        style: {},
        textContent: '',
        innerHTML: '',
        appendChild: jest.fn(),
        removeChild: jest.fn(),
        insertBefore: jest.fn(),
        setAttribute: jest.fn(),
        getAttribute: jest.fn(),
        removeAttribute: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
        querySelector: jest.fn(),
        querySelectorAll: jest.fn(),
        getElementById: jest.fn(),
        parentNode: null,
        nextSibling: null,
        children: [],
        value: '',
        checked: false,
        type: 'text',
        name: '',
        placeholder: ''
    })),
    body: {
        appendChild: jest.fn(),
        removeChild: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
        classList: {
            add: jest.fn(),
            remove: jest.fn(),
            contains: jest.fn(),
            toggle: jest.fn()
        }
    },
    head: {
        appendChild: jest.fn(),
        removeChild: jest.fn()
    },
    documentElement: {
        setAttribute: jest.fn(),
        getAttribute: jest.fn(),
        classList: {
            add: jest.fn(),
            remove: jest.fn(),
            contains: jest.fn(),
            toggle: jest.fn()
        }
    },
    createTextNode: jest.fn().mockReturnValue({}),
    getElementById: jest.fn(),
    querySelector: jest.fn(),
    querySelectorAll: jest.fn().mockReturnValue([]),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn()
};

// Mock de CustomEvent
global.CustomEvent = class CustomEvent {
    constructor(event, options = {}) {
        this.type = event;
        this.detail = options.detail;
        this.bubbles = options.bubbles || false;
        this.cancelable = options.cancelable || false;
    }
};

// Mock de matchMedia
global.matchMedia = jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn()
}));

// Mock de ResizeObserver
global.ResizeObserver = class ResizeObserver {
    constructor(cb) {
        this.cb = cb;
    }
    observe() { }
    unobserve() { }
    disconnect() { }
};

// Mock de IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
    constructor(cb) {
        this.cb = cb;
    }
    observe() { }
    unobserve() { }
    disconnect() { }
};

// Mock de requestAnimationFrame
global.requestAnimationFrame = jest.fn(cb => setTimeout(cb, 16));
global.cancelAnimationFrame = jest.fn(id => clearTimeout(id));

// Mock de setTimeout y setInterval para tests más rápidos
jest.useFakeTimers();

// Helper para esperar a que se resuelvan todas las promesas pendientes
global.flushPromises = () => new Promise(resolve => setImmediate(resolve));

// Helper para esperar a que se ejecuten los timers
global.advanceTimers = (ms = 0) => jest.advanceTimersByTime(ms);