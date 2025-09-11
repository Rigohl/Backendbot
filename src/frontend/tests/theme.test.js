/** @jest-environment jsdom */
import { setupThemeToggle } from '../../components/theme.js';
describe('setupThemeToggle', () => {
    beforeEach(() => {
        document.body.innerHTML = '<button id="themeToggle"></button>';
        localStorage.clear();
    });
    test('inicializa con tema claro', () => {
        setupThemeToggle();
        expect(document.body.classList.contains('dark')).toBe(false);
    });
    test('cambia a modo oscuro al hacer click', () => {
        setupThemeToggle();
        document.getElementById('themeToggle').click();
        expect(document.body.classList.contains('dark')).toBe(true);
        expect(localStorage.getItem('theme')).toBe('dark');
    });
});
