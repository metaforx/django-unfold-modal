'use strict';
(function() {
    // Only run in iframe mode (no opener, has parent)
    if (window.opener || !window.parent || window.parent === window) {
        return;
    }

    document.addEventListener('DOMContentLoaded', function() {
        document.body.addEventListener('click', function(event) {
            const link = event.target.closest('a[data-popup-opener]');
            if (!link) return;

            event.preventDefault();
            window.parent.postMessage({
                type: 'django:popup:lookup',
                chosenId: link.dataset.popupOpener
            }, window.location.origin);
        });
    });
})();
