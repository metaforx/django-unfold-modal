"""Template tags for unfold-modal."""

from django import template

from unfold_modal.apps import get_setting
from unfold_modal.utils import get_cms_modal_head_html

register = template.Library()


@register.simple_tag
def unfold_modal_show_add_in_popup():
    """Return the UNFOLD_MODAL_SHOW_ADD_IN_POPUP setting value."""
    return get_setting("UNFOLD_MODAL_SHOW_ADD_IN_POPUP")


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
    return get_cms_modal_head_html()
