/**
 * Tests para el sistema de validación
 */

import { validateField, validateForm, showFieldFeedback, removeFieldFeedback } from '../components/validation.js';

// Mock de DOM para tests
global.document = {
    createElement: (tag) => ({
        className: '',
        textContent: '',
        style: {},
        parentNode: {
            insertBefore: jest.fn(),
            querySelector: jest.fn(),
            removeChild: jest.fn()
        }
    }),
    getElementById: jest.fn(),
    querySelectorAll: jest.fn(() => [])
};

describe('Validation System', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('validateField', () => {
        test('should validate URL field correctly', () => {
            const result = validateField('backendUrl', 'http://127.0.0.1:8000');
            expect(result.isValid).toBe(true);
            expect(result.message).toBe('');
        });

        test('should reject invalid URL', () => {
            const result = validateField('backendUrl', 'invalid-url');
            expect(result.isValid).toBe(false);
            expect(result.message).toContain('URL debe ser');
        });

        test('should validate API key correctly', () => {
            const result = validateField('apiKey', 'valid-api-key-12345');
            expect(result.isValid).toBe(true);
        });

        test('should reject short API key', () => {
            const result = validateField('apiKey', 'short');
            expect(result.isValid).toBe(false);
            expect(result.message).toContain('al menos 20 caracteres');
        });

        test('should validate username correctly', () => {
            const result = validateField('username', 'testuser');
            expect(result.isValid).toBe(true);
        });

        test('should reject invalid username', () => {
            const result = validateField('username', 'us');
            expect(result.isValid).toBe(false);
            expect(result.message).toContain('3-20 caracteres');
        });

        test('should validate password correctly', () => {
            const result = validateField('password', 'securepassword123');
            expect(result.isValid).toBe(true);
        });

        test('should reject short password', () => {
            const result = validateField('password', 'short');
            expect(result.isValid).toBe(false);
            expect(result.message).toContain('al menos 8 caracteres');
        });

        test('should return valid for unknown field types', () => {
            const result = validateField('unknownField', 'any value');
            expect(result.isValid).toBe(true);
        });
    });

    describe('validateForm', () => {
        test('should validate complete form correctly', () => {
            const formData = {
                backendUrl: 'http://127.0.0.1:8000',
                apiKey: 'valid-api-key-12345678901234567890',
                username: 'testuser',
                password: 'securepass123'
            };

            const result = validateForm(formData);
            expect(result.isValid).toBe(true);
            expect(result.errors).toHaveLength(0);
        });

        test('should collect multiple validation errors', () => {
            const formData = {
                backendUrl: 'invalid-url',
                apiKey: 'short',
                username: 'us',
                password: 'short'
            };

            const result = validateForm(formData);
            expect(result.isValid).toBe(false);
            expect(result.errors).toHaveLength(4);
        });
    });

    describe('showFieldFeedback', () => {
        test('should add valid class for valid field', () => {
            const mockField = {
                classList: {
                    add: jest.fn(),
                    remove: jest.fn()
                },
                parentNode: {
                    insertBefore: jest.fn(),
                    querySelector: jest.fn()
                }
            };

            const validationResult = { isValid: true, message: '' };

            showFieldFeedback(mockField, validationResult);

            expect(mockField.classList.add).toHaveBeenCalledWith('valid');
            expect(mockField.classList.remove).toHaveBeenCalledWith('invalid');
        });

        test('should add invalid class and error message for invalid field', () => {
            const mockField = {
                classList: {
                    add: jest.fn(),
                    remove: jest.fn()
                },
                parentNode: {
                    insertBefore: jest.fn(),
                    querySelector: jest.fn()
                }
            };

            const validationResult = { isValid: false, message: 'Error message' };

            showFieldFeedback(mockField, validationResult);

            expect(mockField.classList.add).toHaveBeenCalledWith('invalid');
            expect(mockField.classList.remove).toHaveBeenCalledWith('valid');
        });

        test('should handle null field gracefully', () => {
            expect(() => showFieldFeedback(null, { isValid: true })).not.toThrow();
        });
    });

    describe('removeFieldFeedback', () => {
        test('should remove all feedback classes and error messages', () => {
            const mockField = {
                classList: {
                    remove: jest.fn()
                },
                parentNode: {
                    querySelector: jest.fn(() => ({ remove: jest.fn() }))
                }
            };

            removeFieldFeedback(mockField);

            expect(mockField.classList.remove).toHaveBeenCalledWith('valid', 'invalid');
        });

        test('should handle null field gracefully', () => {
            expect(() => removeFieldFeedback(null)).not.toThrow();
        });
    });
});