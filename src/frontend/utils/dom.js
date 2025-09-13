/**
 * DOM Utilities
 * Helper functions for DOM manipulation
 */

export class DOMUtils {
    /**
     * Create an element with attributes and content
     */
    static createElement(tag, attributes = {}, content = '') {
        const element = document.createElement(tag);

        // Set attributes
        for (const [key, value] of Object.entries(attributes)) {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'textContent') {
                element.textContent = value;
            } else if (key === 'innerHTML') {
                element.innerHTML = value;
            } else if (key.startsWith('on') && typeof value === 'function') {
                element.addEventListener(key.slice(2).toLowerCase(), value);
            } else {
                element.setAttribute(key, value);
            }
        }

        // Set content if provided and not already set
        if (content && !attributes.textContent && !attributes.innerHTML) {
            element.textContent = content;
        }

        return element;
    }

    /**
     * Add event listener with automatic cleanup
     */
    static addEventListener(element, event, handler, options = {}) {
        element.addEventListener(event, handler, options);

        // Return cleanup function
        return () => element.removeEventListener(event, handler, options);
    }

    /**
     * Toggle class on element
     */
    static toggleClass(element, className, force) {
        return element.classList.toggle(className, force);
    }

    /**
     * Add class to element
     */
    static addClass(element, ...classNames) {
        element.classList.add(...classNames);
    }

    /**
     * Remove class from element
     */
    static removeClass(element, ...classNames) {
        element.classList.remove(...classNames);
    }

    /**
     * Check if element has class
     */
    static hasClass(element, className) {
        return element.classList.contains(className);
    }

    /**
     * Get element by selector with optional context
     */
    static $(selector, context = document) {
        return context.querySelector(selector);
    }

    /**
     * Get elements by selector with optional context
     */
    static $$(selector, context = document) {
        return Array.from(context.querySelectorAll(selector));
    }

    /**
     * Show element
     */
    static show(element) {
        element.style.display = '';
    }

    /**
     * Hide element
     */
    static hide(element) {
        element.style.display = 'none';
    }

    /**
     * Toggle element visibility
     */
    static toggle(element) {
        const current = element.style.display;
        element.style.display = current === 'none' ? '' : 'none';
    }

    /**
     * Empty element content
     */
    static empty(element) {
        while (element.firstChild) {
            element.removeChild(element.firstChild);
        }
    }

    /**
     * Get element dimensions
     */
    static getDimensions(element) {
        const rect = element.getBoundingClientRect();
        return {
            width: rect.width,
            height: rect.height,
            top: rect.top,
            left: rect.left,
            right: rect.right,
            bottom: rect.bottom
        };
    }

    /**
     * Animate element
     */
    static animate(element, properties, duration = 300, easing = 'ease') {
        return new Promise(resolve => {
            const start = {};
            const delta = {};

            // Get initial values
            for (const property in properties) {
                if (properties.hasOwnProperty(property)) {
                    start[property] = parseFloat(getComputedStyle(element)[property]) || 0;
                    delta[property] = properties[property] - start[property];
                }
            }

            const startTime = performance.now();

            const animate = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);

                // Apply easing
                let easedProgress;
                switch (easing) {
                    case 'ease-in':
                        easedProgress = progress * progress;
                        break;
                    case 'ease-out':
                        easedProgress = progress * (2 - progress);
                        break;
                    case 'ease-in-out':
                        easedProgress = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;
                        break;
                    default:
                        easedProgress = progress;
                }

                // Apply properties
                for (const property in properties) {
                    if (properties.hasOwnProperty(property)) {
                        const value = start[property] + delta[property] * easedProgress;
                        element.style[property] = value + (typeof properties[property] === 'number' ? 'px' : '');
                    }
                }

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    resolve();
                }
            };

            requestAnimationFrame(animate);
        });
    }
}