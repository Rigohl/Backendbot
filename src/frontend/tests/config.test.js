/** @jest-environment jsdom */
import { setupConfigModal } from '../components/config.js';
describe('setupConfigModal', () => {
    beforeEach(() => {
        document.body.innerHTML = '<button id="configBtn"></button>';
    });
    test('muestra alerta al hacer click', () => {
        setupConfigModal();
        window.alert = jest.fn();
        document.getElementById('configBtn').click();
        expect(window.alert).toHaveBeenCalledWith('Configuración avanzada próximamente');
    });
});
