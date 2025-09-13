/**
 * Metrics Service
 * Handles communication with backend metrics endpoints
 */

import { api } from '../utils/api.js';
import { Utils } from '../utils/utils.js';

export class MetricsService {
    constructor() {
        this.metrics = {};
        this.intervals = new Map();
        this.listeners = new Map();
        this.isPolling = false;
    }

    /**
     * Initialize the metrics service
     */
    async init() {
        console.log('Initializing Metrics Service...');
        this.startPolling();
    }

    /**
     * Start polling for metrics
     */
    startPolling(interval = 5000) {
        if (this.isPolling) {
            this.stopPolling();
        }

        this.isPolling = true;
        this.updateMetrics();

        const intervalId = setInterval(() => {
            this.updateMetrics();
        }, interval);

        this.intervals.set('metrics', intervalId);
    }

    /**
     * Stop polling for metrics
     */
    stopPolling() {
        this.isPolling = false;
        for (const [key, intervalId] of this.intervals) {
            clearInterval(intervalId);
        }
        this.intervals.clear();
    }

    /**
     * Update metrics from backend
     */
    async updateMetrics() {
        try {
            const data = await api.get('/metrics');
            this.metrics = { ...this.metrics, ...data, lastUpdate: Date.now() };
            this.notifyListeners('metricsUpdated', this.metrics);
        } catch (error) {
            console.error('Failed to update metrics:', error);
            this.notifyListeners('metricsError', error);
        }
    }

    /**
     * Get current metrics
     */
    getMetrics() {
        return { ...this.metrics };
    }

    /**
     * Get specific metric
     */
    getMetric(key) {
        return this.metrics[key];
    }

    /**
     * Format CPU usage
     */
    formatCpuUsage() {
        const cpu = this.getMetric('cpu_percent');
        return cpu !== undefined ? Utils.formatPercentage(cpu) : '--%';
    }

    /**
     * Format memory usage
     */
    formatMemoryUsage() {
        const mem = this.getMetric('memory_percent');
        return mem !== undefined ? Utils.formatPercentage(mem) : '--%';
    }

    /**
     * Format disk usage
     */
    formatDiskUsage() {
        const disk = this.getMetric('disk_percent');
        return disk !== undefined ? Utils.formatPercentage(disk) : '--%';
    }

    /**
     * Get memory details
     */
    getMemoryDetails() {
        const total = this.getMetric('memory_total');
        const used = this.getMetric('memory_used');
        const free = this.getMetric('memory_free');

        return {
            total: total ? Utils.formatBytes(total) : '-- GB',
            used: used ? Utils.formatBytes(used) : '-- GB',
            free: free ? Utils.formatBytes(free) : '-- GB'
        };
    }

    /**
     * Get system uptime
     */
    getUptime() {
        const uptime = this.getMetric('uptime');
        return uptime ? Utils.formatUptime(uptime) : '--:--:--';
    }

    /**
     * Check if metrics are fresh (updated within last 30 seconds)
     */
    isFresh() {
        const lastUpdate = this.getMetric('lastUpdate');
        return lastUpdate && (Date.now() - lastUpdate) < 30000;
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
                    console.error('Error in metrics listener:', error);
                }
            }
        }
    }

    /**
     * Trigger manual metrics update
     */
    async refresh() {
        return this.updateMetrics();
    }

    /**
     * Get metrics history (if available)
     */
    async getHistory(hours = 24) {
        try {
            return await api.get('/metrics/history', { hours });
        } catch (error) {
            console.error('Failed to get metrics history:', error);
            return [];
        }
    }

    /**
     * Export metrics data
     */
    exportData() {
        return {
            timestamp: new Date().toISOString(),
            metrics: this.getMetrics(),
            formatted: {
                cpu: this.formatCpuUsage(),
                memory: this.formatMemoryUsage(),
                disk: this.formatDiskUsage(),
                memoryDetails: this.getMemoryDetails(),
                uptime: this.getUptime()
            }
        };
    }

    /**
     * Cleanup
     */
    destroy() {
        this.stopPolling();
        this.listeners.clear();
    }
}

// Create global instance
export const metricsService = new MetricsService();