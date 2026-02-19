'use strict';
(function() {
    // Only run in iframe mode (no opener, has parent)
    if (window.opener || !window.parent || window.parent === window) {
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
