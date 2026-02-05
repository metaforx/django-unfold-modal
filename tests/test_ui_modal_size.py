"""Playwright UI tests for modal size presets and resize functionality."""

import pytest
from playwright.sync_api import expect


@pytest.mark.django_db(transaction=True)
class TestModalSizeDefault:
    """Test default modal size dimensions."""

    def test_default_size_dimensions(self, authenticated_page, live_server):
        """Modal should have default dimensions (90% width, 900px max)."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Open modal
        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")
        page.wait_for_timeout(200)

        container = page.locator(".unfold-modal-container")
        expect(container).to_be_visible()

        # Check computed max-width is 900px (default)
        max_width = container.evaluate("el => window.getComputedStyle(el).maxWidth")
        assert max_width == "900px"


@pytest.mark.django_db(transaction=True)
class TestModalConfigLoaded:
    """Test that modal config is properly loaded."""

    def test_config_object_exists(self, authenticated_page, live_server):
        """window.UNFOLD_MODAL_CONFIG should be defined."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Wait for scripts to load
        page.wait_for_timeout(500)

        config_exists = page.evaluate("typeof window.UNFOLD_MODAL_CONFIG !== 'undefined'")
        assert config_exists, "UNFOLD_MODAL_CONFIG should be defined"

    def test_config_has_dimensions(self, authenticated_page, live_server):
        """Config should have dimensions object."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")
        page.wait_for_timeout(500)

        has_dimensions = page.evaluate(
            "window.UNFOLD_MODAL_CONFIG && window.UNFOLD_MODAL_CONFIG.dimensions"
        )
        assert has_dimensions, "Config should have dimensions"

    def test_config_has_resize_flag(self, authenticated_page, live_server):
        """Config should have resize flag."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")
        page.wait_for_timeout(500)

        resize_value = page.evaluate(
            "window.UNFOLD_MODAL_CONFIG && window.UNFOLD_MODAL_CONFIG.resize"
        )
        # Default is false
        assert resize_value is False
