/**
 * Unfold Modal - CMS Host Bridge
 *
 * Thin bridge for CMS parent pages. Listens for postMessage from child
 * admin iframes and delegates modal lifecycle to Modal.open / Modal.close
 * (provided by related_modal.js). Requires modal_core.js and
 * related_modal.js to be loaded first.
 */
'use strict';

(function(Modal) {
    var MSG = Modal.MSG;
    var utils = Modal.utils;
    var state = Modal.state;

    // Track which iframe window sent the initial open request
    var originIframeWindow = null;

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
            Modal.open(data.url, data.iframeName);
            return;
        }

        // Close request (ESC from inside iframe)
        if (data.type === MSG.MODAL_CLOSE) {
            if (!activeModal) return;
            // Accept close from active modal iframe or from origin iframe
            if (event.source !== activeModal.iframe.contentWindow
                && event.source !== originIframeWindow) return;
            Modal.close();
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

            Modal.close();

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

            Modal.close();

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
                originIframeWindow = null;
            }
        }
    }

    window.addEventListener('message', handleMessage);

    // Expose for capability detection from child iframes
    Modal.cmsHost = {
        open: Modal.open,
        close: Modal.close
    };

})(window.UnfoldModal);
