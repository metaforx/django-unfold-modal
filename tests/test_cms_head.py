"""Tests for CMS head HTML output (get_cms_modal_head_html)."""

import pytest

from unfold_modal.utils import get_cms_modal_head_html


@pytest.mark.django_db
class TestCmsModalHeadHtml:
    """Verify get_cms_modal_head_html includes all required assets."""

    def test_includes_material_symbols_stylesheet(self):
        html = get_cms_modal_head_html()
        assert "material-symbols/styles.css" in html

    def test_includes_modal_css(self):
        html = get_cms_modal_head_html()
        assert "unfold_modal/css/modal.css" in html

    def test_includes_modal_core_js(self):
        html = get_cms_modal_head_html()
        assert "unfold_modal/js/modal_core.js" in html

    def test_includes_related_modal_js(self):
        html = get_cms_modal_head_html()
        assert "unfold_modal/js/related_modal.js" in html

    def test_includes_cms_host_js(self):
        html = get_cms_modal_head_html()
        assert "unfold_modal/js/cms_host.js" in html

    def test_includes_inline_config(self):
        html = get_cms_modal_head_html()
        assert "window.UNFOLD_MODAL_CONFIG" in html

    def test_icon_css_before_modal_css(self):
        """Material Symbols stylesheet should appear before modal CSS."""
        html = get_cms_modal_head_html()
        icons_pos = html.index("material-symbols/styles.css")
        modal_css_pos = html.index("unfold_modal/css/modal.css")
        assert icons_pos < modal_css_pos

    def test_css_before_js(self):
        """All CSS should appear before any JS."""
        html = get_cms_modal_head_html()
        last_css = html.rindex("</link>") if "</link>" in html else html.rindex('.css">')
        first_script = html.index("<script")
        assert last_css < first_script
