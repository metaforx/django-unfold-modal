"""Utility functions for django-unfold-modal."""

from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse


def _get_config_url(request):
    """
    Get the URL for the modal config JS endpoint.

    Returns the reverse URL if the app's URLs are included in ROOT_URLCONF,
    otherwise returns None (config script is skipped, modal uses defaults).
    """
    try:
        return reverse("django_unfold_modal:config_js")
    except NoReverseMatch:
        # App URLs not included - config.js won't be loaded, modal uses defaults
        return None


def get_modal_scripts():
    """
    Return a list of script callables for the modal JavaScript files.

    This is the single source of truth for modal script paths. Use this in
    UNFOLD["SCRIPTS"] configuration to avoid hardcoding static paths.

    Returns:
        list: List of callables matching Unfold's SCRIPTS format.
              Each callable takes a request and returns a static URL.

    Example:
        from django_unfold_modal.utils import get_modal_scripts

        UNFOLD = {
            "SCRIPTS": [
                *get_modal_scripts(),
            ],
        }

    Note:
        For custom size presets (UNFOLD_MODAL_SIZE) or resize functionality
        (UNFOLD_MODAL_RESIZE), include the app's URLs in your ROOT_URLCONF:

            path("unfold-modal/", include("django_unfold_modal.urls")),

        Without this, the modal will use default dimensions.
    """
    return [
        # Config script (dynamic, sets window.UNFOLD_MODAL_CONFIG)
        # Returns None if app URLs not included, which Unfold filters out
        _get_config_url,
        # Main modal script
        lambda request: static("django_unfold_modal/js/related_modal.js"),
        # Popup iframe script
        lambda request: static("django_unfold_modal/js/popup_iframe.js"),
    ]
