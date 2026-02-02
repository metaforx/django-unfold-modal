/**
 * Django Unfold Modal - Related Object Modal
 *
 * Replaces Django admin popup windows with Unfold-styled modals using iframes.
 * Listens for django:show-related and django:lookup-related events and prevents
 * the default popup behavior.
 */
'use strict';

(function() {
    const $ = django.jQuery;

    // Track popup index for nested popups (matches Django's scheme)
    let popupIndex = 0;

    // Modal state
    let activeModal = null;
    let scrollbarWidth = 0;
    let savedScrollStyles = null;

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
     * Lock body scroll without page jump
     */
    function lockScroll() {
        // Save current scroll styles before modifying
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
     * Unlock body scroll
     */
    function unlockScroll() {
        // Restore saved scroll styles instead of just clearing them
        if (savedScrollStyles) {
            document.body.style.overflow = savedScrollStyles.overflow;
            document.body.style.paddingRight = savedScrollStyles.paddingRight;
            savedScrollStyles = null;
        }
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
            width: 90%;
            max-width: 900px;
            height: 85vh;
            max-height: 700px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            transform: scale(0.95);
            transition: transform 0.15s ease-out;
        `;
        return container;
    }

    /**
     * Create modal header with close button
     */
    function createModalHeader() {
        const header = document.createElement('div');
        header.className = 'unfold-modal-header';
        header.style.cssText = `
            display: flex;
            justify-content: flex-end;
            padding: 0.5rem;
            border-bottom: 1px solid var(--unfold-border-color, #e5e7eb);
            flex-shrink: 0;
        `;

        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'unfold-modal-close';
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

        header.appendChild(closeButton);
        return header;
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
     * Open modal with iframe
     */
    function openModal(url, iframeName) {
        // Close any existing modal
        if (activeModal) {
            closeModal();
        }

        // Create modal structure
        const overlay = createModalOverlay();
        const container = createModalContainer();
        const header = createModalHeader();
        const iframe = createIframe(url, iframeName);

        container.appendChild(header);
        container.appendChild(iframe);
        overlay.appendChild(container);
        document.body.appendChild(overlay);

        // Lock scroll
        lockScroll();

        // Store reference
        activeModal = {
            overlay: overlay,
            container: container,
            iframe: iframe,
            iframeName: iframeName
        };

        // Animate in
        requestAnimationFrame(function() {
            overlay.style.opacity = '1';
            container.style.transform = 'scale(1)';
        });

        // Close on overlay click (not container)
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                closeModal();
            }
        });

        // Close on ESC
        document.addEventListener('keydown', handleEscKey);
    }

    /**
     * Close modal
     */
    function closeModal() {
        if (!activeModal) return;

        const { overlay, container } = activeModal;
        const modalToClose = activeModal;

        // Animate out
        overlay.style.opacity = '0';
        container.style.transform = 'scale(0.95)';

        // Remove after animation
        setTimeout(function() {
            if (overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }
            unlockScroll();
            // Only clear activeModal if it's still the same modal instance
            if (activeModal === modalToClose) {
                activeModal = null;
            }
        }, 150);

        // Remove ESC listener
        document.removeEventListener('keydown', handleEscKey);
    }

    /**
     * Handle ESC key
     */
    function handleEscKey(e) {
        if (e.key === 'Escape' || e.keyCode === 27) {
            closeModal();
        }
    }

    /**
     * Create a fake window object for Django's dismiss functions
     * This allows us to reuse Django's existing dismiss* functions
     */
    function createFakeWindow(iframeName) {
        return {
            name: iframeName,
            close: closeModal,
            closed: false
        };
    }

    /**
     * Handle postMessage from iframe (popup_response.html)
     */
    function handlePopupMessage(event) {
        // Verify message is from our iframe
        if (!activeModal) return;

        // Validate that event.source matches activeModal.iframe.contentWindow
        if (event.source !== activeModal.iframe.contentWindow) return;

        const data = event.data;
        if (!data || !data.type || !data.type.startsWith('django:popup:')) return;

        const fakeWin = createFakeWindow(activeModal.iframeName);

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

    /**
     * Handle django:show-related event (add/change/view/delete)
     */
    function handleShowRelated(event) {
        event.preventDefault();

        const link = event.currentTarget;
        const href = new URL(link.href);

        // Ensure _popup parameter is set
        if (!href.searchParams.has('_popup')) {
            href.searchParams.set('_popup', '1');
        }

        // Generate iframe name matching Django's scheme
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

        // Ensure _popup parameter is set
        if (!href.searchParams.has('_popup')) {
            href.searchParams.set('_popup', '1');
        }

        // Generate iframe name matching Django's scheme
        const name = addPopupIndex(link.id.replace(/^lookup_/, ''));

        openModal(href.toString(), name);
    }

    /**
     * Initialize modal functionality
     */
    function init() {
        setPopupIndex();

        // Listen for Django's related object events and prevent default popup
        $('body').on('django:show-related', '.related-widget-wrapper-link[data-popup="yes"]', handleShowRelated);
        $('body').on('django:lookup-related', '.related-lookup', handleLookupRelated);

        // Listen for postMessage from iframe
        window.addEventListener('message', handlePopupMessage);
    }

    // Initialize when DOM is ready
    $(document).ready(init);

    // Expose for testing/debugging
    window.unfoldModal = {
        open: openModal,
        close: closeModal
    };
})();
