"""Utility functions for django-unfold-modal."""

from django.templatetags.static import static
from django.urls import reverse


def get_modal_styles():
    """
    Return a list of style callables for the modal CSS file.

    This is the single source of truth for modal stylesheet paths. Use this in
    UNFOLD["STYLES"] configuration.

    Returns:
        list: List of callables matching Unfold's STYLES format.
              Each callable takes a request and returns a static URL.

    Example:
        from django_unfold_modal.utils import get_modal_styles

        UNFOLD = {
            "STYLES": [
                *get_modal_styles(),
            ],
        }
    """
    return [
        lambda request: static("django_unfold_modal/css/modal.css"),
    ]


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
        # Core module (state, utilities, DOM creation) - must load first
        lambda request: static("django_unfold_modal/js/modal_core.js"),
        # Main modal script
        lambda request: static("django_unfold_modal/js/related_modal.js"),
        # Popup iframe script
        lambda request: static("django_unfold_modal/js/popup_iframe.js"),
    ]


def get_modal_scripts_with_config():
    """
    Return modal scripts including the config endpoint.

    Use this instead of get_modal_scripts() when you have included the
    app's URLs in your ROOT_URLCONF:

        path("unfold-modal/", include("django_unfold_modal.urls")),

    This enables custom size presets (UNFOLD_MODAL_SIZE) and resize
    functionality (UNFOLD_MODAL_RESIZE).

    Example:
        from django_unfold_modal.utils import get_modal_scripts_with_config

        UNFOLD = {
            "SCRIPTS": [
                *get_modal_scripts_with_config(),
            ],
        }
    """
    return [
        # Config script (dynamic, sets window.UNFOLD_MODAL_CONFIG)
        lambda request: reverse("django_unfold_modal:config_js"),
        # Core module (state, utilities, DOM creation) - must load first
        lambda request: static("django_unfold_modal/js/modal_core.js"),
        # Main modal script
        lambda request: static("django_unfold_modal/js/related_modal.js"),
        # Popup iframe script
        lambda request: static("django_unfold_modal/js/popup_iframe.js"),
    ]
