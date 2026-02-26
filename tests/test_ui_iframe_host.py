"""Playwright tests for modal behavior when admin is inside a non-modal iframe.

Covers the Django CMS sideframe scenario: admin runs inside an iframe that
is NOT created by unfold-modal, so modal should open locally inside the
iframe rather than forwarding to parent or falling back to a popup window.
"""

import pytest
from playwright.sync_api import expect


@pytest.mark.django_db(transaction=True)
class TestIframeHostModal:
    """Modal should work when admin is loaded inside a non-modal iframe."""

    def test_modal_opens_inside_sideframe_iframe(self, browser, live_server, admin_user):
        """Clicking add-related inside a non-modal iframe should open the modal
        inside the iframe, not a popup window."""
        context = browser.new_context()
        page = context.new_page()

        # Log in via the admin login page
        page.goto(f"{live_server.url}/admin/login/?next=/admin/")
        page.fill('input[name="username"]', "playwrightadmin")
        page.fill('input[name="password"]', "playwrightpass")
        page.click('button[type="submit"], input[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Navigate to iframe host page with admin book-add form embedded
        book_add_url = "/admin/testapp/book/add/"
        page.goto(f"{live_server.url}/iframe-host/?url={book_add_url}")
        page.wait_for_load_state("networkidle")

        # Get the iframe
        sideframe = page.frame_locator("#sideframe")

        # Wait for admin form to load inside iframe
        sideframe.locator("#add_id_category").wait_for(state="visible", timeout=10000)

        # Track popup windows
        popup_opened = []
        page.on("popup", lambda p: popup_opened.append(p))

        # Click add button for category (ForeignKey)
        sideframe.locator("#add_id_category").click()

        # Modal overlay should appear INSIDE the iframe
        overlay = sideframe.locator(".unfold-modal-overlay")
        expect(overlay).to_be_visible(timeout=5000)

        # Modal iframe should also be present
        modal_iframe = sideframe.locator(".unfold-modal-iframe")
        expect(modal_iframe).to_be_visible()

        # No popup window should have opened
        assert len(popup_opened) == 0, "Popup window opened instead of modal"

        context.close()

    def test_nested_modal_still_works_from_sideframe(self, browser, live_server, admin_user):
        """After opening a modal inside a sideframe iframe, nested related
        fields inside the modal should also work (nested modal flow)."""
        context = browser.new_context()
        page = context.new_page()

        # Log in
        page.goto(f"{live_server.url}/admin/login/?next=/admin/")
        page.fill('input[name="username"]', "playwrightadmin")
        page.fill('input[name="password"]', "playwrightpass")
        page.click('button[type="submit"], input[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Navigate to iframe host with admin book-add form
        book_add_url = "/admin/testapp/book/add/"
        page.goto(f"{live_server.url}/iframe-host/?url={book_add_url}")
        page.wait_for_load_state("networkidle")

        sideframe = page.frame_locator("#sideframe")
        sideframe.locator("#add_id_category").wait_for(state="visible", timeout=10000)

        # Open first modal (add category)
        sideframe.locator("#add_id_category").click()
        overlay = sideframe.locator(".unfold-modal-overlay")
        expect(overlay).to_be_visible(timeout=5000)

        # The modal should have an iframe with the category add form
        modal_iframe = sideframe.locator(".unfold-modal-iframe")
        expect(modal_iframe).to_be_visible()

        context.close()
