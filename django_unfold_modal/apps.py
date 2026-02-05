from django.apps import AppConfig
from django.conf import settings


class DjangoUnfoldModalConfig(AppConfig):
    """AppConfig for django-unfold-modal."""

    name = "django_unfold_modal"
    verbose_name = "Django Unfold Modal"

    # Default settings
    default_settings = {
        "UNFOLD_MODAL_ENABLED": True,
        "UNFOLD_MODAL_VARIANT": "iframe",  # Reserved for future "fetch"
        "UNFOLD_MODAL_PRESENTATION": "modal",  # Reserved for future "drawer"
        "UNFOLD_MODAL_SIZE": "default",  # Presets: "default", "large", "full"
        "UNFOLD_MODAL_RESIZE": False,  # Enable manual resize handle
    }

    # Size preset dimensions (width, maxWidth, height, maxHeight)
    SIZE_PRESETS = {
        "default": {"width": "90%", "maxWidth": "900px", "height": "85vh", "maxHeight": "700px"},
        "large": {"width": "95%", "maxWidth": "1200px", "height": "90vh", "maxHeight": "900px"},
        "full": {"width": "98%", "maxWidth": "none", "height": "95vh", "maxHeight": "none"},
    }


def get_setting(name):
    """
    Get a django-unfold-modal setting with fallback to default.

    Args:
        name: The setting name (e.g., "UNFOLD_MODAL_ENABLED")

    Returns:
        The setting value from Django settings, or the default value if not set.
    """
    default_value = DjangoUnfoldModalConfig.default_settings.get(name)
    return getattr(settings, name, default_value)
