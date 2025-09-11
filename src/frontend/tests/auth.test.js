/** @jest-environment jsdom */
import { setupAuthModal } from '../components/auth.js';
describe('setupAuthModal', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <button id="authBtn"></button>
            <input id="apiKeyInput" value="testkey" />
            <input id="backendUrlInput" value="http://test" />
            <div id="authModal" class="show"></div>
            <div id="mainContent" style="display:none"></div>
        `;
        localStorage.clear();
    });
    test('guarda credenciales y muestra dashboard', () => {
        let called = false;
        setupAuthModal(() => { called = true; });
        document.getElementById('authBtn').click();
        expect(localStorage.getItem('apiKey')).toBe('testkey');
        expect(localStorage.getItem('backendUrl')).toBe('http://test');
        expect(document.getElementById('authModal').classList.contains('show')).toBe(false);
        expect(document.getElementById('mainContent').style.display).toBe('block');
        expect(called).toBe(true);
    });
});
