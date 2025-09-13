// BackendBot Dashboard JavaScript
class BackendBotDashboard {
    constructor() {
        this.backendUrl = localStorage.getItem('backendUrl') || 'http://127.0.0.1:8000';
        this.apiKey = localStorage.getItem('apiKey') || '';
        this.autoRefresh = localStorage.getItem('autoRefresh') !== 'false';
        this.notifications = localStorage.getItem('notifications') !== 'false';
        this.refreshInterval = null;
        this.charts = {};

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSettings();
        this.checkConnection();
        this.startAutoRefresh();
        this.initializeCharts();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Header controls
        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshData());
        document.getElementById('settingsBtn').addEventListener('click', () => this.showSettingsModal());

        // Control panel buttons
        document.getElementById('optimizeBtn').addEventListener('click', () => this.optimizeMemory());
        document.getElementById('clearCacheBtn').addEventListener('click', () => this.clearCache());
        document.getElementById('restartBtn').addEventListener('click', () => this.restartServices());
        document.getElementById('shutdownBtn').addEventListener('click', () => this.shutdownSystem());

        // Process monitor
        document.getElementById('processSearch').addEventListener('input', (e) => this.filterProcesses(e.target.value));
        document.getElementById('sortBy').addEventListener('change', (e) => this.sortProcesses(e.target.value));

        // Logs
        document.getElementById('logLevel').addEventListener('change', (e) => this.filterLogs(e.target.value));
        document.getElementById('clearLogsBtn').addEventListener('click', () => this.clearLogs());

        // Settings modal
        document.getElementById('settingsClose').addEventListener('click', () => this.hideSettingsModal());
        document.getElementById('settingsCancel').addEventListener('click', () => this.hideSettingsModal());
        document.getElementById('settingsSave').addEventListener('click', () => this.saveSettings());

        // Close modal on outside click
        document.getElementById('settingsModal').addEventListener('click', (e) => {
            if (e.target.id === 'settingsModal') {
                this.hideSettingsModal();
            }
        });
    }

    loadSettings() {
        document.getElementById('autoRefresh').checked = this.autoRefresh;
        document.getElementById('notifications').checked = this.notifications;
        document.getElementById('backendUrl').value = this.backendUrl;
        document.getElementById('apiKey').value = this.apiKey;
    }

    async checkConnection() {
        const statusEl = document.getElementById('connectionStatus');
        try {
            const response = await fetch(`${this.backendUrl}/health`, {
                headers: { 'X-API-Key': this.apiKey },
                signal: AbortSignal.timeout(5000)
            });

            if (response.ok) {
                statusEl.className = 'connection-status connected';
                statusEl.querySelector('span').textContent = 'Conectado';
            } else {
                throw new Error('Respuesta no válida');
            }
        } catch (error) {
            statusEl.className = 'connection-status disconnected';
            statusEl.querySelector('span').textContent = 'Desconectado';
            this.showNotification('error', 'No se pudo conectar al backend');
        }
    }

    startAutoRefresh() {
        if (this.autoRefresh) {
            this.refreshInterval = setInterval(() => {
                this.refreshData();
            }, 5000);
        }
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    initializeCharts() {
        const cpuCtx = document.getElementById('cpuChart').getContext('2d');
        const memoryCtx = document.getElementById('memoryChart').getContext('2d');

        this.charts.cpu = new Chart(cpuCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Uso de CPU (%)',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        this.charts.memory = new Chart(memoryCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Uso de Memoria (%)',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    async loadInitialData() {
        await this.refreshData();
        await this.loadProcesses();
        await this.loadLogs();
    }

    async refreshData() {
        try {
            const response = await fetch(`${this.backendUrl}/metrics`, {
                headers: { 'X-API-Key': this.apiKey }
            });

            if (!response.ok) {
                throw new Error('Error al obtener métricas');
            }

            const data = await response.json();
            this.updateMetrics(data);
            this.updateCharts(data);
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showNotification('error', 'Error al actualizar datos');
        }
    }

    updateMetrics(data) {
        // RAM
        const ramUsage = data.ram?.used || 0;
        const ramTotal = data.ram?.total || 1;
        const ramPercent = (ramUsage / ramTotal) * 100;

        document.getElementById('ramUsage').textContent = `${ramPercent.toFixed(1)}%`;
        document.getElementById('ramProgress').style.width = `${ramPercent}%`;
        document.getElementById('ramTotal').textContent = `${(ramTotal / 1024).toFixed(1)}`;
        document.getElementById('ramAvailable').textContent = `${((ramTotal - ramUsage) / 1024).toFixed(1)}`;

        // CPU
        const cpuUsage = data.cpu?.usage || 0;
        document.getElementById('cpuUsage').textContent = `${cpuUsage.toFixed(1)}%`;
        document.getElementById('cpuProgress').style.width = `${cpuUsage}%`;
        document.getElementById('cpuCores').textContent = data.cpu?.cores || '--';

        // Disk
        const diskUsage = data.disk?.used || 0;
        const diskTotal = data.disk?.total || 1;
        const diskPercent = (diskUsage / diskTotal) * 100;

        document.getElementById('diskUsage').textContent = `${diskPercent.toFixed(1)}%`;
        document.getElementById('diskProgress').style.width = `${diskPercent}%`;
        document.getElementById('diskTotal').textContent = `${(diskTotal / (1024 ** 3)).toFixed(1)}`;
        document.getElementById('diskFree').textContent = `${((diskTotal - diskUsage) / (1024 ** 3)).toFixed(1)}`;

        // Network
        document.getElementById('networkUsage').textContent = '--';
        document.getElementById('networkDown').textContent = '--';
        document.getElementById('networkUp').textContent = '--';
    }

    updateCharts(data) {
        const now = new Date().toLocaleTimeString();

        // CPU Chart
        this.charts.cpu.data.labels.push(now);
        this.charts.cpu.data.datasets[0].data.push(data.cpu?.usage || 0);

        if (this.charts.cpu.data.labels.length > 12) {
            this.charts.cpu.data.labels.shift();
            this.charts.cpu.data.datasets[0].data.shift();
        }

        this.charts.cpu.update();

        // Memory Chart
        const memoryPercent = data.ram ? (data.ram.used / data.ram.total) * 100 : 0;
        this.charts.memory.data.labels.push(now);
        this.charts.memory.data.datasets[0].data.push(memoryPercent);

        if (this.charts.memory.data.labels.length > 12) {
            this.charts.memory.data.labels.shift();
            this.charts.memory.data.datasets[0].data.shift();
        }

        this.charts.memory.update();
    }

    async loadProcesses() {
        try {
            const response = await fetch(`${this.backendUrl}/processes`, {
                headers: { 'X-API-Key': this.apiKey }
            });

            if (!response.ok) {
                throw new Error('Error al obtener procesos');
            }

            const data = await response.json();
            this.displayProcesses(data.processes || []);
        } catch (error) {
            console.error('Error loading processes:', error);
            this.showNotification('error', 'Error al cargar procesos');
        }
    }

    displayProcesses(processes) {
        const tbody = document.getElementById('processTableBody');
        tbody.innerHTML = '';

        if (processes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading-row">No hay procesos para mostrar</td></tr>';
            return;
        }

        processes.forEach(process => {
            const row = document.createElement('tr');

            const memoryMB = process.memory ? (process.memory / (1024 * 1024)).toFixed(1) : '--';

            row.innerHTML = `
                <td>${process.pid}</td>
                <td>${process.name}</td>
                <td>${process.cpu?.toFixed(1) || '--'}%</td>
                <td>${memoryMB} MB</td>
                <td><span class="process-status status-${process.status || 'running'}">${process.status || 'running'}</span></td>
                <td>
                    <button class="process-action kill" onclick="dashboard.killProcess(${process.pid})">
                        <i class="fas fa-times"></i>
                    </button>
                    <button class="process-action suspend" onclick="dashboard.suspendProcess(${process.pid})">
                        <i class="fas fa-pause"></i>
                    </button>
                </td>
            `;

            tbody.appendChild(row);
        });
    }

    filterProcesses(searchTerm) {
        const rows = document.querySelectorAll('#processTableBody tr');
        rows.forEach(row => {
            const name = row.cells[1].textContent.toLowerCase();
            row.style.display = name.includes(searchTerm.toLowerCase()) ? '' : 'none';
        });
    }

    sortProcesses(criteria) {
        // This would require storing the process data and re-sorting
        // For now, just refresh the data
        this.loadProcesses();
    }

    async loadLogs() {
        try {
            const response = await fetch(`${this.backendUrl}/logs`, {
                headers: { 'X-API-Key': this.apiKey }
            });

            if (!response.ok) {
                throw new Error('Error al obtener logs');
            }

            const data = await response.json();
            this.displayLogs(data.logs || []);
        } catch (error) {
            console.error('Error loading logs:', error);
            this.showNotification('error', 'Error al cargar logs');
        }
    }

    displayLogs(logs) {
        const container = document.getElementById('logsContainer');
        container.innerHTML = '';

        if (logs.length === 0) {
            container.innerHTML = '<div class="log-entry">No hay logs disponibles</div>';
            return;
        }

        logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${log.level || 'info'}`;
            logEntry.textContent = `[${log.timestamp}] ${log.level?.toUpperCase()}: ${log.message}`;
            container.appendChild(logEntry);
        });

        container.scrollTop = container.scrollHeight;
    }

    filterLogs(level) {
        const entries = document.querySelectorAll('.log-entry');
        entries.forEach(entry => {
            if (level === 'all' || entry.classList.contains(level)) {
                entry.style.display = '';
            } else {
                entry.style.display = 'none';
            }
        });
    }

    async optimizeMemory() {
        try {
            const response = await fetch(`${this.backendUrl}/optimize/memory`, {
                method: 'POST',
                headers: { 'X-API-Key': this.apiKey }
            });

            if (!response.ok) {
                throw new Error('Error al optimizar memoria');
            }

            this.showNotification('success', 'Memoria optimizada exitosamente');
            setTimeout(() => this.refreshData(), 1000);
        } catch (error) {
            this.showNotification('error', 'Error al optimizar memoria');
        }
    }

    async clearCache() {
        try {
            const response = await fetch(`${this.backendUrl}/optimize/cache`, {
                method: 'POST',
                headers: { 'X-API-Key': this.apiKey }
            });

            if (!response.ok) {
                throw new Error('Error al limpiar cache');
            }

            this.showNotification('success', 'Cache limpiado exitosamente');
        } catch (error) {
            this.showNotification('error', 'Error al limpiar cache');
        }
    }

    async restartServices() {
        if (!confirm('¿Estás seguro de que quieres reiniciar los servicios?')) {
            return;
        }

        try {
            const response = await fetch(`${this.backendUrl}/system/restart`, {
                method: 'POST',
                headers: { 'X-API-Key': this.apiKey }
            });

            if (!response.ok) {
                throw new Error('Error al reiniciar servicios');
            }

            this.showNotification('success', 'Servicios reiniciados exitosamente');
        } catch (error) {
            this.showNotification('error', 'Error al reiniciar servicios');
        }
    }

    async shutdownSystem() {
        if (!confirm('¿Estás seguro de que quieres apagar el sistema?')) {
            return;
        }

        try {
            const response = await fetch(`${this.backendUrl}/system/shutdown`, {
                method: 'POST',
                headers: { 'X-API-Key': this.apiKey }
            });

            if (!response.ok) {
                throw new Error('Error al apagar sistema');
            }

            this.showNotification('warning', 'Sistema apagándose...');
        } catch (error) {
            this.showNotification('error', 'Error al apagar sistema');
        }
    }

    async killProcess(pid) {
        if (!confirm(`¿Estás seguro de que quieres terminar el proceso ${pid}?`)) {
            return;
        }

        try {
            const response = await fetch(`${this.backendUrl}/processes/${pid}`, {
                method: 'DELETE',
                headers: { 'X-API-Key': this.apiKey }
            });

            if (!response.ok) {
                throw new Error('Error al terminar proceso');
            }

            this.showNotification('success', `Proceso ${pid} terminado`);
            setTimeout(() => this.loadProcesses(), 1000);
        } catch (error) {
            this.showNotification('error', 'Error al terminar proceso');
        }
    }

    async suspendProcess(pid) {
        try {
            const response = await fetch(`${this.backendUrl}/processes/${pid}/suspend`, {
                method: 'POST',
                headers: { 'X-API-Key': this.apiKey }
            });

            if (!response.ok) {
                throw new Error('Error al suspender proceso');
            }

            this.showNotification('success', `Proceso ${pid} suspendido`);
            setTimeout(() => this.loadProcesses(), 1000);
        } catch (error) {
            this.showNotification('error', 'Error al suspender proceso');
        }
    }

    async clearLogs() {
        try {
            const response = await fetch(`${this.backendUrl}/logs`, {
                method: 'DELETE',
                headers: { 'X-API-Key': this.apiKey }
            });

            if (!response.ok) {
                throw new Error('Error al limpiar logs');
            }

            this.showNotification('success', 'Logs limpiados exitosamente');
            this.loadLogs();
        } catch (error) {
            this.showNotification('error', 'Error al limpiar logs');
        }
    }

    showSettingsModal() {
        document.getElementById('settingsModal').classList.add('show');
    }

    hideSettingsModal() {
        document.getElementById('settingsModal').classList.remove('show');
    }

    saveSettings() {
        this.autoRefresh = document.getElementById('autoRefresh').checked;
        this.notifications = document.getElementById('notifications').checked;
        this.backendUrl = document.getElementById('backendUrl').value;
        this.apiKey = document.getElementById('apiKey').value;

        localStorage.setItem('autoRefresh', this.autoRefresh);
        localStorage.setItem('notifications', this.notifications);
        localStorage.setItem('backendUrl', this.backendUrl);
        localStorage.setItem('apiKey', this.apiKey);

        if (this.autoRefresh) {
            this.startAutoRefresh();
        } else {
            this.stopAutoRefresh();
        }

        this.checkConnection();
        this.hideSettingsModal();
        this.showNotification('success', 'Configuración guardada');
    }

    showNotification(type, message, title = '') {
        if (!this.notifications && type !== 'error') {
            return;
        }

        const notificationsEl = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;

        const iconClass = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        }[type] || 'fa-info-circle';

        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas ${iconClass}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${title || type.charAt(0).toUpperCase() + type.slice(1)}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        notificationsEl.appendChild(notification);

        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// Initialize dashboard when DOM is loaded
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new BackendBotDashboard();
});

// Make dashboard globally available for onclick handlers
window.dashboard = dashboard;