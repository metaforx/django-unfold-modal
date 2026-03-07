"""Template tags for unfold-modal."""

from django import template

from unfold_modal.utils import get_cms_modal_head_html

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
    return get_cms_modal_head_html()
