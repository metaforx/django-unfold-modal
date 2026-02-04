"""Utility functions for django-unfold-modal."""

from django.templatetags.static import static


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
    """
    return [
        lambda request: static("django_unfold_modal/js/related_modal.js"),
        lambda request: static("django_unfold_modal/js/popup_iframe.js"),
    ]
