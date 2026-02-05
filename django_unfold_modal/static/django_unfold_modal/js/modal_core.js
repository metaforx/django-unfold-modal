/**
 * Django Unfold Modal - Core Module
 *
 * State management, configuration, utilities, and DOM creation.
 * Must be loaded before related_modal.js
 */
'use strict';

window.UnfoldModal = window.UnfoldModal || {};

(function(Modal) {
    // ---------------------------------------------------------------
    // Configuration
    // ---------------------------------------------------------------

    const config = window.UNFOLD_MODAL_CONFIG || {};
    const dimensions = config.dimensions || {
        width: "90%",
        maxWidth: "900px",
        height: "85vh",
        maxHeight: "700px"
    };
    const resizeEnabled = config.resize || false;

    // Expose config
    Modal.config = config;
    Modal.dimensions = dimensions;
    Modal.resizeEnabled = resizeEnabled;

    // ---------------------------------------------------------------
    // State
    // ---------------------------------------------------------------

    // Modal stack – last element is the active (visible) modal
    let modalStack = [];

    // Guard to prevent double-close during animation
    let isClosing = false;

    // Resize tracking – prevents overlay click from closing modal during resize
    let isResizing = false;

    // Scroll lock state
    let scrollbarWidth = 0;
    let savedScrollStyles = null;

    // CSS injection flag
    let stylesInjected = false;

    // Popup index for nested popups (matches Django's scheme)
    let popupIndex = 0;

    // Detect whether script is running inside a modal iframe
    const isInIframe = (window.parent !== window) && !window.opener;

    // Expose state accessors
    Modal.state = {
        get modalStack() { return modalStack; },
        get isClosing() { return isClosing; },
        set isClosing(v) { isClosing = v; },
        get isResizing() { return isResizing; },
        set isResizing(v) { isResizing = v; },
        get isInIframe() { return isInIframe; },
        get popupIndex() { return popupIndex; },
        set popupIndex(v) { popupIndex = v; }
    };

    // ---------------------------------------------------------------
    // Utility Functions
    // ---------------------------------------------------------------

    /**
     * Return the active (topmost) modal, or null.
     */
    function getActiveModal() {
        return modalStack.length > 0 ? modalStack[modalStack.length - 1] : null;
    }

    /**
     * Calculate scrollbar width to prevent page jump when locking scroll
     */
    function getScrollbarWidth() {
        if (scrollbarWidth) return scrollbarWidth;

        const outer = document.createElement('div');
        outer.style.visibility = 'hidden';
        outer.style.overflow = 'scroll';
        document.body.appendChild(outer);

        const inner = document.createElement('div');
        outer.appendChild(inner);

        scrollbarWidth = outer.offsetWidth - inner.offsetWidth;
        outer.parentNode.removeChild(outer);

        return scrollbarWidth;
    }

    /**
     * Lock body scroll without page jump.
     * Only saves styles on the first call (outermost modal).
     */
    function lockScroll() {
        if (savedScrollStyles !== null) return;

        savedScrollStyles = {
            overflow: document.body.style.overflow,
            paddingRight: document.body.style.paddingRight
        };

        const hasScrollbar = document.body.scrollHeight > window.innerHeight;
        document.body.style.overflow = 'hidden';
        if (hasScrollbar) {
            document.body.style.paddingRight = getScrollbarWidth() + 'px';
        }
    }

    /**
     * Unlock body scroll (only when no modals remain).
     */
    function unlockScroll() {
        if (savedScrollStyles) {
            document.body.style.overflow = savedScrollStyles.overflow;
            document.body.style.paddingRight = savedScrollStyles.paddingRight;
            savedScrollStyles = null;
        }
    }

    /**
     * Get maximize bounds (viewport minus margins matching Unfold container).
     * Returns { width, height } in pixels.
     */
    function getMaximizeBounds() {
        const margin = 16;
        return {
            width: window.innerWidth - (margin * 2),
            height: window.innerHeight - (margin * 2)
        };
    }

    /**
     * Set popup index from current window name (for nested popups)
     */
    function setPopupIndex() {
        if (document.getElementsByName('_popup').length > 0) {
            const index = window.name.lastIndexOf('__') + 2;
            popupIndex = parseInt(window.name.substring(index)) || 0;
        } else {
            popupIndex = 0;
        }
    }

    /**
     * Add popup index to name (matches Django's naming scheme)
     */
    function addPopupIndex(name) {
        return name + '__' + (popupIndex + 1);
    }

    // Expose utilities
    Modal.utils = {
        getActiveModal: getActiveModal,
        lockScroll: lockScroll,
        unlockScroll: unlockScroll,
        getMaximizeBounds: getMaximizeBounds,
        setPopupIndex: setPopupIndex,
        addPopupIndex: addPopupIndex
    };

    // ---------------------------------------------------------------
    // CSS Injection
    // ---------------------------------------------------------------

    /**
     * Inject CSS styles for dark mode support.
     */
    function injectStyles() {
        if (stylesInjected) return;
        stylesInjected = true;

        const style = document.createElement('style');
        style.textContent = `
            /* Dark mode support for modal */
            .dark .unfold-modal-container,
            [data-theme="dark"] .unfold-modal-container {
                background: var(--unfold-bg-color, #1f2937);
            }
            .dark .unfold-modal-header,
            [data-theme="dark"] .unfold-modal-header {
                border-bottom-color: var(--unfold-border-color, #374151);
            }
            .dark .unfold-modal-title,
            [data-theme="dark"] .unfold-modal-title {
                color: var(--unfold-text-color, #f3f4f6);
            }
            .dark .unfold-modal-close,
            .dark .unfold-modal-maximize,
            [data-theme="dark"] .unfold-modal-close,
            [data-theme="dark"] .unfold-modal-maximize {
                color: var(--unfold-text-color, #9ca3af);
            }
            .dark .unfold-modal-close:hover,
            .dark .unfold-modal-maximize:hover,
            [data-theme="dark"] .unfold-modal-close:hover,
            [data-theme="dark"] .unfold-modal-maximize:hover {
                background: var(--unfold-hover-bg, #374151) !important;
            }
            .dark .unfold-modal-iframe,
            [data-theme="dark"] .unfold-modal-iframe {
                background: var(--unfold-bg-color, #1f2937);
            }
        `;
        document.head.appendChild(style);
    }

    Modal.injectStyles = injectStyles;

    // ---------------------------------------------------------------
    // DOM Creation
    // ---------------------------------------------------------------

    /**
     * Create modal overlay element
     */
    function createModalOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'unfold-modal-overlay';
        overlay.style.cssText = `
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.15s ease-out;
        `;
        return overlay;
    }

    /**
     * Create modal container element
     */
    function createModalContainer() {
        const container = document.createElement('div');
        container.className = 'unfold-modal-container';

        const hasResizeObserver = typeof ResizeObserver !== 'undefined';

        // Calculate initial dimensions
        let initialWidth, initialHeight, maxWidthStyle, maxHeightStyle;

        if (resizeEnabled && hasResizeObserver) {
            // When resize is enabled, calculate initial size respecting preset max
            // but allow resizing beyond via ResizeObserver bounds enforcement
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;

            // Parse width (e.g., "95%" -> 0.95)
            const widthPercent = parseFloat(dimensions.width) / 100;
            const calculatedWidth = viewportWidth * widthPercent;
            const maxWidthPx = dimensions.maxWidth === 'none' ? Infinity : parseInt(dimensions.maxWidth);
            initialWidth = Math.min(calculatedWidth, maxWidthPx) + 'px';

            // Parse height (e.g., "90vh" -> 90% of viewport)
            const heightValue = parseFloat(dimensions.height);
            const calculatedHeight = viewportHeight * heightValue / 100;
            const maxHeightPx = dimensions.maxHeight === 'none' ? Infinity : parseInt(dimensions.maxHeight);
            initialHeight = Math.min(calculatedHeight, maxHeightPx) + 'px';

            // Allow resizing beyond preset (ResizeObserver enforces viewport bounds)
            maxWidthStyle = 'none';
            maxHeightStyle = 'none';
        } else {
            // No resize or no ResizeObserver - use preset dimensions directly
            initialWidth = dimensions.width;
            initialHeight = dimensions.height;
            maxWidthStyle = dimensions.maxWidth;
            maxHeightStyle = dimensions.maxHeight;
        }

        container.style.cssText = `
            background: var(--unfold-bg-color, #fff);
            border-radius: var(--unfold-border-radius, 0.5rem);
            width: ${initialWidth};
            max-width: ${maxWidthStyle};
            height: ${initialHeight};
            max-height: ${maxHeightStyle};
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            transform: scale(0.95);
            transition: transform 0.15s ease-out;
            ${resizeEnabled ? 'resize: both;' : ''}
        `;
        return container;
    }

    /**
     * Create modal header with maximize button (left), title (center), close button (right)
     */
    function createModalHeader(closeCallback) {
        const header = document.createElement('div');
        header.className = 'unfold-modal-header';
        header.style.cssText = `
            display: flex;
            align-items: center;
            padding: 0.5rem;
            border-bottom: 1px solid var(--unfold-border-color, #e5e7eb);
            flex-shrink: 0;
            min-height: 2.5rem;
        `;

        // Left button group (maximize button)
        const leftButtonGroup = document.createElement('div');
        leftButtonGroup.style.cssText = `
            display: flex;
            align-items: center;
            flex-shrink: 0;
            min-width: 2.5rem;
        `;

        // Maximize button (left side)
        const maximizeButton = document.createElement('button');
        maximizeButton.type = 'button';
        maximizeButton.className = 'unfold-modal-maximize';
        maximizeButton.title = 'Maximize';
        maximizeButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            </svg>
        `;
        maximizeButton.style.cssText = `
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.5rem;
            color: var(--unfold-text-color, #6b7280);
            border-radius: 0.25rem;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        maximizeButton.addEventListener('mouseenter', function() {
            this.style.background = 'var(--unfold-hover-bg, #f3f4f6)';
        });
        maximizeButton.addEventListener('mouseleave', function() {
            this.style.background = 'none';
        });

        leftButtonGroup.appendChild(maximizeButton);

        // Title element (centered)
        const title = document.createElement('span');
        title.className = 'unfold-modal-title';
        title.style.cssText = `
            flex: 1;
            text-align: center;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--unfold-text-color, #374151);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            padding: 0 0.5rem;
        `;
        title.textContent = '';

        // Right button group (close button)
        const rightButtonGroup = document.createElement('div');
        rightButtonGroup.style.cssText = `
            display: flex;
            align-items: center;
            flex-shrink: 0;
            min-width: 2.5rem;
        `;

        // Close button (right side)
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'unfold-modal-close';
        closeButton.title = 'Close';
        closeButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        `;
        closeButton.style.cssText = `
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.5rem;
            color: var(--unfold-text-color, #6b7280);
            border-radius: 0.25rem;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        closeButton.addEventListener('click', closeCallback);
        closeButton.addEventListener('mouseenter', function() {
            this.style.background = 'var(--unfold-hover-bg, #f3f4f6)';
        });
        closeButton.addEventListener('mouseleave', function() {
            this.style.background = 'none';
        });

        rightButtonGroup.appendChild(closeButton);

        header.appendChild(leftButtonGroup);
        header.appendChild(title);
        header.appendChild(rightButtonGroup);

        return { header, title, maximizeButton };
    }

    /**
     * Create iframe element
     */
    function createIframe(url, name) {
        const iframe = document.createElement('iframe');
        iframe.name = name;
        iframe.src = url;
        iframe.className = 'unfold-modal-iframe';
        iframe.style.cssText = `
            flex: 1;
            width: 100%;
            border: none;
            background: var(--unfold-bg-color, #fff);
        `;
        return iframe;
    }

    // Expose DOM creation functions
    Modal.dom = {
        createOverlay: createModalOverlay,
        createContainer: createModalContainer,
        createHeader: createModalHeader,
        createIframe: createIframe
    };

})(window.UnfoldModal);
