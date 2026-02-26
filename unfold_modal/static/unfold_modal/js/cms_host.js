/**
 * Unfold Modal - CMS Host Module
 *
 * Runs in the CMS parent page (non-admin). Listens for postMessage from
 * child admin iframes and manages modal overlay/container in the parent
 * document. Requires modal_core.js to be loaded first.
 */
'use strict';

(function(Modal) {
    var state = Modal.state;
    var utils = Modal.utils;
    var dom = Modal.dom;
    var MSG = Modal.MSG;
    var ICONS = Modal.ICONS;

    // Use CMS-specific config if available, fall back to base config
    var cmsConfig = (Modal.config && Modal.config.cms) || Modal.config || {};
    var resizeEnabled = cmsConfig.resize || false;
    var disableHeader = cmsConfig.disableHeader !== false;

    // Override modal_core dimensions with CMS config for DOM creation
    var cmsDimensions = cmsConfig.dimensions || {
        width: "98%", maxWidth: "none", height: "95vh", maxHeight: "none"
    };

    // Track which iframe window sent the initial open request
    var originIframeWindow = null;

    // ---------------------------------------------------------------
    // Resize and Maximize
    // ---------------------------------------------------------------

    function toggleMaximize(modal) {
        var container = modal.container;
        var maximizeButton = modal.maximizeButton;
        var bounds = utils.getMaximizeBounds();

        if (modal.isMaximized) {
            container.style.width = modal.preMaximizeDimensions.width;
            container.style.maxWidth = modal.preMaximizeDimensions.maxWidth;
            container.style.height = modal.preMaximizeDimensions.height;
            container.style.maxHeight = modal.preMaximizeDimensions.maxHeight;
            maximizeButton.title = 'Maximize';
            maximizeButton.innerHTML = ICONS.maximize;
            modal.isMaximized = false;
        } else {
            modal.preMaximizeDimensions = {
                width: container.style.width,
                maxWidth: container.style.maxWidth,
                height: container.style.height,
                maxHeight: container.style.maxHeight
            };
            container.style.width = bounds.width + 'px';
            container.style.maxWidth = 'none';
            container.style.height = bounds.height + 'px';
            container.style.maxHeight = 'none';
            maximizeButton.title = 'Restore';
            maximizeButton.innerHTML = ICONS.restore;
            modal.isMaximized = true;
        }
    }

    function setupResizeTracking(container, modal) {
        var observer = null;

        container.addEventListener('mousedown', function(e) {
            var rect = container.getBoundingClientRect();
            if (e.clientX > rect.right - 20 || e.clientY > rect.bottom - 20) {
                state.isResizing = true;
            }
        });

        function handleMouseUp() {
            if (state.isResizing) state.isResizing = false;
        }
        document.addEventListener('mouseup', handleMouseUp);

        function clampToViewport() {
            var bounds = utils.getMaximizeBounds();
            if (container.offsetWidth > bounds.width) container.style.width = bounds.width + 'px';
            if (container.offsetHeight > bounds.height) container.style.height = bounds.height + 'px';
        }

        function handleWindowResize() {
            clampToViewport();
            if (modal.isMaximized) {
                var bounds = utils.getMaximizeBounds();
                container.style.width = bounds.width + 'px';
                container.style.height = bounds.height + 'px';
            }
        }
        window.addEventListener('resize', handleWindowResize);

        if (typeof ResizeObserver !== 'undefined') {
            observer = new ResizeObserver(function() {
                clampToViewport();
                if (modal.isMaximized && state.isResizing) {
                    modal.isMaximized = false;
                    modal.maximizeButton.title = 'Maximize';
                    modal.maximizeButton.innerHTML = ICONS.maximize;
                }
            });
            observer.observe(container);
        }

        return function cleanup() {
            document.removeEventListener('mouseup', handleMouseUp);
            window.removeEventListener('resize', handleWindowResize);
            if (observer) observer.disconnect();
        };
    }

    // ---------------------------------------------------------------
    // Modal Operations
    // ---------------------------------------------------------------

    function handleEscKey(e) {
        if (e.key === 'Escape' || e.keyCode === 27) {
            closeModal();
        }
    }

    /**
     * Create modal container with CMS-specific dimensions.
     * Overrides modal_core.js createContainer to use CMS config.
     */
    function createCmsContainer() {
        var container = document.createElement('div');
        container.className = resizeEnabled
            ? 'unfold-modal-container unfold-modal-resizable'
            : 'unfold-modal-container';

        var hasResizeObserver = typeof ResizeObserver !== 'undefined';
        var initialWidth, initialHeight, maxWidthStyle, maxHeightStyle;

        if (resizeEnabled && hasResizeObserver) {
            var viewportWidth = window.innerWidth;
            var viewportHeight = window.innerHeight;
            var widthPercent = parseFloat(cmsDimensions.width) / 100;
            var calculatedWidth = viewportWidth * widthPercent;
            var maxWidthPx = cmsDimensions.maxWidth === 'none' ? Infinity : parseInt(cmsDimensions.maxWidth);
            initialWidth = Math.min(calculatedWidth, maxWidthPx) + 'px';
            var heightValue = parseFloat(cmsDimensions.height);
            var calculatedHeight = viewportHeight * heightValue / 100;
            var maxHeightPx = cmsDimensions.maxHeight === 'none' ? Infinity : parseInt(cmsDimensions.maxHeight);
            initialHeight = Math.min(calculatedHeight, maxHeightPx) + 'px';
            maxWidthStyle = 'none';
            maxHeightStyle = 'none';
        } else {
            initialWidth = cmsDimensions.width;
            initialHeight = cmsDimensions.height;
            maxWidthStyle = cmsDimensions.maxWidth;
            maxHeightStyle = cmsDimensions.maxHeight;
        }

        container.style.width = initialWidth;
        container.style.maxWidth = maxWidthStyle;
        container.style.height = initialHeight;
        container.style.maxHeight = maxHeightStyle;

        return container;
    }

    function openModal(url, iframeName) {
        var currentModal = utils.getActiveModal();
        var modalStack = state.modalStack;

        if (currentModal) {
            currentModal.overlay.style.display = 'none';
        } else {
            utils.lockScroll();
        }

        var overlay = dom.createOverlay();
        var container = createCmsContainer();
        var headerParts = dom.createHeader(closeModal);
        var iframe = dom.createIframe(url, iframeName);

        container.appendChild(headerParts.header);
        container.appendChild(iframe);
        overlay.appendChild(container);
        document.body.appendChild(overlay);

        var modal = {
            overlay: overlay,
            container: container,
            iframe: iframe,
            iframeName: iframeName,
            title: headerParts.title,
            maximizeButton: headerParts.maximizeButton,
            isMaximized: false,
            preMaximizeDimensions: null
        };
        modalStack.push(modal);

        headerParts.maximizeButton.addEventListener('click', function() {
            toggleMaximize(modal);
        });

        // Update title and optionally hide admin header when iframe loads
        iframe.addEventListener('load', function() {
            try {
                var iframeDoc = iframe.contentDocument;
                var iframeTitle = iframeDoc.title;
                if (iframeTitle) headerParts.title.textContent = iframeTitle;

                if (disableHeader) {
                    var SELECTORS = Modal.SELECTORS;
                    var headerInner = iframeDoc.getElementById(SELECTORS.HEADER_INNER);
                    if (headerInner) {
                        var headerContainer = headerInner;
                        for (var i = 0; i < SELECTORS.HEADER_CONTAINER_DEPTH; i++) {
                            if (headerContainer.parentElement) {
                                headerContainer = headerContainer.parentElement;
                            }
                        }
                        if (headerContainer && headerContainer !== iframeDoc.body) {
                            headerContainer.style.display = 'none';
                        }
                    }
                    var mainContent = iframeDoc.getElementById(SELECTORS.MAIN);
                    if (mainContent) mainContent.style.paddingTop = '1rem';
                }
            } catch (e) {
                // Cross-origin
            }
        });

        if (resizeEnabled) {
            modal.resizeCleanup = setupResizeTracking(container, modal);
        }

        // Animate in
        requestAnimationFrame(function() {
            overlay.style.opacity = '1';
            container.style.transform = 'scale(1)';
        });

        // Overlay click to close
        var mousedownOnOverlay = false;
        overlay.addEventListener('mousedown', function(e) {
            mousedownOnOverlay = (e.target === overlay);
        });
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay && mousedownOnOverlay && !state.isResizing) {
                closeModal();
            }
            mousedownOnOverlay = false;
        });

        if (modalStack.length === 1) {
            document.addEventListener('keydown', handleEscKey);
        }
    }

    function closeModal() {
        var modalStack = state.modalStack;
        if (modalStack.length === 0 || state.isClosing) return;

        state.isClosing = true;

        var modalToClose = modalStack.pop();
        var overlay = modalToClose.overlay;
        var container = modalToClose.container;
        var resizeCleanup = modalToClose.resizeCleanup;
        var previousModal = utils.getActiveModal();

        if (resizeCleanup) resizeCleanup();

        var cleanupDone = false;
        function cleanupAfterClose() {
            if (cleanupDone) return;
            cleanupDone = true;

            if (overlay.parentNode) overlay.parentNode.removeChild(overlay);

            if (!previousModal) {
                utils.unlockScroll();
                document.removeEventListener('keydown', handleEscKey);
            }

            // Clear origin tracking when all modals closed
            if (modalStack.length === 0) {
                originIframeWindow = null;
            }

            state.isClosing = false;
        }

        var animTarget = previousModal ? container : overlay;
        animTarget.addEventListener('transitionend', function onEnd(e) {
            if (e.target === animTarget) {
                animTarget.removeEventListener('transitionend', onEnd);
                cleanupAfterClose();
            }
        });
        setTimeout(cleanupAfterClose, 200);

        if (previousModal) {
            previousModal.overlay.style.display = 'flex';
            previousModal.overlay.style.opacity = '1';
            overlay.style.background = 'transparent';
            container.style.transform = 'scale(0.95)';
            container.style.opacity = '0';
            container.style.transition = 'transform 0.15s ease-out, opacity 0.1s ease-out';
        } else {
            overlay.style.opacity = '0';
            container.style.transform = 'scale(0.95)';
        }
    }

    // ---------------------------------------------------------------
    // Message Handling
    // ---------------------------------------------------------------

    /**
     * Collect same-origin iframe windows from the current document.
     */
    function getChildIframeWindows() {
        var wins = [];
        var iframes = document.querySelectorAll('iframe');
        for (var i = 0; i < iframes.length; i++) {
            try { wins.push(iframes[i].contentWindow); } catch (e) {}
        }
        return wins;
    }

    function handleMessage(event) {
        // Validate origin: only accept same-origin messages
        if (event.origin !== window.location.origin) return;

        var data = event.data;
        if (!data || !data.type) return;

        var activeModal = utils.getActiveModal();
        var modalStack = state.modalStack;

        // Open request from child iframe
        if (data.type === MSG.MODAL_OPEN) {
            if (!activeModal) {
                // First modal – verify sender is a known child iframe
                var knownIframes = getChildIframeWindows();
                if (knownIframes.indexOf(event.source) === -1) return;
                originIframeWindow = event.source;
            } else {
                // Nested modal – must come from active modal's iframe
                if (event.source !== activeModal.iframe.contentWindow) return;
            }
            openModal(data.url, data.iframeName);
            return;
        }

        // Close request (ESC from inside iframe)
        if (data.type === MSG.MODAL_CLOSE) {
            if (!activeModal) return;
            // Accept close from active modal iframe or from origin iframe
            if (event.source !== activeModal.iframe.contentWindow
                && event.source !== originIframeWindow) return;
            closeModal();
            return;
        }

        // Dismiss messages from modal iframe
        if (!data.type.startsWith('django:popup:')) return;
        if (!activeModal) return;
        if (event.source !== activeModal.iframe.contentWindow) return;

        if (modalStack.length > 1) {
            // Nested modal completing – forward to previous modal's iframe
            var previousModal = modalStack[modalStack.length - 2];
            var popupUrl = '';
            try { popupUrl = activeModal.iframe.contentWindow.location.href; } catch (e) {}

            closeModal();

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
            // Top-level modal completing – forward dismiss to origin admin iframe
            var topPopupUrl = '';
            try { topPopupUrl = activeModal.iframe.contentWindow.location.href; } catch (e) {}

            closeModal();

            if (originIframeWindow) {
                try {
                    originIframeWindow.postMessage({
                        type: MSG.MODAL_DISMISS,
                        dismissType: data.type,
                        data: data,
                        iframeName: activeModal.iframeName,
                        popupUrl: topPopupUrl
                    }, window.location.origin);
                } catch (e) {}
            }
        }
    }

    // ---------------------------------------------------------------
    // Initialization
    // ---------------------------------------------------------------

    window.addEventListener('message', handleMessage);

    // Expose public API
    Modal.cmsHost = {
        open: openModal,
        close: closeModal
    };

})(window.UnfoldModal);
