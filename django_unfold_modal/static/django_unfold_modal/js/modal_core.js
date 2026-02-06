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
