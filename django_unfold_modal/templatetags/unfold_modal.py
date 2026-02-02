from django import template

from django_unfold_modal.apps import get_setting

register = template.Library()


@register.simple_tag
def unfold_modal_enabled():
    """Check if unfold modal is enabled."""
    return get_setting("UNFOLD_MODAL_ENABLED")
