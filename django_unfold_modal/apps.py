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
