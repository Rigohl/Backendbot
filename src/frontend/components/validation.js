/**
 * Sistema de validación de formularios y feedback de usuario
 * Proporciona validaciones en tiempo real y mensajes de error consistentes
 */

// Configuración de validaciones
const VALIDATION_RULES = {
    url: {
        pattern: /^https?:\/\/(localhost|127\.0\.0\.1|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d{1,5})?$/,
        message: 'URL debe ser localhost, 127.0.0.1 o una IP válida con puerto opcional'
    },
    apiKey: {
        pattern: /^[a-zA-Z0-9\-_]{20,}$/,
        message: 'API Key debe tener al menos 20 caracteres alfanuméricos'
    },
    username: {
        pattern: /^[a-zA-Z0-9_]{3,20}$/,
        message: 'Usuario debe tener 3-20 caracteres alfanuméricos o guiones bajos'
    },
    password: {
        pattern: /^.{8,}$/,
        message: 'Contraseña debe tener al menos 8 caracteres'
    }
};

/**
 * Valida un campo individual
 * @param {string} fieldName - Nombre del campo
 * @param {string} value - Valor a validar
 * @returns {Object} Resultado de validación
 */
export function validateField(fieldName, value) {
    const rule = VALIDATION_RULES[fieldName];
    if (!rule) {
        return { isValid: true };
    }

    const isValid = rule.pattern.test(value);
    return {
        isValid,
        message: isValid ? '' : rule.message,
        field: fieldName
    };
}

/**
 * Valida un formulario completo
 * @param {Object} formData - Datos del formulario
 * @returns {Object} Resultado de validación del formulario
 */
export function validateForm(formData) {
    const errors = [];
    const results = {};

    Object.keys(formData).forEach(field => {
        const result = validateField(field, formData[field]);
        results[field] = result;
        if (!result.isValid) {
            errors.push(result);
        }
    });

    return {
        isValid: errors.length === 0,
        errors,
        results
    };
}

/**
 * Muestra feedback visual en un campo
 * @param {HTMLElement} field - Elemento del campo
 * @param {Object} validationResult - Resultado de validación
 */
export function showFieldFeedback(field, validationResult) {
    if (!field) {
        return;
    }

    // Remover feedback anterior
    removeFieldFeedback(field);

    const { isValid, message } = validationResult;

    if (!isValid && message) {
        field.classList.add('invalid');
        field.classList.remove('valid');

        // Crear mensaje de error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            color: #ef4444;
            font-size: 0.875rem;
            margin-top: 0.25rem;
            display: block;
        `;

        field.parentNode.insertBefore(errorDiv, field.nextSibling);
    } else if (field.value.trim() !== '') {
        field.classList.add('valid');
        field.classList.remove('invalid');
    }
}

/**
 * Remueve feedback visual de un campo
 * @param {HTMLElement} field - Elemento del campo
 */
export function removeFieldFeedback(field) {
    if (!field) {
        return;
    }

    field.classList.remove('valid', 'invalid');

    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Configura validación en tiempo real para un campo
 * @param {HTMLElement} field - Elemento del campo
 * @param {string} fieldName - Nombre del campo para validación
 */
export function setupFieldValidation(field, fieldName) {
    if (!field) {
        return;
    }

    let timeoutId;

    field.addEventListener('input', () => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            const result = validateField(fieldName, field.value);
            showFieldFeedback(field, result);
        }, 300); // Debounce de 300ms
    });

    field.addEventListener('blur', () => {
        const result = validateField(fieldName, field.value);
        showFieldFeedback(field, result);
    });
}

/**
 * Valida y envía un formulario
 * @param {HTMLFormElement} form - Elemento del formulario
 * @param {Function} submitCallback - Callback para envío exitoso
 * @returns {boolean} True si el formulario es válido
 */
export function validateAndSubmit(form, submitCallback) {
    if (!form) {
        return false;
    }

    const formData = {};
    const fields = form.querySelectorAll('input, select, textarea');

    fields.forEach(field => {
        formData[field.name || field.id] = field.value;
    });

    const validation = validateForm(formData);

    // Mostrar feedback en todos los campos
    fields.forEach(field => {
        const fieldName = field.name || field.id;
        if (validation.results[fieldName]) {
            showFieldFeedback(field, validation.results[fieldName]);
        }
    });

    if (validation.isValid && typeof submitCallback === 'function') {
        submitCallback(formData);
        return true;
    }

    return false;
}

/**
 * Inicializa validaciones para un formulario
 * @param {string} formId - ID del formulario
 * @param {Function} submitCallback - Callback para envío
 */
export function initFormValidation(formId, submitCallback) {
    const form = document.getElementById(formId);
    if (!form) {
        return;
    }

    // Configurar validación para cada campo
    const fields = form.querySelectorAll('input, select, textarea');
    fields.forEach(field => {
        const fieldName = field.name || field.id;
        if (VALIDATION_RULES[fieldName]) {
            setupFieldValidation(field, fieldName);
        }
    });

    // Configurar envío del formulario
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        validateAndSubmit(form, submitCallback);
    });
}
