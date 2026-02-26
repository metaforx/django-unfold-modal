'use strict';
(function() {
    // Only run inside an Unfold modal iframe (not any iframe, e.g. CMS sideframe)
    var isInModalIframe = false;
    try {
        isInModalIframe = (window.parent !== window)
            && !window.opener
            && window.frameElement
            && window.frameElement.classList.contains('unfold-modal-iframe');
    } catch (e) {
        // Cross-origin: frameElement access throws; not our modal iframe
    }
    if (!isInModalIframe) {
        return;
    }

    // Get message type from core module if available, fallback for safety
    var MSG_POPUP_LOOKUP = (window.UnfoldModal && window.UnfoldModal.MSG)
        ? window.UnfoldModal.MSG.POPUP_LOOKUP
        : 'django:popup:lookup';

    document.addEventListener('DOMContentLoaded', function() {
        document.body.addEventListener('click', function(event) {
            var link = event.target.closest('a[data-popup-opener]');
            if (!link) return;

            event.preventDefault();
            window.parent.postMessage({
                type: MSG_POPUP_LOOKUP,
                chosenId: link.dataset.popupOpener
            }, window.location.origin);
        });
    });
})();
