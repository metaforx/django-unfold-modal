"""Views for unfold-modal."""

import json

from django.http import HttpResponse

from .apps import UnfoldModalConfig, get_setting


def modal_config_js(request):
    """
    Serve modal configuration as a JavaScript file.

    This view returns a small JS snippet that sets up window.UNFOLD_MODAL_CONFIG
    with the current settings. Include this in UNFOLD["SCRIPTS"] before the
    main modal script.
    """
    presets = UnfoldModalConfig.SIZE_PRESETS

    # Regular modal settings
    size_preset = get_setting("UNFOLD_MODAL_SIZE")
    resize_enabled = get_setting("UNFOLD_MODAL_RESIZE")
    disable_header = get_setting("UNFOLD_MODAL_DISABLE_HEADER")
    dimensions = presets.get(size_preset, presets["default"])

    # CMS parent-window modal settings
    cms_size = get_setting("UNFOLD_CMS_MODAL_SIZE")
    cms_resize = get_setting("UNFOLD_CMS_MODAL_RESIZE")
    cms_disable_header = get_setting("UNFOLD_CMS_MODAL_DISABLE_HEADER")
    cms_dimensions = presets.get(cms_size, presets["full"])

    config = {
        "size": size_preset,
        "dimensions": dimensions,
        "resize": resize_enabled,
        "disableHeader": disable_header,
        "cms": {
            "size": cms_size,
            "dimensions": cms_dimensions,
            "resize": cms_resize,
            "disableHeader": cms_disable_header,
        },
    }

    js_content = f"window.UNFOLD_MODAL_CONFIG = {json.dumps(config)};"

    return HttpResponse(js_content, content_type="application/javascript")
