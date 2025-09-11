/**
 * Módulo para el cambio de tema (oscuro/claro) en el dashboard.
 *
 * @function setupThemeToggle
 * @description Inicializa el botón de cambio de tema, actualiza el DOM y localStorage.
 * @example
 * setupThemeToggle();
 */
export function setupThemeToggle() {
    // Verifica si el botón existe antes de agregar el listener
    let isDarkMode = localStorage.getItem('theme') === 'dark';
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) {
        return;
    }
    // Actualiza el ícono y la clase del body según el estado
    themeToggle.innerHTML = isDarkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    document.body.classList.toggle('dark', isDarkMode);
    themeToggle.addEventListener('click', () => {
        isDarkMode = !isDarkMode;
        document.body.classList.toggle('dark', isDarkMode);
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        themeToggle.innerHTML = isDarkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });
}
