import { loadUltraMetrics, setupUltraUI } from '../components/ultra.js';

describe('Dashboard Ultra', () => {
  it('should have loadUltraMetrics and setupUltraUI as functions', () => {
    expect(typeof loadUltraMetrics).toBe('function');
    expect(typeof setupUltraUI).toBe('function');
  });

  it('should setup UI and bind events without errors', () => {
    document.body.innerHTML = `
      <button id="themeToggle"></button>
      <button id="refreshBtn"></button>
      <button id="optimizeBtn"></button>
      <button id="resetMemoryBtn"></button>
      <div id="mainContent"></div>
    `;
    expect(() => setupUltraUI()).not.toThrow();
  });

  it('should call loadUltraMetrics and update metrics', async () => {
    document.body.innerHTML = `
      <span id="systemPid"></span>
      <span id="systemUptime"></span>
      <span id="systemThreads"></span>
      <span id="ramUsage"></span>
      <span id="ramTotal"></span>
      <div id="ramProgress"></div>
      <span id="cpuUsage"></span>
      <span id="cpuCores"></span>
      <div id="cpuProgress"></div>
      <span id="gpuUsage"></span>
      <div id="gpuProgress"></div>
      <div id="processesList"></div>
      <div id="historyList"></div>
    `;
    // Mock fetch for /self, /procesos, /history/optimizations
    global.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({ pid: 1, uptime_sec: 600, num_threads: 5, ram_mb: 1000, ram_total_mb: 2000, cpu_percent: 50, cpu_cores: 4, gpu_percent: 20 }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ([{ pid: 1, name: 'python', ram_mb: 500 }, { pid: 2, name: 'uvicorn', ram_mb: 300 }]) })
      .mockResolvedValueOnce({ ok: true, json: async () => ([{ timestamp: Date.now(), ram_freed_mb: 100 }]) });
    await loadUltraMetrics();
    expect(document.getElementById('systemPid').textContent).toBe('1');
    expect(document.getElementById('ramUsage').textContent).toBe('1000 MB');
    expect(document.getElementById('cpuUsage').textContent).toBe('50 %');
    expect(document.getElementById('gpuUsage').textContent).toBe('20 %');
    expect(document.getElementById('processesList').innerHTML).toContain('python');
    expect(document.getElementById('historyList').innerHTML).toContain('MB liberados');
  });
});
