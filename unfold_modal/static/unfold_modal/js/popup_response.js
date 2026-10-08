/**
 * Django Unfold Modal - Popup Response
 *
 * Loaded by admin/popup_response.html. Reports the popup result to its host:
 * the unfold-modal iframe, a real popup window, or Unfold's native modal.
 */
'use strict';
(function() {
    const marker = document.currentScript;
    const initData = JSON.parse(marker.dataset.popupResponse);

    let inUnfoldModalIframe = false;
    try {
        inUnfoldModalIframe = !!window.frameElement
            && window.frameElement.classList.contains('unfold-modal-iframe');
    } catch (e) {
        // Cross-origin parent: not an unfold-modal iframe
    }

    // 1. unfold-modal iframe: hand the result to the modal host via postMessage
    if (inUnfoldModalIframe) {
        let message;

        switch (initData.action) {
            case 'change':
                message = {
                    type: 'django:popup:change',
                    objId: initData.value,
                    newRepr: initData.obj,
                    newId: initData.new_value
                };
                break;

            case 'delete':
                message = {
                    type: 'django:popup:delete',
                    objId: initData.value
                };
                break;

            default:
                // 'add' action
                message = {
                    type: 'django:popup:add',
                    newId: initData.value,
                    newRepr: initData.obj
                };
                break;
        }

        window.parent.postMessage(message, '*');
        return;
    }

    // 2. Real popup window: call opener directly (Unfold >=0.107 replaces
    //    admin/js/popup_response.js with a version that targets window.parent).
    if (window.opener) {
        switch (initData.action) {
            case 'change':
                opener.dismissChangeRelatedObjectPopup(window, initData.value, initData.obj, initData.new_value);
                break;
            case 'delete':
                opener.dismissDeleteRelatedObjectPopup(window, initData.value);
                break;
            default:
                opener.dismissAddRelatedObjectPopup(window, initData.value, initData.obj);
                break;
        }
        return;
    }

    // 3. Anything else (Unfold's native modal iframe): the admin's own script
    const script = document.createElement('script');
    script.src = marker.dataset.adminScript;
    document.body.appendChild(script);
})();
