/**
 * Sistema de Internacionalización para BackendBot
 * Soporte multi-idioma con detección automática
 */

class I18nService {
    constructor() {
        this.currentLang = this.detectLanguage();
        this.translations = {};
        this.fallbackLang = 'es';
        this.observers = [];

        this.init();
    }

    async init() {
        // Cargar idioma por defecto
        await this.loadLanguage(this.currentLang);

        // Suscribirse a cambios de configuración
        if (window.useConfigStore) {
            window.useConfigStore.subscribe((state) => {
                if (state.language !== this.currentLang) {
                    this.setLanguage(state.language);
                }
            });
        }
    }

    // Detectar idioma del navegador/sistema
    detectLanguage() {
        // Prioridad: localStorage > navegador > fallback
        const saved = localStorage.getItem('backendbot_language');
        if (saved && this.isSupportedLanguage(saved)) {
            return saved;
        }

        const browserLang = navigator.language || navigator.userLanguage;
        const lang = browserLang.split('-')[0]; // es-ES -> es

        return this.isSupportedLanguage(lang) ? lang : this.fallbackLang;
    }

    // Verificar si el idioma está soportado
    isSupportedLanguage(lang) {
        return ['es', 'en', 'pt', 'fr', 'de'].includes(lang);
    }

    // Cargar traducciones de un idioma
    async loadLanguage(lang) {
        try {
            const response = await fetch(`/locales/${lang}.json`);
            if (!response.ok) {
                throw new Error(`Language file not found: ${lang}`);
            }

            this.translations[lang] = await response.json();
            return true;
        } catch (error) {
            console.warn(`Error loading language ${lang}:`, error);

            // Intentar con fallback
            if (lang !== this.fallbackLang) {
                return this.loadLanguage(this.fallbackLang);
            }

            return false;
        }
    }

    // Cambiar idioma
    async setLanguage(lang) {
        if (!this.isSupportedLanguage(lang)) {
            console.warn(`Unsupported language: ${lang}`);
            return false;
        }

        if (!this.translations[lang]) {
            const loaded = await this.loadLanguage(lang);
            if (!loaded) {
                return false;
            }
        }

        this.currentLang = lang;
        localStorage.setItem('backendbot_language', lang);

        // Notificar a observadores
        this.notifyObservers();

        // Actualizar configuración global
        if (window.useConfigStore) {
            window.useConfigStore.getState().setLanguage(lang);
        }

        // Disparar evento personalizado
        window.dispatchEvent(new CustomEvent('languageChanged', {
            detail: { language: lang }
        }));

        return true;
    }

    // Traducir texto
    t(key, params = {}) {
        const keys = key.split('.');
        let value = this.translations[this.currentLang];

        // Navegar por la estructura anidada
        for (const k of keys) {
            value = value?.[k];
        }

        // Fallback al idioma por defecto
        if (!value && this.currentLang !== this.fallbackLang) {
            value = this.translations[this.fallbackLang];
            for (const k of keys) {
                value = value?.[k];
            }
        }

        // Fallback a la key si no se encuentra
        if (!value) {
            console.warn(`Translation missing for key: ${key}`);
            return key;
        }

        // Reemplazar parámetros
        return this.interpolate(value, params);
    }

    // Interpolar parámetros en el texto
    interpolate(text, params) {
        return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
            return params[key] !== undefined ? params[key] : match;
        });
    }

    // Obtener idioma actual
    getCurrentLanguage() {
        return this.currentLang;
    }

    // Obtener idiomas disponibles
    getAvailableLanguages() {
        return [
            { code: 'es', name: 'Español', flag: '🇪🇸' },
            { code: 'en', name: 'English', flag: '🇺🇸' },
            { code: 'pt', name: 'Português', flag: '🇧🇷' },
            { code: 'fr', name: 'Français', flag: '🇫🇷' },
            { code: 'de', name: 'Deutsch', flag: '🇩🇪' }
        ];
    }

    // Suscribirse a cambios de idioma
    subscribe(callback) {
        this.observers.push(callback);
        return () => {
            this.observers = this.observers.filter(obs => obs !== callback);
        };
    }

    // Notificar a observadores
    notifyObservers() {
        this.observers.forEach(callback => callback(this.currentLang));
    }

    // Formatear números según locale
    formatNumber(number, options = {}) {
        return new Intl.NumberFormat(this.currentLang, options).format(number);
    }

    // Formatear fechas según locale
    formatDate(date, options = {}) {
        return new Intl.DateTimeFormat(this.currentLang, options).format(date);
    }

    // Formatear moneda
    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat(this.currentLang, {
            style: 'currency',
            currency
        }).format(amount);
    }

    // Obtener dirección del texto (RTL/LTR)
    getTextDirection() {
        const rtlLanguages = ['ar', 'he', 'fa'];
        return rtlLanguages.includes(this.currentLang) ? 'rtl' : 'ltr';
    }
}

// Instancia global
export const i18n = new I18nService();

// Funciones convenientes globales
window.t = (key, params) => i18n.t(key, params);
window.setLanguage = (lang) => i18n.setLanguage(lang);
window.getCurrentLanguage = () => i18n.getCurrentLanguage();