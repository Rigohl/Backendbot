/**
 * Módulo para el modal de autenticación en el dashboard.
 * Permite testeo y buenas prácticas.
 */
export async function setupAuthModal(loadMetrics) {
    const authBtn = document.getElementById('authBtn');
    const authModal = document.getElementById('authModal');
    const mainContent = document.getElementById('mainContent');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const backendUrlInput = document.getElementById('backendUrlInput');

    if (!authBtn || !authModal || !mainContent) {
        return;
    }

    // Intentar obtener credenciales del backend primero
    const backendUrl = localStorage.getItem('backendUrl') || 'http://127.0.0.1:8000';
    try {
        const response = await fetch(`${backendUrl}/get-api-key`);
        if (response.ok) {
            const data = await response.json();
            if (data.api_key && data.api_key !== "default-api-key") {
                // API_KEY encontrada en .env, usar automáticamente
                localStorage.setItem('apiKey', data.api_key);
                localStorage.setItem('backendUrl', backendUrl);
                authModal.classList.remove('show');
                mainContent.style.display = 'block';
                if (typeof loadMetrics === 'function') {
                    loadMetrics();
                }
                return; // No mostrar modal
            }
            // Si hay usuario/contraseña configurados, mostrar modal con campos adicionales
            if (data.username && data.password) {
                const usernameSection = document.getElementById('usernameSection');
                const passwordSection = document.getElementById('passwordSection');
                if (usernameSection) {
                    usernameSection.style.display = 'block';
                }
                if (passwordSection) {
                    passwordSection.style.display = 'block';
                }
                if (apiKeyInput) {
                    apiKeyInput.placeholder = 'O usa API Key directamente';
                }
            }
        }
    } catch (error) {
        console.log('No se pudo obtener credenciales del backend, mostrando modal de autenticación');
    }

    // Si no se encontró API_KEY en .env, mostrar modal
    authBtn.addEventListener('click', async () => {
        const key = apiKeyInput.value;
        const username = document.getElementById('usernameInput')?.value;
        const password = document.getElementById('passwordInput')?.value;
        const url = backendUrlInput.value;

        // Si se proporciona API_KEY, usarla directamente
        if (key) {
            localStorage.setItem('apiKey', key);
            localStorage.setItem('backendUrl', url);
            authModal.classList.remove('show');
            mainContent.style.display = 'block';
            if (typeof loadMetrics === 'function') {
                loadMetrics();
            }
            return;
        }

        // Si se proporcionan usuario y contraseña, intentar autenticación
        if (username && password) {
            try {
                const response = await fetch(`${url}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('apiKey', data.api_key);
                    localStorage.setItem('backendUrl', url);
                    authModal.classList.remove('show');
                    mainContent.style.display = 'block';
                    if (typeof loadMetrics === 'function') {
                        loadMetrics();
                    }
                } else {
                    alert('Credenciales incorrectas');
                }
            } catch (error) {
                alert('Error de conexión: ' + error.message);
            }
            return;
        }

        // Si no se proporcionó nada
        alert('Por favor ingresa API Key o credenciales de usuario');
    });
}
