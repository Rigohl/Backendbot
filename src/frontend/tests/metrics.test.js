import { loadMetrics } from '../components/metrics.js';

describe('loadMetrics', () => {
    it('should update metric elements if present', async () => {
        document.body.innerHTML = `
			<span id="ramMetric"></span>
			<span id="cpuMetric"></span>
			<span id="uptimeMetric"></span>
			<span id="processesMetric"></span>
		`;
        // Mock fetch and API responses
        global.fetch = jest.fn()
            .mockResolvedValueOnce({ ok: true, json: async () => ({ ram_mb: 123, cpu_percent: 45, uptime_sec: 600 }) })
            .mockResolvedValueOnce({ ok: true, json: async () => ([{}, {}, {}]) });
        await loadMetrics();
        expect(document.getElementById('ramMetric').textContent).toBe('123 MB');
        expect(document.getElementById('cpuMetric').textContent).toBe('45%');
        expect(document.getElementById('uptimeMetric').textContent).toBe('10m');
        expect(document.getElementById('processesMetric').textContent).toBe('3');
    });
});
