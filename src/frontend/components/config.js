/**
 * Módulo para el modal/configuración avanzada en el dashboard.
 * Permite testeo y buenas prácticas.
 */
export function setupConfigModal() {
    const configBtn = document.getElementById('configBtn');
    if (!configBtn) return;
    configBtn.addEventListener('click', () => {
        alert('Configuración avanzada próximamente');
    });
}
