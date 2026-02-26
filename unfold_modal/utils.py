"""Utility functions for unfold-modal."""

import json

from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe


def get_modal_styles():
    """
    Return a list of style callables for the modal CSS file.

    This is the single source of truth for modal stylesheet paths. Use this in
    UNFOLD["STYLES"] configuration.

    Returns:
        list: List of callables matching Unfold's STYLES format.
              Each callable takes a request and returns a static URL.

    Example:
        from unfold_modal.utils import get_modal_styles

        UNFOLD = {
            "STYLES": [
                *get_modal_styles(),
            ],
        }
    """
    return [
        lambda request: static("unfold_modal/css/modal.css"),
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
        from unfold_modal.utils import get_modal_scripts

        UNFOLD = {
            "SCRIPTS": [
                *get_modal_scripts(),
            ],
        }

    Note:
        For custom size presets (UNFOLD_MODAL_SIZE) or resize functionality
        (UNFOLD_MODAL_RESIZE), include the app's URLs in your ROOT_URLCONF:

            path("unfold-modal/", include("unfold_modal.urls")),

        Without this, the modal will use default dimensions.
    """
    return [
        # Core module (state, utilities, DOM creation) - must load first
        lambda request: static("unfold_modal/js/modal_core.js"),
        # Main modal script
        lambda request: static("unfold_modal/js/related_modal.js"),
        # Popup iframe script
        lambda request: static("unfold_modal/js/popup_iframe.js"),
    ]


def get_modal_scripts_with_config():
    """
    Return modal scripts including the config endpoint.

    Use this instead of get_modal_scripts() when you have included the
    app's URLs in your ROOT_URLCONF:

        path("unfold-modal/", include("unfold_modal.urls")),

    This enables custom size presets (UNFOLD_MODAL_SIZE) and resize
    functionality (UNFOLD_MODAL_RESIZE).

    Example:
        from unfold_modal.utils import get_modal_scripts_with_config

        UNFOLD = {
            "SCRIPTS": [
                *get_modal_scripts_with_config(),
            ],
        }
    """
    return [
        # Config script (dynamic, sets window.UNFOLD_MODAL_CONFIG)
        lambda request: reverse("unfold_modal:config_js"),
        # Core module (state, utilities, DOM creation) - must load first
        lambda request: static("unfold_modal/js/modal_core.js"),
        # Main modal script
        lambda request: static("unfold_modal/js/related_modal.js"),
        # Popup iframe script
        lambda request: static("unfold_modal/js/popup_iframe.js"),
    ]


def get_cms_modal_head_html():
    """
    Return HTML string with all required assets for CMS parent-window modal hosting.

    Use this in non-template contexts (e.g., inline views) where template tags
    are not available. For Django templates, prefer the ``{% unfold_modal_cms_head %}``
    template tag.

    Returns:
        SafeString: HTML containing ``<link>``, inline config ``<script>``, and
        ``<script src>`` tags for CMS modal hosting.

    Example::

        from unfold_modal.utils import get_cms_modal_head_html

        html = f"<head>{get_cms_modal_head_html()}</head>"
    """
    from unfold_modal.apps import UnfoldModalConfig, get_setting

    presets = UnfoldModalConfig.SIZE_PRESETS
    cms_size = get_setting("UNFOLD_CMS_MODAL_SIZE")
    cms_resize = get_setting("UNFOLD_CMS_MODAL_RESIZE")
    cms_disable_header = get_setting("UNFOLD_CMS_MODAL_DISABLE_HEADER")
    cms_dimensions = presets.get(cms_size, presets["full"])

    config = {
        "size": cms_size,
        "dimensions": cms_dimensions,
        "resize": cms_resize,
        "disableHeader": cms_disable_header,
        "cms": {
            "size": cms_size,
            "dimensions": cms_dimensions,
            "resize": cms_resize,
            "disableHeader": cms_disable_header,
        },
    }

    css_url = static("unfold_modal/css/modal.css")
    core_js_url = static("unfold_modal/js/modal_core.js")
    host_js_url = static("unfold_modal/js/cms_host.js")

    return mark_safe(
        f'<link rel="stylesheet" href="{css_url}">\n'
        f"<script>window.UNFOLD_MODAL_CONFIG = {json.dumps(config)};</script>\n"
        f'<script src="{core_js_url}"></script>\n'
        f'<script src="{host_js_url}"></script>'
    )
