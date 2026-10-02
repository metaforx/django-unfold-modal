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
    var MSG_POPUP_FILER = (window.UnfoldModal && window.UnfoldModal.MSG)
        ? window.UnfoldModal.MSG.POPUP_FILER
        : 'django:popup:filer';

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

    // django-filer binds .js-dismiss-popup links to window.opener.dismissRelated*LookupPopup().
    // Capture the click before it reaches the link and forward it to the parent instead.
    document.addEventListener('click', function(event) {
        var link = event.target.closest && event.target.closest('.js-dismiss-popup');
        if (!link) return;

        event.preventDefault();
        event.stopPropagation();

        var isFolder = link.classList.contains('js-dismiss-folder');
        window.parent.postMessage({
            type: MSG_POPUP_FILER,
            fn: isFolder ? 'dismissRelatedFolderLookupPopup' : 'dismissRelatedImageLookupPopup',
            args: isFolder
                ? [link.dataset.fileId, link.dataset.label]
                : [link.dataset.fileId, link.dataset.iconUrl, link.dataset.label, link.dataset.changeUrl || '']
        }, window.location.origin);
    }, true);
})();
