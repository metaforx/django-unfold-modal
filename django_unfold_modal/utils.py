"""Utility functions for django-unfold-modal."""

from django.templatetags.static import static
from django.urls import reverse


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
        The config script must be included before the modal script so that
        window.UNFOLD_MODAL_CONFIG is available when related_modal.js runs.
    """
    return [
        # Config script (dynamic, sets window.UNFOLD_MODAL_CONFIG)
        lambda request: reverse("django_unfold_modal:config_js"),
        # Main modal script
        lambda request: static("django_unfold_modal/js/related_modal.js"),
        # Popup iframe script
        lambda request: static("django_unfold_modal/js/popup_iframe.js"),
    ]
