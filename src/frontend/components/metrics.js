// metrics.js - Lógica modularizada para métricas del dashboard
export const baseUrl = localStorage.getItem('backendUrl') || 'http://127.0.0.1:8000';
export const apiKey = localStorage.getItem('apiKey') || 'your-super-secret-api-key';
export const headers = { 'X-API-Key': apiKey, 'Content-Type': 'application/json' };

export async function api(path, opts = {}) {
    return fetch(baseUrl + path, { headers, ...opts });
}

export async function loadMetrics() {
    try {
        const res = await api('/self');
        if (res.ok) {
            const data = await res.json();
            const ramMetric = document.getElementById('ramMetric');
            const cpuMetric = document.getElementById('cpuMetric');
            const uptimeMetric = document.getElementById('uptimeMetric');
            if (ramMetric) { ramMetric.textContent = `${data.ram_mb} MB`; }
            if (cpuMetric) { cpuMetric.textContent = `${data.cpu_percent}%`; }
            if (uptimeMetric) { uptimeMetric.textContent = `${Math.floor(data.uptime_sec / 60)}m`; }
        }

        const procRes = await api('/procesos');
        if (procRes.ok) {
            const processes = await procRes.json();
            const processesMetric = document.getElementById('processesMetric');
            if (processesMetric) { processesMetric.textContent = processes.length; }
        }
    } catch (e) {
        console.error('Error loading metrics:', e);
    }
}
// TODO: Migrar lógica de métricas desde dashboard.js aquí
