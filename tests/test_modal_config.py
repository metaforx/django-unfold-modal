"""Tests for modal configuration settings."""

import pytest
from django.test import override_settings


@pytest.mark.django_db
class TestModalConfig:
    """Test modal configuration view and settings."""

    def test_config_js_returns_javascript(self, client):
        """Config endpoint should return JavaScript content type."""
        response = client.get("/unfold-modal/config.js")
        assert response.status_code == 200
        assert response["Content-Type"] == "application/javascript"

    @override_settings(UNFOLD_MODAL_SIZE="default")
    def test_config_js_contains_default_dimensions(self, client):
        """Config should contain default dimensions when not configured."""
        response = client.get("/unfold-modal/config.js")
        content = response.content.decode()
        assert "UNFOLD_MODAL_CONFIG" in content
        assert '"width": "90%"' in content
        assert '"maxWidth": "900px"' in content
        assert '"height": "85vh"' in content
        assert '"maxHeight": "700px"' in content

    @override_settings(UNFOLD_MODAL_SIZE="large")
    def test_config_js_uses_large_preset(self, client):
        """Config should use large dimensions when configured."""
        response = client.get("/unfold-modal/config.js")
        content = response.content.decode()
        assert '"maxWidth": "1200px"' in content
        assert '"maxHeight": "900px"' in content

    @override_settings(UNFOLD_MODAL_SIZE="full")
    def test_config_js_uses_full_preset(self, client):
        """Config should use full dimensions when configured."""
        response = client.get("/unfold-modal/config.js")
        content = response.content.decode()
        assert '"maxWidth": "none"' in content
        assert '"maxHeight": "none"' in content

    @override_settings(UNFOLD_MODAL_RESIZE=True)
    def test_config_js_includes_resize_flag(self, client):
        """Config should include resize flag when enabled."""
        response = client.get("/unfold-modal/config.js")
        content = response.content.decode()
        assert '"resize": true' in content

    @override_settings(UNFOLD_MODAL_RESIZE=False)
    def test_config_js_resize_false_by_default(self, client):
        """Config should have resize false by default."""
        response = client.get("/unfold-modal/config.js")
        content = response.content.decode()
        assert '"resize": false' in content

    def test_config_js_disable_header_true_by_default(self, client):
        """Config should have disableHeader true by default."""
        response = client.get("/unfold-modal/config.js")
        content = response.content.decode()
        assert '"disableHeader": true' in content

    @override_settings(UNFOLD_MODAL_DISABLE_HEADER=False)
    def test_config_js_disable_header_can_be_false(self, client):
        """Config should allow disableHeader to be set to false."""
        response = client.get("/unfold-modal/config.js")
        content = response.content.decode()
        assert '"disableHeader": false' in content


@pytest.mark.django_db
class TestOverrideNativeInAdmin:
    """UNFOLD_MODAL_OVERRIDE_NATIVE as rendered into admin pages."""

    ADAPTER = "unfold_modal/js/unfold_related_adapter.js"

    def test_admin_page_loads_adapter_without_fragment(self, admin_client):
        content = admin_client.get("/admin/testapp/book/add/").content.decode()
        assert f'{self.ADAPTER}"' in content
        assert "#coexist" not in content

    @override_settings(UNFOLD_MODAL_OVERRIDE_NATIVE=False)
    def test_admin_page_loads_adapter_with_coexist_fragment(self, admin_client):
        content = admin_client.get("/admin/testapp/book/add/").content.decode()
        assert f'{self.ADAPTER}#coexist"' in content

    @override_settings(UNFOLD_MODAL_OVERRIDE_NATIVE=False)
    def test_popup_page_loads_adapter_with_coexist_fragment(self, admin_client):
        content = admin_client.get(
            "/admin/testapp/category/add/?_popup=1"
        ).content.decode()
        assert f'{self.ADAPTER}#coexist"' in content
