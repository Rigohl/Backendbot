export async function loadUltraMetrics() {
    // Ejemplo de migración: cargar métricas del backend y actualizar UI
    const baseUrl = localStorage.getItem('backendUrl') || 'http://127.0.0.1:8000';
    const apiKey = localStorage.getItem('apiKey') || '';
    const headers = { 'X-API-Key': apiKey, 'Content-Type': 'application/json' };

    async function api(path, opts = {}) {
        return fetch(baseUrl + path, { headers, ...opts });
    }

    try {
        // Cargar estado del sistema
        const res = await api('/self');
        if (res.ok) {
            const data = await res.json();
            if (document.getElementById('systemPid')) { document.getElementById('systemPid').textContent = data.pid; }
            if (document.getElementById('systemUptime')) { document.getElementById('systemUptime').textContent = `${Math.floor(data.uptime_sec/60)}m ${Math.round(data.uptime_sec%60)}s`; }
            if (document.getElementById('systemThreads')) { document.getElementById('systemThreads').textContent = data.num_threads; }
            if (document.getElementById('ramUsage')) { document.getElementById('ramUsage').textContent = `${data.ram_mb} MB`; }
            if (document.getElementById('ramTotal')) { document.getElementById('ramTotal').textContent = data.ram_total_mb; }
            if (document.getElementById('ramProgress')) { document.getElementById('ramProgress').style.width = `${Math.round((data.ram_mb/data.ram_total_mb)*100)}%`; }
            if (document.getElementById('cpuUsage')) { document.getElementById('cpuUsage').textContent = `${data.cpu_percent} %`; }
            if (document.getElementById('cpuCores')) { document.getElementById('cpuCores').textContent = data.cpu_cores; }
            if (document.getElementById('cpuProgress')) { document.getElementById('cpuProgress').style.width = `${data.cpu_percent}%`; }
            if (document.getElementById('gpuUsage')) { document.getElementById('gpuUsage').textContent = `${data.gpu_percent} %`; }
            if (document.getElementById('gpuProgress')) { document.getElementById('gpuProgress').style.width = `${data.gpu_percent}%`; }
        }

        // Cargar procesos activos
        const procRes = await api('/procesos');
        if (procRes.ok) {
            const processes = await procRes.json();
            const list = document.getElementById('processesList');
            if (list) {
                list.innerHTML = processes.slice(0, 20).map(p => `<div class="flex justify-between"><span>${p.pid} - ${p.name}</span><span>${p.ram_mb} MB</span></div>`).join('');
            }
        }

        // Cargar historial de optimizaciones
        const histRes = await api('/history/optimizations?limit=10');
        if (histRes.ok) {
            const history = await histRes.json();
            const hlist = document.getElementById('historyList');
            if (hlist) {
                hlist.innerHTML = history.slice(-10).reverse().map(ev => `<div>${new Date(ev.timestamp).toLocaleString()} — ${ev.ram_freed_mb} MB liberados</div>`).join('');
            }
        }
    } catch (e) {
        console.error('Error cargando métricas ultra:', e);
    }
}

export function setupUltraUI() {
    // Inicializar eventos principales del dashboard ultra
    if (document.getElementById('themeToggle')) {
        document.getElementById('themeToggle').addEventListener('click', () => {
            document.body.classList.toggle('dark');
        });
    }
    if (document.getElementById('refreshBtn')) {
        document.getElementById('refreshBtn').addEventListener('click', () => {
            loadUltraMetrics();
        });
    }
    if (document.getElementById('optimizeBtn')) {
        document.getElementById('optimizeBtn').addEventListener('click', async () => {
            // Llamar API para optimizar RAM
            const baseUrl = localStorage.getItem('backendUrl') || 'http://127.0.0.1:8000';
            const apiKey = localStorage.getItem('apiKey') || '';
            const headers = { 'X-API-Key': apiKey, 'Content-Type': 'application/json' };
            try {
                const res = await fetch(baseUrl + '/optimize', { method: 'POST', headers });
                if (res.ok) { alert('Optimización solicitada'); } else { alert('Fallo optimización'); }
            } catch (e) { alert('Error de red'); }
        });
    }
    if (document.getElementById('resetMemoryBtn')) {
        document.getElementById('resetMemoryBtn').addEventListener('click', async () => {
            const baseUrl = localStorage.getItem('backendUrl') || 'http://127.0.0.1:8000';
            const apiKey = localStorage.getItem('apiKey') || '';
            const headers = { 'X-API-Key': apiKey, 'Content-Type': 'application/json' };
            try {
                const res = await fetch(baseUrl + '/reset-memoria', { method: 'POST', headers });
                if (res.ok) { alert('Memoria reseteada'); } else { alert('Fallo'); }
            } catch (e) { alert('Error de red'); }
        });
    }
    // Puedes seguir agregando eventos para otros botones/modales
}
