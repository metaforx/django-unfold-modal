"""Playwright UI tests for modal UX features (T13): title, maximize, resize."""

import pytest
from playwright.sync_api import expect


@pytest.mark.django_db(transaction=True)
class TestModalTitlebar:
    """Test modal titlebar displays iframe page title."""

    def test_modal_has_title_element(self, authenticated_page, live_server):
        """Modal header should have a title element."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Open modal
        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")
        page.wait_for_timeout(200)

        title = page.locator(".unfold-modal-title")
        expect(title).to_be_visible()

    def test_modal_title_shows_iframe_title(self, authenticated_page, live_server):
        """Modal title should show the iframe page title after load."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Open modal
        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")

        # Wait for iframe to load
        iframe = page.frame_locator(".unfold-modal-iframe")
        iframe.locator("body").wait_for()
        page.wait_for_timeout(300)

        title = page.locator(".unfold-modal-title")
        # The title should contain something (Add category page title)
        title_text = title.text_content()
        assert title_text, "Title should have content after iframe loads"

    def test_modal_title_is_centered(self, authenticated_page, live_server):
        """Modal title should be centered in the header."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")
        page.wait_for_timeout(200)

        title = page.locator(".unfold-modal-title")
        text_align = title.evaluate("el => window.getComputedStyle(el).textAlign")
        assert text_align == "center"


@pytest.mark.django_db(transaction=True)
class TestModalMaximize:
    """Test modal maximize functionality."""

    def test_modal_has_maximize_button(self, authenticated_page, live_server):
        """Modal header should have a maximize button."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")
        page.wait_for_timeout(200)

        maximize_btn = page.locator(".unfold-modal-maximize")
        expect(maximize_btn).to_be_visible()

    def test_maximize_expands_modal(self, authenticated_page, live_server):
        """Clicking maximize should expand modal to near-viewport size."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")
        page.wait_for_timeout(200)

        container = page.locator(".unfold-modal-container")
        initial_width = container.evaluate("el => el.offsetWidth")

        # Click maximize
        page.click(".unfold-modal-maximize")
        page.wait_for_timeout(100)

        maximized_width = container.evaluate("el => el.offsetWidth")
        viewport_width = page.evaluate("window.innerWidth")

        # Maximized width should be much larger than initial and close to viewport
        assert maximized_width > initial_width
        assert maximized_width >= viewport_width - 50  # 16px margin each side + tolerance

    def test_maximize_toggle_restores_size(self, authenticated_page, live_server):
        """Double-clicking maximize should restore original size."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")
        page.wait_for_timeout(200)

        container = page.locator(".unfold-modal-container")
        initial_width = container.evaluate("el => el.offsetWidth")

        # Maximize then restore
        page.click(".unfold-modal-maximize")
        page.wait_for_timeout(100)
        page.click(".unfold-modal-maximize")
        page.wait_for_timeout(100)

        restored_width = container.evaluate("el => el.offsetWidth")

        # Restored width should match initial
        assert abs(restored_width - initial_width) < 10  # Small tolerance

    def test_maximize_button_title_changes(self, authenticated_page, live_server):
        """Maximize button title should change between Maximize/Restore."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")
        page.wait_for_timeout(200)

        maximize_btn = page.locator(".unfold-modal-maximize")

        # Initial state
        assert maximize_btn.get_attribute("title") == "Maximize"

        # After maximize
        maximize_btn.click()
        page.wait_for_timeout(100)
        assert maximize_btn.get_attribute("title") == "Restore"

        # After restore
        maximize_btn.click()
        page.wait_for_timeout(100)
        assert maximize_btn.get_attribute("title") == "Maximize"


@pytest.mark.django_db(transaction=True)
class TestModalResizeUX:
    """Test modal resize UX improvements (testapp has resize enabled)."""

    def test_modal_has_resize_handle(self, authenticated_page, live_server):
        """Modal should have CSS resize enabled (testapp has UNFOLD_MODAL_RESIZE=True)."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")
        page.wait_for_timeout(200)

        container = page.locator(".unfold-modal-container")
        resize_style = container.evaluate("el => window.getComputedStyle(el).resize")
        assert resize_style == "both"


@pytest.mark.django_db(transaction=True)
class TestModalStackUX:
    """Test nested modal close UX (no flicker)."""

    def test_nested_modal_close_shows_previous_immediately(self, authenticated_page, live_server):
        """When closing nested modal, previous modal should be visible immediately."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/event/add/")

        # Open first modal (Venue)
        page.click("#add_id_venue")
        page.wait_for_selector(".unfold-modal-overlay")
        page.wait_for_timeout(300)

        # Open nested modal (City)
        first_iframe = page.frame_locator(".unfold-modal-iframe").first
        first_iframe.locator("#add_id_city").click()
        page.wait_for_timeout(500)

        # Should have 2 modals
        assert page.locator(".unfold-modal-overlay").count() == 2

        # Close nested modal with close button
        page.locator(".unfold-modal-close").last.click()

        # First modal should be visible immediately (no waiting for animation)
        expect(page.locator(".unfold-modal-overlay").first).to_be_visible()

        # After animation, should have 1 modal left
        page.wait_for_timeout(200)
        assert page.locator(".unfold-modal-overlay").count() == 1

    def test_overlay_stays_visible_during_nested_close(self, authenticated_page, live_server):
        """Overlay should stay visible (not flicker) during nested modal close."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/event/add/")

        # Open first modal
        page.click("#add_id_venue")
        page.wait_for_selector(".unfold-modal-overlay")
        page.wait_for_timeout(300)

        # Open nested modal
        first_iframe = page.frame_locator(".unfold-modal-iframe").first
        first_iframe.locator("#add_id_city").click()
        page.wait_for_timeout(500)

        # Close nested modal
        page.locator(".unfold-modal-close").last.click()

        # First overlay should have opacity 1 immediately
        first_overlay = page.locator(".unfold-modal-overlay").first
        opacity = first_overlay.evaluate("el => window.getComputedStyle(el).opacity")
        assert opacity == "1"
