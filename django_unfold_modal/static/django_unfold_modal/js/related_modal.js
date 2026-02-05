/**
 * Django Unfold Modal - Related Object Modal
 *
 * Replaces Django admin popup windows with Unfold-styled modals using iframes.
 * Listens for django:show-related and django:lookup-related events and prevents
 * the default popup behavior.
 *
 * Supports nested modals via a replacement stack: opening a nested modal hides
 * the current one; closing/saving restores it.
 */
'use strict';

(function() {
    // Track popup index for nested popups (matches Django's scheme)
    let popupIndex = 0;

    // Modal stack – last element is the active (visible) modal
    let modalStack = [];

    // Guard to prevent double-close during animation
    let isClosing = false;

    let scrollbarWidth = 0;
    let savedScrollStyles = null;

    // Detect whether this script is running inside a modal iframe
    const isInIframe = (window.parent !== window) && !window.opener;

    // Read configuration from window.UNFOLD_MODAL_CONFIG (set by config.js)
    const config = window.UNFOLD_MODAL_CONFIG || {};
    const dimensions = config.dimensions || {
        width: "90%",
        maxWidth: "900px",
        height: "85vh",
        maxHeight: "700px"
    };
    const resizeEnabled = config.resize || false;

    // Resize tracking – prevents overlay click from closing modal during resize
    let isResizing = false;

    // CSS injection flag
    let stylesInjected = false;

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
        if (savedScrollStyles !== null) return; // already locked

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
        // Use 1rem (16px) margin on each side like Unfold's container padding
        const margin = 16;
        return {
            width: window.innerWidth - (margin * 2),
            height: window.innerHeight - (margin * 2)
        };
    }

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
        container.style.cssText = `
            background: var(--unfold-bg-color, #fff);
            border-radius: var(--unfold-border-radius, 0.5rem);
            width: ${dimensions.width};
            max-width: ${dimensions.maxWidth};
            height: ${dimensions.height};
            max-height: ${dimensions.maxHeight};
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
     * Create modal header with title, maximize button, and close button
     */
    function createModalHeader() {
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

        // Spacer for symmetry (same width as button group)
        const leftSpacer = document.createElement('div');
        leftSpacer.style.cssText = `
            width: 5rem;
            flex-shrink: 0;
        `;

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

        // Button group (right side)
        const buttonGroup = document.createElement('div');
        buttonGroup.style.cssText = `
            display: flex;
            align-items: center;
            gap: 0.25rem;
            flex-shrink: 0;
        `;

        // Maximize button
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

        // Close button
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
        closeButton.addEventListener('click', closeModal);
        closeButton.addEventListener('mouseenter', function() {
            this.style.background = 'var(--unfold-hover-bg, #f3f4f6)';
        });
        closeButton.addEventListener('mouseleave', function() {
            this.style.background = 'none';
        });

        buttonGroup.appendChild(maximizeButton);
        buttonGroup.appendChild(closeButton);

        header.appendChild(leftSpacer);
        header.appendChild(title);
        header.appendChild(buttonGroup);

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

    /**
     * Open modal with iframe.
     * If a modal is already visible it is hidden and pushed down the stack.
     */
    function openModal(url, iframeName) {
        // Inject dark mode styles on first use
        injectStyles();

        const currentModal = getActiveModal();

        // Hide current modal (don't remove) so it can be restored later
        if (currentModal) {
            currentModal.overlay.style.display = 'none';
        } else {
            // First modal – lock page scroll
            lockScroll();
        }

        // Create modal structure
        const overlay = createModalOverlay();
        const container = createModalContainer();
        const { header, title, maximizeButton } = createModalHeader();
        const iframe = createIframe(url, iframeName);

        container.appendChild(header);
        container.appendChild(iframe);
        overlay.appendChild(container);
        document.body.appendChild(overlay);

        // Track original dimensions for restore from maximize
        const originalDimensions = {
            width: container.style.width,
            maxWidth: container.style.maxWidth,
            height: container.style.height,
            maxHeight: container.style.maxHeight
        };

        // Push onto stack
        const modal = {
            overlay: overlay,
            container: container,
            iframe: iframe,
            iframeName: iframeName,
            title: title,
            maximizeButton: maximizeButton,
            isMaximized: false,
            originalDimensions: originalDimensions
        };
        modalStack.push(modal);

        // Maximize button handler
        maximizeButton.addEventListener('click', function() {
            toggleMaximize(modal);
        });

        // Update title when iframe loads
        iframe.addEventListener('load', function() {
            try {
                const iframeTitle = iframe.contentDocument.title;
                if (iframeTitle) {
                    title.textContent = iframeTitle;
                }
            } catch (e) {
                // Cross-origin – cannot access title
            }
        });

        // Resize tracking via ResizeObserver to enforce max bounds
        if (resizeEnabled) {
            setupResizeTracking(container, modal);
        }

        // Animate in
        requestAnimationFrame(function() {
            overlay.style.opacity = '1';
            container.style.transform = 'scale(1)';
        });

        // Close on overlay click (not container), but not during resize
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay && !isResizing) {
                closeModal();
            }
        });

        // ESC handler – attach once for the first modal
        if (modalStack.length === 1) {
            document.addEventListener('keydown', handleEscKey);
        }
    }

    /**
     * Toggle maximize state for a modal.
     */
    function toggleMaximize(modal) {
        const { container, maximizeButton, originalDimensions } = modal;
        const bounds = getMaximizeBounds();

        if (modal.isMaximized) {
            // Restore to original dimensions
            container.style.width = originalDimensions.width;
            container.style.maxWidth = originalDimensions.maxWidth;
            container.style.height = originalDimensions.height;
            container.style.maxHeight = originalDimensions.maxHeight;
            maximizeButton.title = 'Maximize';
            // Restore icon to maximize (rectangle)
            maximizeButton.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                </svg>
            `;
            modal.isMaximized = false;
        } else {
            // Maximize to bounds
            container.style.width = bounds.width + 'px';
            container.style.maxWidth = 'none';
            container.style.height = bounds.height + 'px';
            container.style.maxHeight = 'none';
            maximizeButton.title = 'Restore';
            // Change icon to restore (overlapping rectangles)
            maximizeButton.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="5" y="7" width="14" height="14" rx="2" ry="2"></rect>
                    <path d="M9 3h10a2 2 0 0 1 2 2v10"></path>
                </svg>
            `;
            modal.isMaximized = true;
        }
    }

    /**
     * Setup resize tracking to prevent overlay close during resize
     * and enforce maximum bounds.
     */
    function setupResizeTracking(container, modal) {
        // Track resize state via mouse events on container edge
        let resizeStartWidth = 0;
        let resizeStartHeight = 0;

        // Detect resize start by watching for mousedown near the resize handle
        container.addEventListener('mousedown', function(e) {
            const rect = container.getBoundingClientRect();
            const nearRight = e.clientX > rect.right - 20;
            const nearBottom = e.clientY > rect.bottom - 20;

            if (nearRight || nearBottom) {
                isResizing = true;
                resizeStartWidth = container.offsetWidth;
                resizeStartHeight = container.offsetHeight;
            }
        });

        // End resize on any mouseup (including over overlay)
        document.addEventListener('mouseup', function() {
            if (isResizing) {
                isResizing = false;
            }
        });

        // Use ResizeObserver to enforce max bounds during resize
        if (typeof ResizeObserver !== 'undefined') {
            const observer = new ResizeObserver(function(entries) {
                for (const entry of entries) {
                    const bounds = getMaximizeBounds();
                    const el = entry.target;

                    // Clamp to maximize bounds
                    if (el.offsetWidth > bounds.width) {
                        el.style.width = bounds.width + 'px';
                    }
                    if (el.offsetHeight > bounds.height) {
                        el.style.height = bounds.height + 'px';
                    }

                    // If resized manually and was maximized, exit maximize state
                    if (modal.isMaximized && isResizing) {
                        modal.isMaximized = false;
                        modal.maximizeButton.title = 'Maximize';
                        modal.maximizeButton.innerHTML = `
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                            </svg>
                        `;
                    }
                }
            });
            observer.observe(container);
        }
    }

    /**
     * Close the active (topmost) modal.
     * If the stack has more modals beneath it, the previous one is restored.
     * Stack UX: Previous modal is shown immediately to avoid flicker.
     */
    function closeModal() {
        if (modalStack.length === 0 || isClosing) return;

        isClosing = true;

        const modalToClose = modalStack.pop();
        const { overlay, container } = modalToClose;
        const previousModal = getActiveModal();

        if (previousModal) {
            // Show previous modal immediately (behind current) to avoid flicker
            previousModal.overlay.style.display = 'flex';
            previousModal.overlay.style.opacity = '1';

            // Only fade out the container, keep overlay visible
            container.style.transform = 'scale(0.95)';
            container.style.opacity = '0';
            container.style.transition = 'transform 0.15s ease-out, opacity 0.1s ease-out';
        } else {
            // Last modal – fade entire overlay
            overlay.style.opacity = '0';
            container.style.transform = 'scale(0.95)';
        }

        // Remove from DOM after animation
        setTimeout(function() {
            if (overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }

            if (!previousModal) {
                // Stack empty – unlock scroll and detach ESC handler
                unlockScroll();
                document.removeEventListener('keydown', handleEscKey);
            }

            isClosing = false;
        }, 150);
    }

    /**
     * Handle ESC key – always closes the topmost modal
     */
    function handleEscKey(e) {
        if (e.key === 'Escape' || e.keyCode === 27) {
            closeModal();
        }
    }

    /**
     * Create a fake window object for Django's dismiss functions.
     */
    function createFakeWindow(modal) {
        let iframeUrl = '';
        try {
            iframeUrl = modal.iframe.contentWindow.location.href;
        } catch (e) {
            // cross-origin or detached – ignore
        }

        return {
            name: modal.iframeName,
            close: closeModal,
            closed: false,
            location: {
                href: iframeUrl,
                pathname: iframeUrl ? new URL(iframeUrl).pathname : ''
            }
        };
    }

    /**
     * Call the appropriate Django dismiss function.
     */
    function callDismissFunction(data, fakeWin) {
        switch (data.type) {
            case 'django:popup:add':
                if (window.dismissAddRelatedObjectPopup) {
                    window.dismissAddRelatedObjectPopup(fakeWin, data.newId, data.newRepr);
                }
                break;

            case 'django:popup:change':
                if (window.dismissChangeRelatedObjectPopup) {
                    window.dismissChangeRelatedObjectPopup(fakeWin, data.objId, data.newRepr, data.newId);
                }
                break;

            case 'django:popup:delete':
                if (window.dismissDeleteRelatedObjectPopup) {
                    window.dismissDeleteRelatedObjectPopup(fakeWin, data.objId);
                }
                break;

            case 'django:popup:lookup':
                if (window.dismissRelatedLookupPopup) {
                    window.dismissRelatedLookupPopup(fakeWin, data.chosenId);
                }
                break;
        }
    }

    // ---------------------------------------------------------------
    // Parent-mode message handling (manages modals on the top page)
    // ---------------------------------------------------------------

    /**
     * Unified message handler for the parent (top-level) page.
     * Handles:
     *   - django:popup:*   – dismiss from an iframe after save/delete
     *   - django:modal:open – nested modal request from an iframe
     */
    function handleParentMessage(event) {
        const data = event.data;
        if (!data || !data.type) return;

        // --- Nested modal request from an iframe ---
        if (data.type === 'django:modal:open') {
            const activeModal = getActiveModal();
            if (!activeModal) return;
            // Only accept from our active modal's iframe
            if (event.source !== activeModal.iframe.contentWindow) return;

            openModal(data.url, data.iframeName);
            return;
        }

        // --- Close request from an iframe (ESC pressed inside iframe) ---
        if (data.type === 'django:modal:close') {
            const activeModal = getActiveModal();
            if (!activeModal) return;
            if (event.source !== activeModal.iframe.contentWindow) return;

            closeModal();
            return;
        }

        // --- Dismiss message from an iframe (popup_response.html / popup_iframe.js) ---
        if (!data.type.startsWith('django:popup:')) return;

        const activeModal = getActiveModal();
        if (!activeModal) return;
        if (event.source !== activeModal.iframe.contentWindow) return;

        if (modalStack.length > 1) {
            // Nested modal completing – close it and forward dismiss to the
            // previous modal's iframe so its widget gets updated.
            const previousModal = modalStack[modalStack.length - 2];

            // Capture the nested modal's URL before closing (Django's dismiss
            // functions use win.location.pathname to derive the model name).
            let popupUrl = '';
            try {
                popupUrl = activeModal.iframe.contentWindow.location.href;
            } catch (e) {
                // cross-origin – ignore
            }

            closeModal();

            // Forward dismiss data into the restored modal's iframe.
            // The iframe is still loaded (was just hidden), so postMessage works.
            try {
                previousModal.iframe.contentWindow.postMessage({
                    type: 'django:modal:dismiss',
                    dismissType: data.type,
                    data: data,
                    iframeName: activeModal.iframeName,
                    popupUrl: popupUrl
                }, window.location.origin);
            } catch (e) {
                // cross-origin guard
            }
        } else {
            // Top-level modal completing – update the parent page's widget.
            const fakeWin = createFakeWindow(activeModal);
            callDismissFunction(data, fakeWin);
        }
    }

    // ---------------------------------------------------------------
    // Iframe-mode handlers (runs inside a modal iframe)
    // ---------------------------------------------------------------

    /**
     * Intercept django:show-related inside an iframe and delegate to parent.
     */
    function handleShowRelatedInIframe(event) {
        event.preventDefault();

        const link = event.currentTarget;
        const href = new URL(link.href);

        if (!href.searchParams.has('_popup')) {
            href.searchParams.set('_popup', '1');
        }

        const name = addPopupIndex(link.id.replace(/^(change|add|delete|view)_/, ''));

        window.parent.postMessage({
            type: 'django:modal:open',
            url: href.toString(),
            iframeName: name
        }, window.location.origin);
    }

    /**
     * Intercept django:lookup-related inside an iframe and delegate to parent.
     */
    function handleLookupRelatedInIframe(event) {
        event.preventDefault();

        const link = event.currentTarget;
        const href = new URL(link.href);

        if (!href.searchParams.has('_popup')) {
            href.searchParams.set('_popup', '1');
        }

        const name = addPopupIndex(link.id.replace(/^lookup_/, ''));

        window.parent.postMessage({
            type: 'django:modal:open',
            url: href.toString(),
            iframeName: name
        }, window.location.origin);
    }

    /**
     * Handle forwarded dismiss messages from the parent page.
     * The parent sends these when a nested modal completes, so the iframe
     * that requested the nested modal can update its own widget.
     */
    function handleForwardedDismiss(event) {
        if (event.source !== window.parent) return;

        const data = event.data;
        if (!data || data.type !== 'django:modal:dismiss') return;

        const popupUrl = data.popupUrl || '';
        const fakeWin = {
            name: data.iframeName,
            close: function() {},
            closed: false,
            location: {
                href: popupUrl,
                pathname: popupUrl ? new URL(popupUrl).pathname : ''
            }
        };

        callDismissFunction(data.data, fakeWin);
    }

    // ---------------------------------------------------------------
    // Parent-mode event handlers (top-level page)
    // ---------------------------------------------------------------

    /**
     * Handle django:show-related event (add/change/view/delete)
     */
    function handleShowRelated(event) {
        event.preventDefault();

        const link = event.currentTarget;
        const href = new URL(link.href);

        if (!href.searchParams.has('_popup')) {
            href.searchParams.set('_popup', '1');
        }

        const name = addPopupIndex(link.id.replace(/^(change|add|delete|view)_/, ''));

        openModal(href.toString(), name);
    }

    /**
     * Handle django:lookup-related event (raw_id_fields)
     */
    function handleLookupRelated(event) {
        event.preventDefault();

        const link = event.currentTarget;
        const href = new URL(link.href);

        if (!href.searchParams.has('_popup')) {
            href.searchParams.set('_popup', '1');
        }

        const name = addPopupIndex(link.id.replace(/^lookup_/, ''));

        openModal(href.toString(), name);
    }

    // ---------------------------------------------------------------
    // Initialization
    // ---------------------------------------------------------------

    /**
     * Initialize modal functionality
     */
    function init($) {
        setPopupIndex();

        if (isInIframe) {
            // Running inside a modal iframe – delegate to parent for nested modals
            $('body').on('django:show-related', '.related-widget-wrapper-link[data-popup="yes"]', handleShowRelatedInIframe);
            $('body').on('django:lookup-related', '.related-lookup', handleLookupRelatedInIframe);

            // Listen for forwarded dismiss results from parent
            window.addEventListener('message', handleForwardedDismiss);

            // Forward ESC key to parent so modal closes even when iframe has focus
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' || e.keyCode === 27) {
                    window.parent.postMessage({
                        type: 'django:modal:close'
                    }, window.location.origin);
                }
            });
        } else {
            // Running on the top-level page – manage the modal stack
            $('body').on('django:show-related', '.related-widget-wrapper-link[data-popup="yes"]', handleShowRelated);
            $('body').on('django:lookup-related', '.related-lookup', handleLookupRelated);

            // Listen for messages from iframes (dismiss + nested open requests)
            window.addEventListener('message', handleParentMessage);
        }
    }

    /**
     * Wait for django.jQuery to be available, then initialize
     */
    function waitForJQuery() {
        if (typeof django !== 'undefined' && typeof django.jQuery !== 'undefined') {
            django.jQuery(document).ready(function() {
                init(django.jQuery);
            });
        } else {
            // Poll every 50ms until django.jQuery is available
            setTimeout(waitForJQuery, 50);
        }
    }

    // Start waiting for jQuery
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', waitForJQuery);
    } else {
        waitForJQuery();
    }

    // Expose for testing/debugging
    window.unfoldModal = {
        open: openModal,
        close: closeModal,
        stackDepth: function() { return modalStack.length; }
    };
})();
