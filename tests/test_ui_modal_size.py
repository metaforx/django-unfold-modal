"""Playwright UI tests for modal size presets and resize functionality."""

import pytest
from playwright.sync_api import expect


@pytest.mark.django_db(transaction=True)
class TestModalSizeConfigured:
    """Test modal size dimensions with testapp configuration (large preset + resize enabled)."""

    def test_large_size_initial_dimensions(self, authenticated_page, live_server):
        """Modal should start with large preset max-width (testapp: UNFOLD_MODAL_SIZE='large', UNFOLD_MODAL_RESIZE=True)."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Open modal
        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")
        page.wait_for_timeout(200)

        container = page.locator(".unfold-modal-container")
        expect(container).to_be_visible()

        # With resize enabled, initial width is calculated as min(percentage * viewport, maxWidth)
        # For large preset (95% width, 1200px maxWidth), initial should be capped at 1200px
        # on typical test viewports (1280px default) where 95% = 1216px > 1200px
        width_style = container.evaluate("el => el.style.width")
        assert width_style == "1200px", f"Expected initial width '1200px' (capped at large preset max), got '{width_style}'"


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
        """Config should have resize flag (testapp is configured with UNFOLD_MODAL_RESIZE=True)."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")
        page.wait_for_timeout(500)

        resize_value = page.evaluate(
            "window.UNFOLD_MODAL_CONFIG && window.UNFOLD_MODAL_CONFIG.resize"
        )
        # Testapp has resize enabled
        assert resize_value is True
