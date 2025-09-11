/**
 * Tests para el sistema de métricas
 */

import { updateMetrics, formatBytes, formatPercentage, formatTime, getMetricsData } from '../components/metrics.js';

// Mock de fetch
global.fetch = jest.fn();

// Mock de console
global.console = {
    log: jest.fn(),
    error: jest.fn(),
    warn: jest.fn()
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
    querySelectorAll: jest.fn(() => []),
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

describe('Metrics System', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        fetch.mockClear();
    });

    describe('formatBytes', () => {
        test('should format bytes correctly', () => {
            expect(formatBytes(0)).toBe('0 B');
            expect(formatBytes(1024)).toBe('1.00 KB');
            expect(formatBytes(1024 * 1024)).toBe('1.00 MB');
            expect(formatBytes(1024 * 1024 * 1024)).toBe('1.00 GB');
            expect(formatBytes(1024 * 1024 * 1024 * 1024)).toBe('1.00 TB');
        });

        test('should handle decimal values', () => {
            expect(formatBytes(1536)).toBe('1.50 KB');
            expect(formatBytes(1024 * 1024 * 1.5)).toBe('1.50 MB');
        });

        test('should handle negative values', () => {
            expect(formatBytes(-1024)).toBe('-1.00 KB');
        });

        test('should handle very large values', () => {
            expect(formatBytes(1024 * 1024 * 1024 * 1024 * 1024)).toBe('1024.00 TB');
        });
    });

    describe('formatPercentage', () => {
        test('should format percentages correctly', () => {
            expect(formatPercentage(0)).toBe('0.0%');
            expect(formatPercentage(0.5)).toBe('50.0%');
            expect(formatPercentage(1)).toBe('100.0%');
            expect(formatPercentage(0.123)).toBe('12.3%');
            expect(formatPercentage(0.999)).toBe('99.9%');
        });

        test('should handle edge cases', () => {
            expect(formatPercentage(0.0001)).toBe('0.0%');
            expect(formatPercentage(1.5)).toBe('150.0%');
            expect(formatPercentage(-0.1)).toBe('-10.0%');
        });
    });

    describe('formatTime', () => {
        test('should format time correctly', () => {
            expect(formatTime(0)).toBe('0ms');
            expect(formatTime(1000)).toBe('1.00s');
            expect(formatTime(60000)).toBe('1.00m');
            expect(formatTime(3600000)).toBe('1.00h');
            expect(formatTime(86400000)).toBe('1.00d');
        });

        test('should handle decimal values', () => {
            expect(formatTime(1500)).toBe('1.50s');
            expect(formatTime(90000)).toBe('1.50m');
        });

        test('should handle negative values', () => {
            expect(formatTime(-1000)).toBe('-1.00s');
        });

        test('should handle very large values', () => {
            expect(formatTime(86400000 * 365)).toBe('365.00d');
        });
    });

    describe('getMetricsData', () => {
        test('should fetch metrics data successfully', async () => {
            const mockData = {
                ram: { used: 1024, total: 8192, percentage: 12.5 },
                cpu: { usage: 45.2, cores: 8 },
                gpu: { usage: 30.1, memory_used: 512, memory_total: 2048 },
                processes: [
                    { pid: 1, name: 'system', cpu: 5.2, memory: 128 },
                    { pid: 2, name: 'app', cpu: 15.8, memory: 256 }
                ]
            };

            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockData)
            });

            const result = await getMetricsData();

            expect(fetch).toHaveBeenCalledWith('/api/metrics');
            expect(result).toEqual(mockData);
        });

        test('should handle fetch errors gracefully', async () => {
            fetch.mockRejectedValueOnce(new Error('Network error'));

            const result = await getMetricsData();

            expect(result).toBeNull();
            expect(console.error).toHaveBeenCalledWith('Error fetching metrics:', expect.any(Error));
        });

        test('should handle HTTP errors gracefully', async () => {
            fetch.mockResolvedValueOnce({
                ok: false,
                status: 500,
                statusText: 'Internal Server Error'
            });

            const result = await getMetricsData();

            expect(result).toBeNull();
            expect(console.error).toHaveBeenCalledWith('Error fetching metrics: 500 Internal Server Error');
        });

        test('should handle invalid JSON response', async () => {
            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.reject(new Error('Invalid JSON'))
            });

            const result = await getMetricsData();

            expect(result).toBeNull();
            expect(console.error).toHaveBeenCalledWith('Error parsing metrics data:', expect.any(Error));
        });
    });

    describe('updateMetrics', () => {
        let mockElements;

        beforeEach(() => {
            mockElements = {
                ramUsed: createMockElement(),
                ramTotal: createMockElement(),
                ramPercentage: createMockElement(),
                ramProgress: createMockElement(),
                cpuUsage: createMockElement(),
                cpuProgress: createMockElement(),
                gpuUsage: createMockElement(),
                gpuMemory: createMockElement(),
                gpuProgress: createMockElement(),
                processesList: createMockElement(),
                lastUpdate: createMockElement()
            };

            document.getElementById.mockImplementation((id) => mockElements[id] || null);
        });

        test('should update RAM metrics correctly', async () => {
            const mockData = {
                ram: { used: 2048, total: 8192, percentage: 25.0 },
                cpu: { usage: 45.2, cores: 8 },
                gpu: { usage: 30.1, memory_used: 512, memory_total: 2048 },
                processes: []
            };

            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockData)
            });

            await updateMetrics();

            expect(mockElements.ramUsed.textContent).toBe('2.00 MB');
            expect(mockElements.ramTotal.textContent).toBe('8.00 MB');
            expect(mockElements.ramPercentage.textContent).toBe('25.0%');
            expect(mockElements.ramProgress.style.width).toBe('25%');
        });

        test('should update CPU metrics correctly', async () => {
            const mockData = {
                ram: { used: 1024, total: 8192, percentage: 12.5 },
                cpu: { usage: 67.8, cores: 8 },
                gpu: { usage: 30.1, memory_used: 512, memory_total: 2048 },
                processes: []
            };

            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockData)
            });

            await updateMetrics();

            expect(mockElements.cpuUsage.textContent).toBe('67.8%');
            expect(mockElements.cpuProgress.style.width).toBe('67.8%');
        });

        test('should update GPU metrics correctly', async () => {
            const mockData = {
                ram: { used: 1024, total: 8192, percentage: 12.5 },
                cpu: { usage: 45.2, cores: 8 },
                gpu: { usage: 85.3, memory_used: 1536, memory_total: 2048 },
                processes: []
            };

            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockData)
            });

            await updateMetrics();

            expect(mockElements.gpuUsage.textContent).toBe('85.3%');
            expect(mockElements.gpuMemory.textContent).toBe('1.50 MB / 2.00 MB');
            expect(mockElements.gpuProgress.style.width).toBe('85.3%');
        });

        test('should update processes list correctly', async () => {
            const mockData = {
                ram: { used: 1024, total: 8192, percentage: 12.5 },
                cpu: { usage: 45.2, cores: 8 },
                gpu: { usage: 30.1, memory_used: 512, memory_total: 2048 },
                processes: [
                    { pid: 1, name: 'system', cpu: 5.2, memory: 128 },
                    { pid: 2, name: 'chrome', cpu: 15.8, memory: 512 }
                ]
            };

            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockData)
            });

            await updateMetrics();

            expect(mockElements.processesList.innerHTML).toContain('system');
            expect(mockElements.processesList.innerHTML).toContain('chrome');
            expect(mockElements.processesList.innerHTML).toContain('5.2%');
            expect(mockElements.processesList.innerHTML).toContain('128.00 KB');
        });

        test('should update last update timestamp', async () => {
            const mockData = {
                ram: { used: 1024, total: 8192, percentage: 12.5 },
                cpu: { usage: 45.2, cores: 8 },
                gpu: { usage: 30.1, memory_used: 512, memory_total: 2048 },
                processes: []
            };

            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockData)
            });

            const beforeTime = Date.now();
            await updateMetrics();
            const afterTime = Date.now();

            const lastUpdateText = mockElements.lastUpdate.textContent;
            expect(lastUpdateText).toContain('Última actualización:');
            // Verify timestamp is within reasonable range
            const timestamp = new Date(lastUpdateText.replace('Última actualización: ', '')).getTime();
            expect(timestamp).toBeGreaterThanOrEqual(beforeTime - 1000);
            expect(timestamp).toBeLessThanOrEqual(afterTime + 1000);
        });

        test('should handle missing DOM elements gracefully', async () => {
            document.getElementById.mockReturnValue(null);

            const mockData = {
                ram: { used: 1024, total: 8192, percentage: 12.5 },
                cpu: { usage: 45.2, cores: 8 },
                gpu: { usage: 30.1, memory_used: 512, memory_total: 2048 },
                processes: []
            };

            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockData)
            });

            await expect(updateMetrics()).resolves.not.toThrow();
        });

        test('should handle fetch errors gracefully', async () => {
            fetch.mockRejectedValueOnce(new Error('Network error'));

            await expect(updateMetrics()).resolves.not.toThrow();

            expect(console.error).toHaveBeenCalledWith('Error updating metrics:', expect.any(Error));
        });

        test('should handle invalid data structure', async () => {
            const mockData = {
                ram: null,
                cpu: { usage: 'invalid' },
                gpu: {},
                processes: null
            };

            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockData)
            });

            await expect(updateMetrics()).resolves.not.toThrow();
        });

        test('should dispatch metrics updated event', async () => {
            const mockData = {
                ram: { used: 1024, total: 8192, percentage: 12.5 },
                cpu: { usage: 45.2, cores: 8 },
                gpu: { usage: 30.1, memory_used: 512, memory_total: 2048 },
                processes: []
            };

            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockData)
            });

            await updateMetrics();

            expect(document.dispatchEvent).toHaveBeenCalledWith(
                expect.objectContaining({
                    type: 'metricsUpdated',
                    detail: mockData
                })
            );
        });
    });
});
