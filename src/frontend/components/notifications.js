/**
 * Sistema de notificaciones para el dashboard
 * Proporciona toast notifications y alertas del sistema
 */

// Configuración de notificaciones
const NOTIFICATION_CONFIG = {
    duration: 5000, // 5 segundos por defecto
    position: 'top-right',
    maxNotifications: 5
};

// Contenedor de notificaciones
let notificationContainer = null;

/**
 * Inicializa el sistema de notificaciones
 */
export function initNotifications() {
    if (notificationContainer) {
        return;
    }

    // Crear contenedor
    notificationContainer = document.createElement('div');
    notificationContainer.id = 'notification-container';
    notificationContainer.className = 'notification-container';
    notificationContainer.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        max-width: 400px;
        pointer-events: none;
    `;

    document.body.appendChild(notificationContainer);

    // Agregar estilos CSS
    addNotificationStyles();
}

/**
 * Agrega estilos CSS para las notificaciones
 */
function addNotificationStyles() {
    if (document.getElementById('notification-styles')) {
        return;
    }

    const styles = document.createElement('style');
    styles.id = 'notification-styles';
    styles.textContent = `
        .notification {
            background: rgba(30, 41, 59, 0.95);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            border-left: 4px solid;
            backdrop-filter: blur(10px);
            pointer-events: auto;
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
            color: white;
            position: relative;
            overflow: hidden;
        }

        .notification.show {
            transform: translateX(0);
            opacity: 1;
        }

        .notification.hide {
            transform: translateX(100%);
            opacity: 0;
        }

        .notification.success {
            border-left-color: #10b981;
        }

        .notification.error {
            border-left-color: #ef4444;
        }

        .notification.warning {
            border-left-color: #f59e0b;
        }

        .notification.info {
            border-left-color: #3b82f6;
        }

        .notification-title {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
        }

        .notification-message {
            font-size: 13px;
            line-height: 1.4;
            opacity: 0.9;
        }

        .notification-close {
            position: absolute;
            top: 8px;
            right: 8px;
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.6);
            cursor: pointer;
            font-size: 16px;
            padding: 4px;
            border-radius: 4px;
            transition: all 0.2s ease;
        }

        .notification-close:hover {
            color: white;
            background: rgba(255, 255, 255, 0.1);
        }

        .notification-progress {
            position: absolute;
            bottom: 0;
            left: 0;
            height: 3px;
            background: currentColor;
            border-radius: 0 0 8px 8px;
            opacity: 0.7;
        }

        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;

    document.head.appendChild(styles);
}

/**
 * Crea una notificación
 * @param {string} type - Tipo de notificación (success, error, warning, info)
 * @param {string} title - Título de la notificación
 * @param {string} message - Mensaje de la notificación
 * @param {number} duration - Duración en ms (opcional)
 * @returns {HTMLElement} Elemento de notificación creado
 */
export function createNotification(type, title, message, duration = NOTIFICATION_CONFIG.duration) {
    if (!notificationContainer) {
        initNotifications();
    }

    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-title">${title}</div>
        <div class="notification-message">${message}</div>
        <button class="notification-close" aria-label="Cerrar">&times;</button>
        <div class="notification-progress" style="width: 100%;"></div>
    `;

    // Configurar cierre manual
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        removeNotification(notification);
    });

    // Animación de entrada
    notificationContainer.appendChild(notification);
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Auto-remover después de la duración
    if (duration > 0) {
        const progressBar = notification.querySelector('.notification-progress');
        let startTime = Date.now();

        const updateProgress = () => {
            const elapsed = Date.now() - startTime;
            const remaining = Math.max(0, duration - elapsed);
            const percentage = (remaining / duration) * 100;

            progressBar.style.width = `${percentage}%`;

            if (remaining > 0) {
                requestAnimationFrame(updateProgress);
            }
        };

        updateProgress();

        setTimeout(() => {
            if (notification.parentNode) {
                removeNotification(notification);
            }
        }, duration);
    }

    // Limitar número máximo de notificaciones
    const notifications = notificationContainer.querySelectorAll('.notification');
    if (notifications.length > NOTIFICATION_CONFIG.maxNotifications) {
        removeNotification(notifications[0]);
    }

    return notification;
}

/**
 * Remueve una notificación
 * @param {HTMLElement} notification - Elemento de notificación a remover
 */
export function removeNotification(notification) {
    if (!notification) {
        return;
    }

    notification.classList.add('hide');
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

/**
 * Muestra una notificación de éxito
 * @param {string} title - Título
 * @param {string} message - Mensaje
 * @param {number} duration - Duración opcional
 */
export function showSuccess(title, message, duration) {
    return createNotification('success', title, message, duration);
}

/**
 * Muestra una notificación de error
 * @param {string} title - Título
 * @param {string} message - Mensaje
 * @param {number} duration - Duración opcional
 */
export function showError(title, message, duration) {
    return createNotification('error', title, message, duration);
}

/**
 * Muestra una notificación de advertencia
 * @param {string} title - Título
 * @param {string} message - Mensaje
 * @param {number} duration - Duración opcional
 */
export function showWarning(title, message, duration) {
    return createNotification('warning', title, message, duration);
}

/**
 * Muestra una notificación de información
 * @param {string} title - Título
 * @param {string} message - Mensaje
 * @param {number} duration - Duración opcional
 */
export function showInfo(title, message, duration) {
    return createNotification('info', title, message, duration);
}

/**
 * Limpia todas las notificaciones
 */
export function clearAllNotifications() {
    if (!notificationContainer) {
        return;
    }

    const notifications = notificationContainer.querySelectorAll('.notification');
    notifications.forEach(notification => {
        removeNotification(notification);
    });
}

/**
 * Actualiza la configuración de notificaciones
 * @param {Object} config - Nueva configuración
 */
export function updateNotificationConfig(config) {
    Object.assign(NOTIFICATION_CONFIG, config);
}