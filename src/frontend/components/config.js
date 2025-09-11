/**
 * Módulo para el modal de configuración avanzada en el dashboard.
 * Permite configurar backend, API keys, temas y métricas.
 */

import { initFormValidation, validateField } from './validation.js';
import { showSuccess, showError, showInfo } from './notifications.js';

// Estado de configuración
let configModal = null;
let currentTab = 'general';

/**
 * Inicializa el modal de configuración
 */
export function setupConfigModal() {
    const configBtn = document.getElementById('configBtn');
    if (!configBtn) {
        return;
    }

    configBtn.addEventListener('click', () => {
        showConfigModal();
    });
}

/**
 * Muestra el modal de configuración
 */
export function showConfigModal() {
    if (configModal) {
        configModal.style.display = 'flex';
        loadCurrentConfig();
        return;
    }

    createConfigModal();
    loadCurrentConfig();
}

/**
 * Crea el modal de configuración
 */
function createConfigModal() {
    configModal = document.createElement('div');
    configModal.id = 'configModal';
    configModal.className = 'config-modal';
    configModal.innerHTML = `
        <div class="config-modal-overlay">
            <div class="config-modal-content">
                <div class="config-modal-header">
                    <h3 class="config-modal-title">⚙️ Configuración Avanzada</h3>
                    <button class="config-modal-close" id="configModalClose">&times;</button>
                </div>

                <div class="config-modal-body">
                    <!-- Pestañas -->
                    <div class="config-tabs">
                        <button class="config-tab active" data-tab="general">General</button>
                        <button class="config-tab" data-tab="backend">Backend</button>
                        <button class="config-tab" data-tab="metrics">Métricas</button>
                        <button class="config-tab" data-tab="theme">Tema</button>
                    </div>

                    <!-- Contenido de pestañas -->
                    <div class="config-tab-content">
                        <!-- Pestaña General -->
                        <div id="tab-general" class="config-tab-pane active">
                            <form id="generalForm" class="config-form">
                                <div class="form-group">
                                    <label for="appTitle">Título de la aplicación</label>
                                    <input type="text" id="appTitle" name="appTitle" placeholder="BackendBot Dashboard">
                                </div>

                                <div class="form-group">
                                    <label for="language">Idioma</label>
                                    <select id="language" name="language">
                                        <option value="es">Español</option>
                                        <option value="en">English</option>
                                        <option value="fr">Français</option>
                                    </select>
                                </div>

                                <div class="form-group">
                                    <label for="autoRefresh">Actualización automática (segundos)</label>
                                    <input type="number" id="autoRefresh" name="autoRefresh" min="5" max="300" value="30">
                                </div>
                            </form>
                        </div>

                        <!-- Pestaña Backend -->
                        <div id="tab-backend" class="config-tab-pane">
                            <form id="backendForm" class="config-form">
                                <div class="form-group">
                                    <label for="backendUrl">URL del Backend</label>
                                    <input type="text" id="backendUrl" name="backendUrl" placeholder="http://127.0.0.1:8000">
                                    <small class="form-help">URL completa del servidor BackendBot</small>
                                </div>

                                <div class="form-group">
                                    <label for="apiKey">API Key</label>
                                    <input type="password" id="apiKey" name="apiKey" placeholder="Ingresa tu API Key">
                                    <small class="form-help">Clave de API para autenticación</small>
                                </div>

                                <div class="form-group">
                                    <label for="timeout">Timeout de conexión (ms)</label>
                                    <input type="number" id="timeout" name="timeout" min="1000" max="30000" value="10000">
                                </div>

                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="sslVerify" name="sslVerify" checked>
                                        Verificar certificados SSL
                                    </label>
                                </div>
                            </form>
                        </div>

                        <!-- Pestaña Métricas -->
                        <div id="tab-metrics" class="config-tab-pane">
                            <form id="metricsForm" class="config-form">
                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="showRam" name="showRam" checked>
                                        Mostrar uso de RAM
                                    </label>
                                </div>

                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="showCpu" name="showCpu" checked>
                                        Mostrar uso de CPU
                                    </label>
                                </div>

                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="showGpu" name="showGpu">
                                        Mostrar uso de GPU
                                    </label>
                                </div>

                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="showProcesses" name="showProcesses" checked>
                                        Mostrar procesos activos
                                    </label>
                                </div>

                                <div class="form-group">
                                    <label for="maxProcesses">Máximo procesos a mostrar</label>
                                    <input type="number" id="maxProcesses" name="maxProcesses" min="5" max="100" value="20">
                                </div>
                            </form>
                        </div>

                        <!-- Pestaña Tema -->
                        <div id="tab-theme" class="config-tab-pane">
                            <form id="themeForm" class="config-form">
                                <div class="form-group">
                                    <label for="themeMode">Modo de tema</label>
                                    <select id="themeMode" name="themeMode">
                                        <option value="auto">Automático</option>
                                        <option value="dark">Oscuro</option>
                                        <option value="light">Claro</option>
                                    </select>
                                </div>

                                <div class="form-group">
                                    <label for="primaryColor">Color primario</label>
                                    <input type="color" id="primaryColor" name="primaryColor" value="#3b82f6">
                                </div>

                                <div class="form-group">
                                    <label for="accentColor">Color de acento</label>
                                    <input type="color" id="accentColor" name="accentColor" value="#10b981">
                                </div>

                                <div class="form-group">
                                    <label class="checkbox-label">
                                        <input type="checkbox" id="animations" name="animations" checked>
                                        Habilitar animaciones
                                    </label>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>

                <div class="config-modal-footer">
                    <button type="button" class="btn btn-secondary" id="configCancel">Cancelar</button>
                    <button type="button" class="btn btn-primary" id="configSave">Guardar Cambios</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(configModal);
    addConfigModalStyles();
    setupConfigModalEvents();
    setupConfigFormValidation();
}

/**
 * Agrega estilos CSS para el modal de configuración
 */
function addConfigModalStyles() {
    if (document.getElementById('config-modal-styles')) {
        return;
    }

    const styles = document.createElement('style');
    styles.id = 'config-modal-styles';
    styles.textContent = `
        .config-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10000;
            backdrop-filter: blur(5px);
        }

        .config-modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .config-modal-overlay {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .config-modal-content {
            background: rgba(30, 41, 59, 0.95);
            border-radius: 12px;
            width: 100%;
            max-width: 800px;
            max-height: 90vh;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .config-modal-header {
            padding: 20px 24px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .config-modal-title {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
            color: white;
        }

        .config-modal-close {
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.6);
            font-size: 24px;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            transition: all 0.2s ease;
        }

        .config-modal-close:hover {
            color: white;
            background: rgba(255, 255, 255, 0.1);
        }

        .config-modal-body {
            padding: 24px;
            max-height: calc(90vh - 140px);
            overflow-y: auto;
        }

        .config-tabs {
            display: flex;
            margin-bottom: 24px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .config-tab {
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.6);
            padding: 12px 16px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s ease;
            font-weight: 500;
        }

        .config-tab:hover {
            color: rgba(255, 255, 255, 0.8);
        }

        .config-tab.active {
            color: #3b82f6;
            border-bottom-color: #3b82f6;
        }

        .config-tab-content {
            min-height: 300px;
        }

        .config-tab-pane {
            display: none;
        }

        .config-tab-pane.active {
            display: block;
        }

        .config-form {
            display: grid;
            gap: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .form-group label {
            font-weight: 500;
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
        }

        .form-group input,
        .form-group select {
            padding: 10px 12px;
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.05);
            color: white;
            font-size: 14px;
            transition: all 0.2s ease;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }

        .form-group input[type="color"] {
            height: 40px;
            cursor: pointer;
        }

        .form-help {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6);
            margin-top: 4px;
        }

        .checkbox-label {
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            font-weight: normal;
        }

        .checkbox-label input[type="checkbox"] {
            width: auto;
            margin: 0;
        }

        .config-modal-footer {
            padding: 20px 24px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }

        .btn {
            padding: 10px 16px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s ease;
            font-size: 14px;
        }

        .btn-primary {
            background: #3b82f6;
            color: white;
        }

        .btn-primary:hover {
            background: #2563eb;
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.8);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        /* Estados de validación */
        .form-group input.valid {
            border-color: #10b981;
        }

        .form-group input.invalid {
            border-color: #ef4444;
        }

        .field-error {
            color: #ef4444;
            font-size: 12px;
            margin-top: 4px;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .config-modal-content {
                margin: 10px;
                max-height: calc(100vh - 20px);
            }

            .config-tabs {
                flex-wrap: wrap;
            }

            .config-tab {
                flex: 1;
                text-align: center;
                padding: 8px 12px;
                font-size: 13px;
            }

            .config-modal-footer {
                flex-direction: column;
            }

            .btn {
                width: 100%;
            }
        }
    `;

    document.head.appendChild(styles);
}

/**
 * Configura los eventos del modal
 */
function setupConfigModalEvents() {
    // Cerrar modal
    const closeBtn = document.getElementById('configModalClose');
    const cancelBtn = document.getElementById('configCancel');

    [closeBtn, cancelBtn].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', () => {
                hideConfigModal();
            });
        }
    });

    // Click fuera del modal
    configModal.addEventListener('click', (e) => {
        if (e.target === configModal) {
            hideConfigModal();
        }
    });

    // Pestañas
    const tabs = configModal.querySelectorAll('.config-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.dataset.tab);
        });
    });

    // Guardar configuración
    const saveBtn = document.getElementById('configSave');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            saveConfiguration();
        });
    }
}

/**
 * Configura validación de formularios
 */
function setupConfigFormValidation() {
    // Validación del formulario de backend
    initFormValidation('backendForm', (data) => {
        // Validar URL
        const urlValidation = validateField('backendUrl', data.backendUrl);
        if (!urlValidation.isValid) {
            showError('Error de validación', urlValidation.message);
            return false;
        }

        // Validar API Key
        const apiKeyValidation = validateField('apiKey', data.apiKey);
        if (!apiKeyValidation.isValid) {
            showError('Error de validación', apiKeyValidation.message);
            return false;
        }

        showSuccess('Configuración guardada', 'Los ajustes de backend se han guardado correctamente.');
        return true;
    });
}

/**
 * Cambia entre pestañas
 * @param {string} tabName - Nombre de la pestaña
 */
function switchTab(tabName) {
    currentTab = tabName;

    // Actualizar pestañas activas
    const tabs = configModal.querySelectorAll('.config-tab');
    tabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });

    // Mostrar contenido de pestaña
    const panes = configModal.querySelectorAll('.config-tab-pane');
    panes.forEach(pane => {
        pane.classList.toggle('active', pane.id === `tab-${tabName}`);
    });
}

/**
 * Carga la configuración actual
 */
function loadCurrentConfig() {
    // Cargar configuración del localStorage
    const config = {
        appTitle: localStorage.getItem('appTitle') || 'BackendBot Dashboard',
        language: localStorage.getItem('language') || 'es',
        autoRefresh: localStorage.getItem('autoRefresh') || '30',
        backendUrl: localStorage.getItem('backendUrl') || 'http://127.0.0.1:8000',
        apiKey: localStorage.getItem('apiKey') || '',
        timeout: localStorage.getItem('timeout') || '10000',
        sslVerify: localStorage.getItem('sslVerify') !== 'false',
        showRam: localStorage.getItem('showRam') !== 'false',
        showCpu: localStorage.getItem('showCpu') !== 'false',
        showGpu: localStorage.getItem('showGpu') === 'true',
        showProcesses: localStorage.getItem('showProcesses') !== 'false',
        maxProcesses: localStorage.getItem('maxProcesses') || '20',
        themeMode: localStorage.getItem('themeMode') || 'auto',
        primaryColor: localStorage.getItem('primaryColor') || '#3b82f6',
        accentColor: localStorage.getItem('accentColor') || '#10b981',
        animations: localStorage.getItem('animations') !== 'false'
    };

    // Aplicar valores a los campos
    Object.keys(config).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = config[key];
            } else {
                element.value = config[key];
            }
        }
    });
}

/**
 * Guarda la configuración
 */
function saveConfiguration() {
    try {
        // Recopilar datos de todos los formularios
        const forms = ['generalForm', 'backendForm', 'metricsForm', 'themeForm'];
        const config = {};

        forms.forEach(formId => {
            const form = document.getElementById(formId);
            if (form) {
                const formData = new FormData(form);
                formData.forEach((value, key) => {
                    config[key] = value;
                });
            }
        });

        // Guardar en localStorage
        Object.keys(config).forEach(key => {
            localStorage.setItem(key, config[key]);
        });

        // Aplicar configuración inmediatamente
        applyConfiguration(config);

        showSuccess('Configuración guardada', 'Todos los cambios han sido aplicados correctamente.');
        hideConfigModal();

    } catch (error) {
        console.error('Error guardando configuración:', error);
        showError('Error', 'No se pudo guardar la configuración. Inténtalo de nuevo.');
    }
}

/**
 * Aplica la configuración al sistema
 * @param {Object} config - Configuración a aplicar
 */
function applyConfiguration(config) {
    // Aplicar tema
    if (config.themeMode) {
        document.documentElement.setAttribute('data-theme', config.themeMode);
    }

    // Aplicar colores
    if (config.primaryColor) {
        document.documentElement.style.setProperty('--primary-color', config.primaryColor);
    }

    if (config.accentColor) {
        document.documentElement.style.setProperty('--accent-color', config.accentColor);
    }

    // Aplicar animaciones
    if (config.animations === 'false') {
        document.documentElement.style.setProperty('--animation-duration', '0s');
    } else {
        document.documentElement.style.setProperty('--animation-duration', '0.3s');
    }

    // Notificar a otros componentes
    const event = new CustomEvent('configChanged', { detail: config });
    document.dispatchEvent(event);
}

/**
 * Oculta el modal de configuración
 */
function hideConfigModal() {
    if (configModal) {
        configModal.style.display = 'none';
    }
}

/**
 * Obtiene la configuración actual
 * @returns {Object} Configuración actual
 */
export function getCurrentConfig() {
    return {
        appTitle: localStorage.getItem('appTitle') || 'BackendBot Dashboard',
        language: localStorage.getItem('language') || 'es',
        autoRefresh: parseInt(localStorage.getItem('autoRefresh') || '30'),
        backendUrl: localStorage.getItem('backendUrl') || 'http://127.0.0.1:8000',
        apiKey: localStorage.getItem('apiKey') || '',
        timeout: parseInt(localStorage.getItem('timeout') || '10000'),
        sslVerify: localStorage.getItem('sslVerify') !== 'false',
        showRam: localStorage.getItem('showRam') !== 'false',
        showCpu: localStorage.getItem('showCpu') !== 'false',
        showGpu: localStorage.getItem('showGpu') === 'true',
        showProcesses: localStorage.getItem('showProcesses') !== 'false',
        maxProcesses: parseInt(localStorage.getItem('maxProcesses') || '20'),
        themeMode: localStorage.getItem('themeMode') || 'auto',
        primaryColor: localStorage.getItem('primaryColor') || '#3b82f6',
        accentColor: localStorage.getItem('accentColor') || '#10b981',
        animations: localStorage.getItem('animations') !== 'false'
    };
}
