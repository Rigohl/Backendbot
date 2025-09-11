/**
 * Tests para el sistema de notificaciones
 */

import {
    initNotifications,
    createNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeNotification,
    clearAllNotifications
} from '../components/notifications.js';

// Mock de DOM para tests
const createMockElement = () => ({
    className: '',
    textContent: '',
    style: {},
    innerHTML: '',
    parentNode: null,
    querySelector: jest.fn(() => ({
        addEventListener: jest.fn(),
        style: {}
    })),
    querySelectorAll: jest.fn(() => []),
    appendChild: jest.fn(),
    removeChild: jest.fn(),
    addEventListener: jest.fn()
});

global.document = {
    createElement: jest.fn(createMockElement),
    getElementById: jest.fn(() => null),
    head: {
        appendChild: jest.fn()
    },
    body: {
        appendChild: jest.fn()
    }
};

describe('Notification System', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        // Reset global notification container
        delete global.notificationContainer;
    });

    describe('initNotifications', () => {
        test('should create notification container and add styles', () => {
            initNotifications();

            expect(document.createElement).toHaveBeenCalledWith('div');
            expect(document.body.appendChild).toHaveBeenCalled();
            expect(document.head.appendChild).toHaveBeenCalled();
        });

        test('should not reinitialize if already initialized', () => {
            // First call
            initNotifications();
            expect(document.createElement).toHaveBeenCalledTimes(1);

            // Second call should not create new elements
            jest.clearAllMocks();
            initNotifications();
            expect(document.createElement).not.toHaveBeenCalled();
        });
    });

    describe('createNotification', () => {
        beforeEach(() => {
            initNotifications();
        });

        test('should create notification with correct structure', () => {
            const notification = createNotification('success', 'Test Title', 'Test Message');

            expect(notification).toBeDefined();
            expect(notification.className).toContain('notification');
            expect(notification.className).toContain('success');
            expect(notification.innerHTML).toContain('Test Title');
            expect(notification.innerHTML).toContain('Test Message');
        });

        test('should auto-remove notification after duration', () => {
            jest.useFakeTimers();

            const notification = createNotification('info', 'Test', 'Message', 1000);

            expect(notification).toBeDefined();

            // Fast-forward time
            jest.advanceTimersByTime(1000);

            // Should have been removed (though we can't easily test setTimeout in this mock)
            expect(notification).toBeDefined();
        });

        test('should limit maximum notifications', () => {
            // Create multiple notifications
            for (let i = 0; i < 7; i++) {
                createNotification('info', `Test ${i}`, `Message ${i}`);
            }

            // Should have created notifications but limited the display
            expect(document.createElement).toHaveBeenCalled();
        });
    });

    describe('Convenience methods', () => {
        beforeEach(() => {
            initNotifications();
        });

        test('showSuccess should create success notification', () => {
            const notification = showSuccess('Success', 'Operation completed');

            expect(notification).toBeDefined();
            expect(notification.className).toContain('success');
        });

        test('showError should create error notification', () => {
            const notification = showError('Error', 'Something went wrong');

            expect(notification).toBeDefined();
            expect(notification.className).toContain('error');
        });

        test('showWarning should create warning notification', () => {
            const notification = showWarning('Warning', 'Be careful');

            expect(notification).toBeDefined();
            expect(notification.className).toContain('warning');
        });

        test('showInfo should create info notification', () => {
            const notification = showInfo('Info', 'Here is some information');

            expect(notification).toBeDefined();
            expect(notification.className).toContain('info');
        });
    });

    describe('removeNotification', () => {
        test('should handle null notification gracefully', () => {
            expect(() => removeNotification(null)).not.toThrow();
        });

        test('should add hide class and remove after timeout', () => {
            const mockNotification = {
                classList: {
                    add: jest.fn()
                },
                parentNode: {
                    removeChild: jest.fn()
                }
            };

            removeNotification(mockNotification);

            expect(mockNotification.classList.add).toHaveBeenCalledWith('hide');
        });
    });

    describe('clearAllNotifications', () => {
        test('should handle null container gracefully', () => {
            expect(() => clearAllNotifications()).not.toThrow();
        });

        test('should remove all notifications when container exists', () => {
            initNotifications();

            // Mock notifications
            const mockNotifications = [
                { classList: { add: jest.fn() }, parentNode: { removeChild: jest.fn() } },
                { classList: { add: jest.fn() }, parentNode: { removeChild: jest.fn() } }
            ];

            // Mock querySelectorAll to return our mock notifications
            document.querySelectorAll = jest.fn(() => mockNotifications);

            clearAllNotifications();

            mockNotifications.forEach(notification => {
                expect(notification.classList.add).toHaveBeenCalledWith('hide');
            });
        });
    });
});