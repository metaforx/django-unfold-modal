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
    const disableHeader = config.disableHeader !== false; // Default true

    // Expose config
    Modal.config = config;
    Modal.dimensions = dimensions;
    Modal.resizeEnabled = resizeEnabled;
    Modal.disableHeader = disableHeader;

    // ---------------------------------------------------------------
    // Message Type Constants
    // ---------------------------------------------------------------

    const MSG = {
        MODAL_OPEN: 'django:modal:open',
        MODAL_CLOSE: 'django:modal:close',
        MODAL_DISMISS: 'django:modal:dismiss',
        POPUP_ADD: 'django:popup:add',
        POPUP_CHANGE: 'django:popup:change',
        POPUP_DELETE: 'django:popup:delete',
        POPUP_LOOKUP: 'django:popup:lookup'
    };

    Modal.MSG = MSG;

    // ---------------------------------------------------------------
    // Material Symbols Icons (matching Unfold's icon pattern)
    // ---------------------------------------------------------------

    const ICONS = {
        maximize: '<span class="material-symbols-outlined">open_in_full</span>',
        restore: '<span class="material-symbols-outlined">close_fullscreen</span>',
        close: '<span class="material-symbols-outlined">close</span>'
    };

    Modal.ICONS = ICONS;

    // ---------------------------------------------------------------
    // Unfold Admin Selectors (stable IDs and structural containers)
    // ---------------------------------------------------------------

    const SELECTORS = {
        // Main content container ID
        MAIN: 'main',
        // Header inner element ID (used to locate header container)
        HEADER_INNER: 'header-inner',
        // Number of levels from HEADER_INNER to the header container div
        HEADER_CONTAINER_DEPTH: 2
    };

    Modal.SELECTORS = SELECTORS;

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

    // CSS injection flag (legacy - styles now in modal.css)
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

    /**
     * Ensure URL has _popup parameter set.
     * Returns URL object with _popup=1 added if missing.
     */
    function ensurePopupParam(href) {
        const url = new URL(href);
        if (!url.searchParams.has('_popup')) {
            url.searchParams.set('_popup', '1');
        }
        return url;
    }

    /**
     * Get popup name from link ID by stripping prefix and adding popup index.
     * @param {string} linkId - The link element's ID
     * @param {RegExp} prefixPattern - Pattern to strip (e.g., /^(change|add|delete|view)_/)
     */
    function getPopupName(linkId, prefixPattern) {
        return addPopupIndex(linkId.replace(prefixPattern, ''));
    }

    // Expose utilities
    Modal.utils = {
        getActiveModal: getActiveModal,
        lockScroll: lockScroll,
        unlockScroll: unlockScroll,
        getMaximizeBounds: getMaximizeBounds,
        setPopupIndex: setPopupIndex,
        addPopupIndex: addPopupIndex,
        ensurePopupParam: ensurePopupParam,
        getPopupName: getPopupName
    };

    // ---------------------------------------------------------------
    // CSS Injection
    // ---------------------------------------------------------------

    /**
     * Inject CSS styles for modal components.
     * This provides runtime injection as fallback when external CSS is not loaded.
     * All styles are also available in static/django_unfold_modal/css/modal.css.
     * Uses Unfold's CSS variable tokens (--color-base-*) with fallbacks.
     */
    function injectStyles() {
        if (stylesInjected) return;
        stylesInjected = true;

        const style = document.createElement('style');
        style.id = 'unfold-modal-styles';
        style.textContent = `
            /* CSS Custom Properties */
            :root {
                --unfold-modal-z-index: 9999;
                --unfold-modal-backdrop: rgba(0, 0, 0, 0.5);
                --unfold-modal-transition-duration: 150ms;
                --unfold-modal-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            }

            /* Modal Overlay */
            .unfold-modal-overlay {
                position: fixed;
                inset: 0;
                background: var(--unfold-modal-backdrop);
                z-index: var(--unfold-modal-z-index);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity var(--unfold-modal-transition-duration) ease-out;
            }

            /* Modal Container */
            .unfold-modal-container {
                border-radius: 0.5rem;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: var(--unfold-modal-shadow);
                transform: scale(0.95);
                transition: transform var(--unfold-modal-transition-duration) ease-out;
                background: var(--color-base-50, #fafafa);
            }

            /* Resize enabled variant */
            .unfold-modal-container.unfold-modal-resizable {
                resize: both;
            }

            /* Modal Header */
            .unfold-modal-header {
                display: flex;
                align-items: center;
                padding: 0.5rem;
                border-bottom-width: 1px;
                border-bottom-style: solid;
                border-bottom-color: var(--color-base-200, #e4e4e7);
                flex-shrink: 0;
                min-height: 2.5rem;
            }

            /* Header Button Groups */
            .unfold-modal-btn-group {
                display: flex;
                align-items: center;
                flex-shrink: 0;
                min-width: 2.5rem;
            }

            /* Modal Title */
            .unfold-modal-title {
                flex: 1;
                text-align: center;
                font-size: 0.875rem;
                font-weight: 500;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                padding: 0 0.5rem;
                color: var(--color-base-700, #3f3f46);
            }

            /* Modal Buttons */
            .unfold-modal-close,
            .unfold-modal-maximize {
                background: transparent;
                border: none;
                cursor: pointer;
                padding: 0.5rem;
                color: var(--color-base-500, #71717a);
                border-radius: 0.25rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.25rem;
                line-height: 1;
            }

            /* Button hover effects (light mode) */
            .unfold-modal-close:hover,
            .unfold-modal-maximize:hover {
                background: var(--color-base-100, #f4f4f5);
            }

            /* Modal Iframe */
            .unfold-modal-iframe {
                flex: 1;
                width: 100%;
                border: none;
                background: var(--color-base-50, #fafafa);
            }

            /* Dark mode support */
            .dark .unfold-modal-container,
            [data-theme="dark"] .unfold-modal-container {
                background: var(--color-base-900, #18181b);
            }
            .dark .unfold-modal-header,
            [data-theme="dark"] .unfold-modal-header {
                border-bottom-color: var(--color-base-700, #3f3f46);
            }
            .dark .unfold-modal-title,
            [data-theme="dark"] .unfold-modal-title {
                color: var(--color-base-100, #f4f4f5);
            }
            .dark .unfold-modal-close,
            .dark .unfold-modal-maximize,
            [data-theme="dark"] .unfold-modal-close,
            [data-theme="dark"] .unfold-modal-maximize {
                color: var(--color-base-400, #a1a1aa);
            }
            .dark .unfold-modal-close:hover,
            .dark .unfold-modal-maximize:hover,
            [data-theme="dark"] .unfold-modal-close:hover,
            [data-theme="dark"] .unfold-modal-maximize:hover {
                background: var(--color-base-800, #27272a);
            }
            .dark .unfold-modal-iframe,
            [data-theme="dark"] .unfold-modal-iframe {
                background: var(--color-base-900, #18181b);
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
        // All styles defined in modal.css
        return overlay;
    }

    /**
     * Create modal container element
     */
    function createModalContainer() {
        const container = document.createElement('div');
        // Base styles from modal.css, add resizable class if enabled
        container.className = resizeEnabled
            ? 'unfold-modal-container unfold-modal-resizable'
            : 'unfold-modal-container';

        const hasResizeObserver = typeof ResizeObserver !== 'undefined';

        // Calculate initial dimensions (must be inline - dynamic from config)
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

        // Only dynamic dimension styles remain inline
        container.style.width = initialWidth;
        container.style.maxWidth = maxWidthStyle;
        container.style.height = initialHeight;
        container.style.maxHeight = maxHeightStyle;

        return container;
    }

    /**
     * Create modal header with maximize button (left), title (center), close button (right)
     */
    function createModalHeader(closeCallback) {
        const header = document.createElement('div');
        header.className = 'unfold-modal-header';
        // All styles defined in modal.css

        // Left button group (maximize button)
        const leftButtonGroup = document.createElement('div');
        leftButtonGroup.className = 'unfold-modal-btn-group';

        // Maximize button (left side)
        const maximizeButton = document.createElement('button');
        maximizeButton.type = 'button';
        maximizeButton.className = 'unfold-modal-maximize';
        maximizeButton.title = 'Maximize';
        maximizeButton.innerHTML = ICONS.maximize;

        leftButtonGroup.appendChild(maximizeButton);

        // Title element (centered)
        const title = document.createElement('span');
        title.className = 'unfold-modal-title';
        title.textContent = '';

        // Right button group (close button)
        const rightButtonGroup = document.createElement('div');
        rightButtonGroup.className = 'unfold-modal-btn-group';

        // Close button (right side)
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'unfold-modal-close';
        closeButton.title = 'Close';
        closeButton.innerHTML = ICONS.close;
        closeButton.addEventListener('click', closeCallback);

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
        // All styles defined in modal.css
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
