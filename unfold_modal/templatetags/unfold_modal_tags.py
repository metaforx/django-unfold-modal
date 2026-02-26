"""Template tags for unfold-modal CMS integration."""

import json

from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from unfold_modal.apps import UnfoldModalConfig, get_setting

register = template.Library()


@register.simple_tag
def unfold_modal_cms_head():
    """
    Output all required CSS, config, and JS for CMS parent-window modal hosting.

    Usage in CMS base template:
        {% load unfold_modal_tags %}
        <head>
            ...
            {% unfold_modal_cms_head %}
        </head>
    """
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
