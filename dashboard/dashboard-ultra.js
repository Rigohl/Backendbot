<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#0f172a">
    <meta name="description" content="BackendBot Dashboard - Monitoreo y optimización del sistema">
    <title>🚀 BackendBot Dashboard Ultra</title>

    <!-- Preload critical resources -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

    <!-- Modern CSS Framework -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>

    <!-- Chart.js with plugins -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>

    <!-- PWA Manifest -->
    <link rel="manifest" href="manifest.json">

    <style>
        :root {
            --primary: #3b82f6;
            --secondary: #64748b;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --background: #0f172a;
            --surface: #1e293b;
            --text: #f1f5f9;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, var(--background) 0%, #1e293b 100%);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
        }

        .glass {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .metric-card {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1));
            border: 1px solid rgba(59, 130, 246, 0.2);
        }

        .chart-container {
            position: relative;
            height: 300px;
            width: 100%;
        }

        .pulse {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .loading-spinner {
            border: 3px solid rgba(255, 255, 255, 0.1);
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            width: 24px;
            height: 24px;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            padding: 16px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            transform: translateX(400px);
            transition: transform 0.3s ease;
        }

        .notification.show {
            transform: translateX(0);
        }

        .notification.success { background: var(--success); }
        .notification.error { background: var(--error); }
        .notification.warning { background: var(--warning); }

        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(8px);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
        }

        .modal-overlay.show {
            display: flex;
        }

        .modal {
            background: var(--surface);
            border-radius: 16px;
            padding: 24px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }

        .btn {
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
            cursor: pointer;
            border: none;
            font-size: 14px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }

        .btn-primary { background: var(--primary); color: white; }
        .btn-secondary { background: var(--secondary); color: white; }
        .btn-success { background: var(--success); color: white; }
        .btn-warning { background: var(--warning); color: white; }
        .btn-error { background: var(--error); color: white; }

        .input {
            width: 100%;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(30, 41, 59, 0.5);
            color: var(--text);
            font-size: 14px;
        }

        .input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .grid-responsive {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        @media (max-width: 768px) {
            .grid-responsive {
                grid-template-columns: 1fr;
            }
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }

        .status-online { background: var(--success); }
        .status-warning { background: var(--warning); }
        .status-error { background: var(--error); }
    </style>
</head>
<body>
    <!-- Auth Modal -->
    <div id="authModal" class="modal-overlay show">
        <div class="modal glass fade-in">
            <div class="flex items-center mb-6">
                <div class="w-12 h-12 bg-primary rounded-lg flex items-center justify-center mr-4">
                    <i data-lucide="lock" class="w-6 h-6"></i>
                </div>
                <div>
                    <h2 class="text-xl font-bold">Autenticación Requerida</h2>
                    <p class="text-gray-400 text-sm">Ingresa tus credenciales para acceder al dashboard</p>
                </div>
            </div>

            <form id="authForm" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-2">API Key</label>
                    <input id="apiKeyInput" type="password" class="input" placeholder="Ingresa tu API Key" required>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">URL del Backend</label>
                    <input id="backendUrlInput" type="url" class="input" placeholder="http://127.0.0.1:8000" value="http://127.0.0.1:8000" required>
                </div>
                <div class="flex gap-3 pt-4">
                    <button type="submit" class="btn btn-primary flex-1">
                        <i data-lucide="log-in" class="w-4 h-4"></i>
                        Conectar
                    </button>
                    <button type="button" id="loadFromFileBtn" class="btn btn-secondary">
                        <i data-lucide="file" class="w-4 h-4"></i>
                        Cargar Archivo
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Main Content -->
    <div id="mainContent" class="hidden">
        <!-- Header -->
        <header class="glass p-6 mb-6 fade-in">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div>
                    <div class="flex items-center gap-3 mb-2">
                        <div class="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                            <i data-lucide="activity" class="w-6 h-6"></i>
                        </div>
                        <div>
                            <h1 class="text-2xl font-bold">🚀 BackendBot Ultra</h1>
                            <p class="text-gray-400 text-sm">Dashboard de monitoreo avanzado</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-4 text-sm">
                        <span id="connectionStatus" class="flex items-center">
                            <span class="status-indicator status-online"></span>
                            Conectado
                        </span>
                        <span id="lastUpdate">Última actualización: hace unos segundos</span>
                    </div>
                </div>

                <div class="flex items-center gap-3">
                    <button id="themeToggle" class="btn btn-secondary">
                        <i data-lucide="moon" class="w-4 h-4"></i>
                    </button>
                    <button id="refreshBtn" class="btn btn-secondary">
                        <i data-lucide="refresh-cw" class="w-4 h-4"></i>
                    </button>
                    <button id="exportBtn" class="btn btn-primary">
                        <i data-lucide="download" class="w-4 h-4"></i>
                        Exportar
                    </button>
                    <button id="settingsBtn" class="btn btn-secondary">
                        <i data-lucide="settings" class="w-4 h-4"></i>
                    </button>
                </div>
            </div>
        </header>

        <!-- Metrics Grid -->
        <div class="grid-responsive mb-6">
            <!-- System Status -->
            <div class="glass p-6 metric-card fade-in">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold">Estado del Sistema</h3>
                    <i data-lucide="server" class="w-5 h-5 text-primary"></i>
                </div>
                <div class="space-y-3">
                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-400">PID</span>
                        <span id="systemPid" class="font-mono">-</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-400">Uptime</span>
                        <span id="systemUptime">-</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-400">Threads</span>
                        <span id="systemThreads">-</span>
                    </div>
                </div>
            </div>

            <!-- RAM Usage -->
            <div class="glass p-6 fade-in">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold">Memoria RAM</h3>
                    <i data-lucide="memory-stick" class="w-5 h-5 text-green-400"></i>
                </div>
                <div class="text-3xl font-bold mb-2" id="ramUsage">-</div>
                <div class="w-full bg-gray-700 rounded-full h-2 mb-2">
                    <div id="ramProgress" class="bg-green-400 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                </div>
                <div class="text-sm text-gray-400">de <span id="ramTotal">-</span> MB</div>
            </div>

            <!-- CPU Usage -->
            <div class="glass p-6 fade-in">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold">CPU</h3>
                    <i data-lucide="cpu" class="w-5 h-5 text-blue-400"></i>
                </div>
                <div class="text-3xl font-bold mb-2" id="cpuUsage">-</div>
                <div class="w-full bg-gray-700 rounded-full h-2 mb-2">
                    <div id="cpuProgress" class="bg-blue-400 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                </div>
                <div class="text-sm text-gray-400"><span id="cpuCores">-</span> núcleos</div>
            </div>

            <!-- GPU Usage -->
            <div class="glass p-6 fade-in">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold">GPU</h3>
                    <i data-lucide="monitor-speaker" class="w-5 h-5 text-purple-400"></i>
                </div>
                <div class="text-3xl font-bold mb-2" id="gpuUsage">-</div>
                <div class="w-full bg-gray-700 rounded-full h-2 mb-2">
                    <div id="gpuProgress" class="bg-purple-400 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                </div>
                <div class="text-sm text-gray-400">Aceleración gráfica</div>
            </div>
        </div>

        <!-- Charts Section -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <!-- RAM Chart -->
            <div class="glass p-6 fade-in">
                <h3 class="text-lg font-semibold mb-4">Historial de RAM</h3>
                <div class="chart-container">
                    <canvas id="ramChart"></canvas>
                </div>
            </div>

            <!-- CPU Chart -->
            <div class="glass p-6 fade-in">
                <h3 class="text-lg font-semibold mb-4">Historial de CPU</h3>
                <div class="chart-container">
                    <canvas id="cpuChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Processes and History -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <!-- Top Processes -->
            <div class="glass p-6 fade-in">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold">Procesos Activos</h3>
                    <button id="refreshProcessesBtn" class="btn btn-secondary btn-sm">
                        <i data-lucide="refresh-cw" class="w-4 h-4"></i>
                    </button>
                </div>
                <div id="processesList" class="space-y-2 max-h-64 overflow-y-auto">
                    <div class="text-center text-gray-400 py-8">
                        <div class="loading-spinner mx-auto mb-4"></div>
                        Cargando procesos...
                    </div>
                </div>
            </div>

            <!-- Optimization History -->
            <div class="glass p-6 fade-in">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold">Historial de Optimizaciones</h3>
                    <button id="refreshHistoryBtn" class="btn btn-secondary btn-sm">
                        <i data-lucide="refresh-cw" class="w-4 h-4"></i>
                    </button>
                </div>
                <div id="historyList" class="space-y-2 max-h-64 overflow-y-auto">
                    <div class="text-center text-gray-400 py-8">
                        <div class="loading-spinner mx-auto mb-4"></div>
                        Cargando historial...
                    </div>
                </div>
            </div>
        </div>

        <!-- Action Buttons -->
        <div class="glass p-6 fade-in">
            <h3 class="text-lg font-semibold mb-4">Acciones Rápidas</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button id="optimizeBtn" class="btn btn-success">
                    <i data-lucide="zap" class="w-4 h-4"></i>
                    Optimizar RAM
                </button>
                <button id="resetMemoryBtn" class="btn btn-warning">
                    <i data-lucide="rotate-cw" class="w-4 h-4"></i>
                    Reset Memoria
                </button>
                <button id="killProcessBtn" class="btn btn-error">
                    <i data-lucide="x-circle" class="w-4 h-4"></i>
                    Matar Proceso
                </button>
                <button id="systemInfoBtn" class="btn btn-primary">
                    <i data-lucide="info" class="w-4 h-4"></i>
                    Info Sistema
                </button>
            </div>
        </div>
    </div>

    <!-- Notifications -->
    <div id="notifications"></div>

    <!-- Settings Modal -->
    <div id="settingsModal" class="modal-overlay">
        <div class="modal glass">
            <div class="flex items-center justify-between mb-6">
                <h2 class="text-xl font-bold">Configuración</h2>
                <button id="closeSettingsBtn" class="btn btn-secondary btn-sm">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            </div>

            <div class="space-y-6">
                <div>
                    <h3 class="font-semibold mb-3">Actualización Automática</h3>
                    <div class="space-y-2">
                        <label class="flex items-center">
                            <input type="radio" name="updateInterval" value="2000" class="mr-2">
                            <span>Cada 2 segundos</span>
                        </label>
                        <label class="flex items-center">
                            <input type="radio" name="updateInterval" value="5000" checked class="mr-2">
                            <span>Cada 5 segundos</span>
                        </label>
                        <label class="flex items-center">
                            <input type="radio" name="updateInterval" value="10000" class="mr-2">
                            <span>Cada 10 segundos</span>
                        </label>
                    </div>
                </div>

                <div>
                    <h3 class="font-semibold mb-3">Notificaciones</h3>
                    <label class="flex items-center">
                        <input type="checkbox" id="notificationsEnabled" checked class="mr-2">
                        <span>Habilitar notificaciones</span>
                    </label>
                </div>

                <div>
                    <h3 class="font-semibold mb-3">Tema</h3>
                    <div class="flex gap-2">
                        <button id="themeLight" class="btn btn-secondary btn-sm">Claro</button>
                        <button id="themeDark" class="btn btn-secondary btn-sm">Oscuro</button>
                        <button id="themeAuto" class="btn btn-primary btn-sm">Auto</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- PWA Install Prompt -->
    <div id="installPrompt" class="notification" style="display: none;">
        <i data-lucide="download" class="w-5 h-5 mr-2"></i>
        Instalar aplicación
        <button id="installBtn" class="ml-auto btn btn-primary btn-sm">Instalar</button>
        <button id="dismissInstallBtn" class="ml-2 btn btn-secondary btn-sm">×</button>
    </div>

    <script src="dashboard-ultra.js"></script>
</body>
</html></content>
<parameter name="filePath">c:\Users\DELL\Desktop\BackendBot\dashboard\dashboard-ultra.html