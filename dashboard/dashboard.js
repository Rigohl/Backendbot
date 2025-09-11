// dashboard.js - Funcionalidad para BackendBot Dashboard

const baseUrl = localStorage.getItem('backendUrl') || 'http://127.0.0.1:8000';
const apiKey = localStorage.getItem('apiKey') || 'your-super-secret-api-key';
const headers = { 'X-API-Key': apiKey, 'Content-Type': 'application/json' };

let isDarkMode = localStorage.getItem('theme') === 'dark';

// Tema toggle
document.getElementById('themeToggle').addEventListener('click', () => {
    isDarkMode = !isDarkMode;
    document.body.classList.toggle('dark', isDarkMode);
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    document.getElementById('themeToggle').innerHTML = isDarkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
});

// Autenticación
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

// API helper
async function api(path, opts = {}) {
    return fetch(baseUrl + path, { headers, ...opts });
}

// Cargar métricas
async function loadMetrics() {
    try {
        const res = await api('/self');
        if (res.ok) {
            const data = await res.json();
            document.getElementById('ramMetric').textContent = `${data.ram_mb} MB`;
            document.getElementById('cpuMetric').textContent = `${data.cpu_percent}%`;
            document.getElementById('uptimeMetric').textContent = `${Math.floor(data.uptime_sec / 60)}m`;
        }

        const procRes = await api('/procesos');
        if (procRes.ok) {
            const processes = await procRes.json();
            document.getElementById('processesMetric').textContent = processes.length;
        }
    } catch (e) {
        console.error('Error loading metrics:', e);
    }
}

// Config modal
document.getElementById('configBtn').addEventListener('click', () => {
    // Mostrar modal de configuración
    alert('Configuración avanzada próximamente');
});

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    document.body.classList.toggle('dark', isDarkMode);
    if (apiKey && apiKey !== 'your-super-secret-api-key') {
        document.getElementById('authModal').classList.remove('show');
        document.getElementById('mainContent').style.display = 'block';
        loadMetrics();
    }
    setInterval(loadMetrics, 5000); // Actualizar cada 5s
});