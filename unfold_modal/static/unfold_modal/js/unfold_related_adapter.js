/**
 * Django Unfold Modal - Related Click Adapter
 *
 * Unfold >=0.107 claims related-link clicks at document capture phase. This
 * takes them earlier (window capture) and re-triggers Django's related events,
 * so related_modal.js keeps handling them. With UNFOLD_MODAL_OVERRIDE_NATIVE
 * off, the script URL ends in `#coexist` and only owned clicks are taken.
 */
'use strict';
(function() {
    // Register only once, even if the script is included twice.
    window.UnfoldModal = window.UnfoldModal || {};
    if (window.UnfoldModal._relatedAdapterInstalled) {
        return;
    }
    window.UnfoldModal._relatedAdapterInstalled = true;

    const script = document.currentScript;
    const coexist = !!script && /#coexist$/.test(script.src);
    window.UnfoldModal.overrideNative = !coexist;

    // The view link has no data-popup="yes"; related_modal.js adds _popup=1.
    const SHOW = '.related-widget-wrapper-link[data-popup="yes"], '
        + '.related-widget-wrapper-link.view-related';
    const LOOKUP = '.related-lookup';
    // django-filer widgets stay ours: their picker reports back via popup_iframe.js.
    const FILER = '.filerFile .related-lookup';

    function findLink(event) {
        if (event.button !== 0) return null;
        const target = event.target;
        if (!target || typeof target.closest !== 'function') return null;
        return target.closest(SHOW + ', ' + LOOKUP);
    }

    function isOwned(link) {
        if (!coexist) return true;
        const state = window.UnfoldModal.state; // set by modal_core.js
        return !!(state && (state.isInIframe || state.isInCmsModal))
            || link.matches(FILER);
    }

    function forward(event, link) {
        const $ = window.django && window.django.jQuery;
        if (!$) return; // Django admin JS not loaded yet: leave the click untouched

        const isLookup = link.matches(LOOKUP);

        event.preventDefault();
        event.stopPropagation();

        if (!isLookup && !link.href) return; // disabled link, same outcome as Django's handler

        const relatedEvent = isLookup
            ? $.Event('django:lookup-related')
            : $.Event('django:show-related', { href: link.href });
        $(link).trigger(relatedEvent);

        if (relatedEvent.isDefaultPrevented()) return;

        // Nobody handled the event: fall back to Django's stock behaviour.
        if (isLookup) {
            if (typeof window.showRelatedObjectLookupPopup === 'function') {
                window.showRelatedObjectLookupPopup(link);
            }
        } else if (link.matches('[data-popup="yes"]')) {
            if (typeof window.showRelatedObjectPopup === 'function') {
                window.showRelatedObjectPopup(link);
            }
        } else {
            window.location.assign(link.href); // view link: plain navigation
        }
    }

    window.addEventListener('click', function(event) {
        const link = findLink(event);
        if (link && isOwned(link)) forward(event, link);
    }, true);

    if (coexist) {
        // Bubble phase: only clicks that neither Unfold nor Django claimed.
        window.addEventListener('click', function(event) {
            const link = findLink(event);
            if (link && !event.defaultPrevented) forward(event, link);
        });
    }
})();
