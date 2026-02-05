"""Views for django-unfold-modal."""

import json

from django.http import HttpResponse

from .apps import DjangoUnfoldModalConfig, get_setting


def modal_config_js(request):
    """
    Serve modal configuration as a JavaScript file.

    This view returns a small JS snippet that sets up window.UNFOLD_MODAL_CONFIG
    with the current settings. Include this in UNFOLD["SCRIPTS"] before the
    main modal script.
    """
    size_preset = get_setting("UNFOLD_MODAL_SIZE")
    resize_enabled = get_setting("UNFOLD_MODAL_RESIZE")

    # Get dimensions from preset or use default
    presets = DjangoUnfoldModalConfig.SIZE_PRESETS
    dimensions = presets.get(size_preset, presets["default"])

    config = {
        "size": size_preset,
        "dimensions": dimensions,
        "resize": resize_enabled,
    }

    js_content = f"window.UNFOLD_MODAL_CONFIG = {json.dumps(config)};"

    return HttpResponse(js_content, content_type="application/javascript")
