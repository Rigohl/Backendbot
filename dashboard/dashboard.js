// dashboard.js - Funcionalidad para BackendBot Dashboard
import { loadMetrics, baseUrl, apiKey, headers } from '../src/frontend/components/metrics.js';

let isDarkMode = localStorage.getItem('theme') === 'dark';

document.getElementById('themeToggle').addEventListener('click', () => {
    isDarkMode = !isDarkMode;
    document.body.classList.toggle('dark', isDarkMode);
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    document.getElementById('themeToggle').innerHTML = isDarkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
});

document.getElementById('authBtn').addEventListener('click', async () => {
    const key = document.getElementById('apiKeyInput').value;
    const url = document.getElementById('backendUrlInput').value;
    if (key) {
        localStorage.setItem('apiKey', key);
        localStorage.setItem('backendUrl', url);
        document.getElementById('authModal').classList.remove('show');
        document.getElementById('mainContent').style.display = 'block';
        loadMetrics();
    }
});

document.getElementById('configBtn').addEventListener('click', () => {
    alert('Configuración avanzada próximamente');
});

document.addEventListener('DOMContentLoaded', () => {
    document.body.classList.toggle('dark', isDarkMode);
    if (apiKey && apiKey !== 'your-super-secret-api-key') {
        document.getElementById('authModal').classList.remove('show');
        document.getElementById('mainContent').style.display = 'block';
        loadMetrics();
    }
    setInterval(loadMetrics, 5000);
});

// Funciones avanzadas migradas desde dashboard-ultra.js
export function updateRamMetric(usage, total) {
    const ramUsageEl = document.getElementById('ramUsage');
    const ramTotalEl = document.getElementById('ramTotal');
    const ramProgressEl = document.getElementById('ramProgress');
    ramUsageEl.textContent = usage + ' MB';
    ramTotalEl.textContent = total + ' MB';
    const percent = Math.round((usage / total) * 100);
    ramProgressEl.style.width = percent + '%';
}

export function updateCpuMetric(usage, cores) {
    const cpuUsageEl = document.getElementById('cpuUsage');
    const cpuCoresEl = document.getElementById('cpuCores');
    const cpuProgressEl = document.getElementById('cpuProgress');
    cpuUsageEl.textContent = usage + ' %';
    cpuCoresEl.textContent = cores;
    cpuProgressEl.style.width = usage + '%';
}

export function updateGpuMetric(usage) {
    const gpuUsageEl = document.getElementById('gpuUsage');
    const gpuProgressEl = document.getElementById('gpuProgress');
    gpuUsageEl.textContent = usage + ' %';
    gpuProgressEl.style.width = usage + '%';
}

export function showNotification(type, message) {
    const notif = document.createElement('div');
    notif.className = `notification show ${type}`;
    notif.textContent = message;
    document.body.appendChild(notif);
    setTimeout(() => notif.remove(), 3000);
}

export function updateProcessesList(processes) {
    const listEl = document.getElementById('processesList');
    listEl.innerHTML = '';
    processes.forEach(proc => {
        const item = document.createElement('div');
        item.className = 'flex justify-between items-center py-2 px-3 rounded bg-gray-800 mb-1';
        item.innerHTML = `<span>${proc.name}</span><span class='font-mono text-xs'>PID: ${proc.pid}</span>`;
        listEl.appendChild(item);
    });
}

// Conexión con el endpoint /metrics/ultra
export async function loadUltraMetrics() {
    const url = localStorage.getItem('backendUrl') || 'http://127.0.0.1:8000';
    const key = localStorage.getItem('apiKey');
    try {
        const res = await fetch(`${url}/metrics/ultra`, {
            headers: { 'X-API-Key': key }
        });
        if (!res.ok) throw new Error('Error al obtener métricas ultra');
        const data = await res.json();
        updateRamMetric(data.ram.used, data.ram.total);
        updateCpuMetric(data.cpu.usage, data.cpu.cores);
        updateGpuMetric(data.gpu.usage);
        updateProcessesList(data.processes);
    } catch (e) {
        showNotification('error', e.message);
    }
}

// Llama a loadUltraMetrics cada 5 segundos
setInterval(loadUltraMetrics, 5000);