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

    def ready(self):
        """Apply default settings if not already configured."""
        for key, default_value in self.default_settings.items():
            if not hasattr(settings, key):
                setattr(settings, key, default_value)
