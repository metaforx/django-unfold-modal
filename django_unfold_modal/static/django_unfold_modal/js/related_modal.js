/**
 * Django Unfold Modal - Main Module
 *
 * Modal operations, event handling, and Django integration.
 * Requires modal_core.js to be loaded first.
 */
'use strict';

(function(Modal) {
    // Get references from core module
    const state = Modal.state;
    const utils = Modal.utils;
    const dom = Modal.dom;
    const resizeEnabled = Modal.resizeEnabled;
    const MSG = Modal.MSG;
    const ICONS = Modal.ICONS;

    // Prefix patterns for popup name extraction
    const SHOW_RELATED_PREFIX = /^(change|add|delete|view)_/;
    const LOOKUP_PREFIX = /^lookup_/;

    // ---------------------------------------------------------------
    // Resize and Maximize
    // ---------------------------------------------------------------

    /**
     * Toggle maximize state for a modal.
     */
    function toggleMaximize(modal) {
        const { container, maximizeButton } = modal;
        const bounds = utils.getMaximizeBounds();

        if (modal.isMaximized) {
            // Restore to pre-maximize dimensions
            container.style.width = modal.preMaximizeDimensions.width;
            container.style.maxWidth = modal.preMaximizeDimensions.maxWidth;
            container.style.height = modal.preMaximizeDimensions.height;
            container.style.maxHeight = modal.preMaximizeDimensions.maxHeight;
            maximizeButton.title = 'Maximize';
            maximizeButton.innerHTML = ICONS.maximize;
            modal.isMaximized = false;
        } else {
            // Capture current dimensions before maximizing
            modal.preMaximizeDimensions = {
                width: container.style.width,
                maxWidth: container.style.maxWidth,
                height: container.style.height,
                maxHeight: container.style.maxHeight
            };
            // Maximize to bounds
            container.style.width = bounds.width + 'px';
            container.style.maxWidth = 'none';
            container.style.height = bounds.height + 'px';
            container.style.maxHeight = 'none';
            maximizeButton.title = 'Restore';
            maximizeButton.innerHTML = ICONS.restore;
            modal.isMaximized = true;
        }
    }

    /**
     * Setup resize tracking to prevent overlay close during resize
     * and enforce maximum bounds.
     */
    function setupResizeTracking(container, modal) {
        let observer = null;

        // Detect resize start by watching for mousedown near the resize handle
        container.addEventListener('mousedown', function(e) {
            const rect = container.getBoundingClientRect();
            const nearRight = e.clientX > rect.right - 20;
            const nearBottom = e.clientY > rect.bottom - 20;

            if (nearRight || nearBottom) {
                state.isResizing = true;
            }
        });

        // End resize on any mouseup
        function handleMouseUp() {
            if (state.isResizing) {
                state.isResizing = false;
            }
        }
        document.addEventListener('mouseup', handleMouseUp);

        // Clamp modal to viewport bounds
        function clampToViewport() {
            const bounds = utils.getMaximizeBounds();

            if (container.offsetWidth > bounds.width) {
                container.style.width = bounds.width + 'px';
            }
            if (container.offsetHeight > bounds.height) {
                container.style.height = bounds.height + 'px';
            }
        }

        // Handle window resize - clamp modal if viewport shrinks
        function handleWindowResize() {
            clampToViewport();

            // Update maximized modal to new bounds
            if (modal.isMaximized) {
                const bounds = utils.getMaximizeBounds();
                container.style.width = bounds.width + 'px';
                container.style.height = bounds.height + 'px';
            }
        }
        window.addEventListener('resize', handleWindowResize);

        // Use ResizeObserver to enforce max bounds during user resize
        if (typeof ResizeObserver !== 'undefined') {
            observer = new ResizeObserver(function(entries) {
                for (const entry of entries) {
                    clampToViewport();

                    // If resized manually and was maximized, exit maximize state
                    if (modal.isMaximized && state.isResizing) {
                        modal.isMaximized = false;
                        modal.maximizeButton.title = 'Maximize';
                        modal.maximizeButton.innerHTML = ICONS.maximize;
                    }
                }
            });
            observer.observe(container);
        }

        // Return cleanup function
        return function cleanup() {
            document.removeEventListener('mouseup', handleMouseUp);
            window.removeEventListener('resize', handleWindowResize);
            if (observer) {
                observer.disconnect();
            }
        };
    }

    // ---------------------------------------------------------------
    // Modal Operations
    // ---------------------------------------------------------------

    /**
     * Handle ESC key – always closes the topmost modal
     */
    function handleEscKey(e) {
        if (e.key === 'Escape' || e.keyCode === 27) {
            closeModal();
        }
    }

    /**
     * Open modal with iframe.
     * If a modal is already visible it is hidden and pushed down the stack.
     */
    function openModal(url, iframeName) {
        // Inject dark mode styles on first use
        Modal.injectStyles();

        const currentModal = utils.getActiveModal();
        const modalStack = state.modalStack;

        // Hide current modal (don't remove) so it can be restored later
        if (currentModal) {
            currentModal.overlay.style.display = 'none';
        } else {
            // First modal – lock page scroll
            utils.lockScroll();
        }

        // Create modal structure
        const overlay = dom.createOverlay();
        const container = dom.createContainer();
        const { header, title, maximizeButton } = dom.createHeader(closeModal);
        const iframe = dom.createIframe(url, iframeName);

        container.appendChild(header);
        container.appendChild(iframe);
        overlay.appendChild(container);
        document.body.appendChild(overlay);

        // Push onto stack
        const modal = {
            overlay: overlay,
            container: container,
            iframe: iframe,
            iframeName: iframeName,
            title: title,
            maximizeButton: maximizeButton,
            isMaximized: false,
            preMaximizeDimensions: null
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

        // Resize tracking
        if (resizeEnabled) {
            modal.resizeCleanup = setupResizeTracking(container, modal);
        }

        // Animate in
        requestAnimationFrame(function() {
            overlay.style.opacity = '1';
            container.style.transform = 'scale(1)';
        });

        // Track mousedown on overlay itself (not bubbled from children)
        let mousedownOnOverlay = false;
        overlay.addEventListener('mousedown', function(e) {
            mousedownOnOverlay = (e.target === overlay);
        });

        // Close on overlay click only if mousedown was also on overlay
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay && mousedownOnOverlay && !state.isResizing) {
                closeModal();
            }
            mousedownOnOverlay = false;
        });

        // ESC handler – attach once for the first modal
        if (modalStack.length === 1) {
            document.addEventListener('keydown', handleEscKey);
        }
    }

    /**
     * Close the active (topmost) modal.
     * If the stack has more modals beneath it, the previous one is restored.
     */
    function closeModal() {
        const modalStack = state.modalStack;

        if (modalStack.length === 0 || state.isClosing) return;

        state.isClosing = true;

        const modalToClose = modalStack.pop();
        const { overlay, container, resizeCleanup } = modalToClose;
        const previousModal = utils.getActiveModal();

        // Clean up resize tracking if present
        if (resizeCleanup) {
            resizeCleanup();
        }

        // Cleanup function to run after animation completes
        let cleanupDone = false;
        function cleanupAfterClose() {
            if (cleanupDone) return;
            cleanupDone = true;

            if (overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }

            if (!previousModal) {
                // Stack empty – unlock scroll and detach ESC handler
                utils.unlockScroll();
                document.removeEventListener('keydown', handleEscKey);
            }

            state.isClosing = false;
        }

        // Listen for transition end on the element that animates
        const animTarget = previousModal ? container : overlay;
        animTarget.addEventListener('transitionend', function onEnd(e) {
            // Only trigger on the expected property to avoid double-fires
            if (e.target === animTarget) {
                animTarget.removeEventListener('transitionend', onEnd);
                cleanupAfterClose();
            }
        });

        // Fallback: cleanup if transitionend doesn't fire (e.g., prefers-reduced-motion)
        setTimeout(cleanupAfterClose, 200);

        if (previousModal) {
            // Show previous modal immediately to avoid flicker
            previousModal.overlay.style.display = 'flex';
            previousModal.overlay.style.opacity = '1';

            // Make closing modal's overlay transparent
            overlay.style.background = 'transparent';

            // Only fade out the container
            container.style.transform = 'scale(0.95)';
            container.style.opacity = '0';
            container.style.transition = 'transform 0.15s ease-out, opacity 0.1s ease-out';
        } else {
            // Last modal – fade entire overlay
            overlay.style.opacity = '0';
            container.style.transform = 'scale(0.95)';
        }
    }

    // ---------------------------------------------------------------
    // Django Integration
    // ---------------------------------------------------------------

    /**
     * Create a fake window object for Django's dismiss functions.
     */
    function createFakeWindow(modal) {
        let iframeUrl = '';
        try {
            iframeUrl = modal.iframe.contentWindow.location.href;
        } catch (e) {
            // cross-origin or detached
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
            case MSG.POPUP_ADD:
                if (window.dismissAddRelatedObjectPopup) {
                    window.dismissAddRelatedObjectPopup(fakeWin, data.newId, data.newRepr);
                }
                break;
            case MSG.POPUP_CHANGE:
                if (window.dismissChangeRelatedObjectPopup) {
                    window.dismissChangeRelatedObjectPopup(fakeWin, data.objId, data.newRepr, data.newId);
                }
                break;
            case MSG.POPUP_DELETE:
                if (window.dismissDeleteRelatedObjectPopup) {
                    window.dismissDeleteRelatedObjectPopup(fakeWin, data.objId);
                }
                break;
            case MSG.POPUP_LOOKUP:
                if (window.dismissRelatedLookupPopup) {
                    window.dismissRelatedLookupPopup(fakeWin, data.chosenId);
                }
                break;
        }
    }

    // ---------------------------------------------------------------
    // Parent-mode Message Handling
    // ---------------------------------------------------------------

    /**
     * Unified message handler for the parent (top-level) page.
     */
    function handleParentMessage(event) {
        const data = event.data;
        if (!data || !data.type) return;

        const activeModal = utils.getActiveModal();
        const modalStack = state.modalStack;

        // Nested modal request from an iframe
        if (data.type === MSG.MODAL_OPEN) {
            if (!activeModal) return;
            if (event.source !== activeModal.iframe.contentWindow) return;
            openModal(data.url, data.iframeName);
            return;
        }

        // Close request from an iframe (ESC pressed inside iframe)
        if (data.type === MSG.MODAL_CLOSE) {
            if (!activeModal) return;
            if (event.source !== activeModal.iframe.contentWindow) return;
            closeModal();
            return;
        }

        // Dismiss message from an iframe
        if (!data.type.startsWith('django:popup:')) return;
        if (!activeModal) return;
        if (event.source !== activeModal.iframe.contentWindow) return;

        if (modalStack.length > 1) {
            // Nested modal completing
            const previousModal = modalStack[modalStack.length - 2];
            let popupUrl = '';
            try {
                popupUrl = activeModal.iframe.contentWindow.location.href;
            } catch (e) {}

            closeModal();

            // Forward dismiss data to the restored modal's iframe
            try {
                previousModal.iframe.contentWindow.postMessage({
                    type: MSG.MODAL_DISMISS,
                    dismissType: data.type,
                    data: data,
                    iframeName: activeModal.iframeName,
                    popupUrl: popupUrl
                }, window.location.origin);
            } catch (e) {}
        } else {
            // Top-level modal completing
            const fakeWin = createFakeWindow(activeModal);
            callDismissFunction(data, fakeWin);
        }
    }

    // ---------------------------------------------------------------
    // Iframe-mode Handlers
    // ---------------------------------------------------------------

    /**
     * Intercept django:show-related inside an iframe and delegate to parent.
     */
    function handleShowRelatedInIframe(event) {
        event.preventDefault();

        const link = event.currentTarget;
        const url = utils.ensurePopupParam(link.href);
        const name = utils.getPopupName(link.id, SHOW_RELATED_PREFIX);

        window.parent.postMessage({
            type: MSG.MODAL_OPEN,
            url: url.toString(),
            iframeName: name
        }, window.location.origin);
    }

    /**
     * Intercept django:lookup-related inside an iframe and delegate to parent.
     */
    function handleLookupRelatedInIframe(event) {
        event.preventDefault();

        const link = event.currentTarget;
        const url = utils.ensurePopupParam(link.href);
        const name = utils.getPopupName(link.id, LOOKUP_PREFIX);

        window.parent.postMessage({
            type: MSG.MODAL_OPEN,
            url: url.toString(),
            iframeName: name
        }, window.location.origin);
    }

    /**
     * Handle forwarded dismiss messages from the parent page.
     */
    function handleForwardedDismiss(event) {
        if (event.source !== window.parent) return;

        const data = event.data;
        if (!data || data.type !== MSG.MODAL_DISMISS) return;

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
    // Parent-mode Event Handlers
    // ---------------------------------------------------------------

    /**
     * Handle django:show-related event (add/change/view/delete)
     */
    function handleShowRelated(event) {
        event.preventDefault();

        const link = event.currentTarget;
        const url = utils.ensurePopupParam(link.href);
        const name = utils.getPopupName(link.id, SHOW_RELATED_PREFIX);

        openModal(url.toString(), name);
    }

    /**
     * Handle django:lookup-related event (raw_id_fields)
     */
    function handleLookupRelated(event) {
        event.preventDefault();

        const link = event.currentTarget;
        const url = utils.ensurePopupParam(link.href);
        const name = utils.getPopupName(link.id, LOOKUP_PREFIX);

        openModal(url.toString(), name);
    }

    // ---------------------------------------------------------------
    // Initialization
    // ---------------------------------------------------------------

    /**
     * Initialize modal functionality
     */
    function init($) {
        utils.setPopupIndex();

        if (state.isInIframe) {
            // Running inside a modal iframe
            $('body').on('django:show-related', '.related-widget-wrapper-link[data-popup="yes"]', handleShowRelatedInIframe);
            $('body').on('django:lookup-related', '.related-lookup', handleLookupRelatedInIframe);

            window.addEventListener('message', handleForwardedDismiss);

            // Forward ESC key to parent
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' || e.keyCode === 27) {
                    window.parent.postMessage({ type: MSG.MODAL_CLOSE }, window.location.origin);
                }
            });
        } else {
            // Running on the top-level page
            $('body').on('django:show-related', '.related-widget-wrapper-link[data-popup="yes"]', handleShowRelated);
            $('body').on('django:lookup-related', '.related-lookup', handleLookupRelated);

            window.addEventListener('message', handleParentMessage);
        }
    }

    /**
     * Initialize when django.jQuery is available.
     * Single-path initialization: poll for django.jQuery, then call init.
     */
    function initWhenReady() {
        if (typeof django !== 'undefined' && typeof django.jQuery !== 'undefined') {
            init(django.jQuery);
        } else {
            // Poll until django.jQuery is available (Django admin loads it async)
            setTimeout(initWhenReady, 50);
        }
    }

    // Start initialization after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWhenReady);
    } else {
        initWhenReady();
    }

    // Expose public API via UnfoldModal namespace
    Modal.open = openModal;
    Modal.close = closeModal;
    Modal.stackDepth = function() { return state.modalStack.length; };

})(window.UnfoldModal);
