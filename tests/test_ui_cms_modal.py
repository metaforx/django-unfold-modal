"""Playwright tests for CMS parent-window modal hosting.

Covers the scenario where Django admin runs inside a Django CMS modal iframe.
The unfold-modal should open in the CMS parent document (outside the admin iframe),
not inside the iframe or as a popup window.
"""

import re

import pytest
from playwright.sync_api import expect

from testapp.models import Publisher


@pytest.mark.django_db(transaction=True)
class TestCmsModalHost:
    """Modal should render in CMS parent document when admin is inside CMS modal."""

    def test_modal_opens_in_parent_document(self, browser, live_server, admin_user):
        """Clicking add-related inside CMS modal iframe should open unfold modal
        in the parent CMS document, not inside the admin iframe."""
        context = browser.new_context()
        page = context.new_page()

        # Log in
        page.goto(f"{live_server.url}/admin/login/?next=/admin/")
        page.fill('input[name="username"]', "playwrightadmin")
        page.fill('input[name="password"]', "playwrightpass")
        page.click('button[type="submit"], input[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Navigate to CMS modal host with admin book-add form
        book_add_url = "/admin/testapp/book/add/"
        page.goto(f"{live_server.url}/cms-modal-host/?url={book_add_url}")
        page.wait_for_load_state("networkidle")

        # Get the CMS iframe containing admin
        cms_iframe = page.frame_locator("#cms-iframe")

        # Wait for admin form to load inside iframe
        cms_iframe.locator("#add_id_category").wait_for(state="visible", timeout=10000)

        # Track popup windows
        popup_opened = []
        page.on("popup", lambda p: popup_opened.append(p))

        # Click add button for category (ForeignKey)
        cms_iframe.locator("#add_id_category").click()

        # Modal overlay should appear in the PARENT document (not in iframe)
        parent_overlay = page.locator(".unfold-modal-overlay")
        expect(parent_overlay).to_be_visible(timeout=5000)

        # Modal iframe should be present in parent document
        parent_modal_iframe = page.locator(".unfold-modal-iframe")
        expect(parent_modal_iframe).to_be_visible()

        # No popup window should have opened
        assert len(popup_opened) == 0, "Popup window opened instead of modal"

        context.close()

    def test_modal_does_not_open_inside_iframe(self, browser, live_server, admin_user):
        """Modal overlay should NOT appear inside the admin iframe document
        when hosted in CMS modal context."""
        context = browser.new_context()
        page = context.new_page()

        # Log in
        page.goto(f"{live_server.url}/admin/login/?next=/admin/")
        page.fill('input[name="username"]', "playwrightadmin")
        page.fill('input[name="password"]', "playwrightpass")
        page.click('button[type="submit"], input[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Navigate to CMS modal host
        book_add_url = "/admin/testapp/book/add/"
        page.goto(f"{live_server.url}/cms-modal-host/?url={book_add_url}")
        page.wait_for_load_state("networkidle")

        cms_iframe = page.frame_locator("#cms-iframe")
        cms_iframe.locator("#add_id_category").wait_for(state="visible", timeout=10000)

        # Click add button
        cms_iframe.locator("#add_id_category").click()

        # Wait for modal in parent
        expect(page.locator(".unfold-modal-overlay")).to_be_visible(timeout=5000)

        # Verify overlay is NOT inside the admin iframe
        iframe_overlay_count = cms_iframe.locator(".unfold-modal-overlay").count()
        assert iframe_overlay_count == 0, "Modal overlay appeared inside iframe instead of parent"

        context.close()

    def test_cms_modal_uses_fullscreen_default(self, browser, live_server, admin_user):
        """CMS modal should use fullscreen dimensions by default (UNFOLD_CMS_MODAL_SIZE=full)."""
        context = browser.new_context()
        page = context.new_page()

        # Log in
        page.goto(f"{live_server.url}/admin/login/?next=/admin/")
        page.fill('input[name="username"]', "playwrightadmin")
        page.fill('input[name="password"]', "playwrightpass")
        page.click('button[type="submit"], input[type="submit"]')
        page.wait_for_load_state("networkidle")

        book_add_url = "/admin/testapp/book/add/"
        page.goto(f"{live_server.url}/cms-modal-host/?url={book_add_url}")
        page.wait_for_load_state("networkidle")

        cms_iframe = page.frame_locator("#cms-iframe")
        cms_iframe.locator("#add_id_category").wait_for(state="visible", timeout=10000)
        cms_iframe.locator("#add_id_category").click()

        # Wait for modal container in parent
        container = page.locator(".unfold-modal-container")
        expect(container).to_be_visible(timeout=5000)

        # Check container uses "full" preset dimensions (98% width, maxWidth none)
        max_width = container.evaluate("el => el.style.maxWidth")
        assert max_width == "none", f"Expected maxWidth 'none' for full preset, got '{max_width}'"

        context.close()

    def test_raw_id_lookup_selection_updates_field_in_cms_iframe(
        self, browser, live_server, admin_user
    ):
        """Selecting from raw_id lookup in CMS-hosted admin should update the source field."""
        Publisher.objects.create(name="CMS Publisher")

        context = browser.new_context()
        page = context.new_page()

        # Log in
        page.goto(f"{live_server.url}/admin/login/?next=/admin/")
        page.fill('input[name="username"]', "playwrightadmin")
        page.fill('input[name="password"]', "playwrightpass")
        page.click('button[type="submit"], input[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Open admin add form inside CMS modal host
        book_add_url = "/admin/testapp/book/add/"
        page.goto(f"{live_server.url}/cms-modal-host/?url={book_add_url}")
        page.wait_for_load_state("networkidle")

        cms_iframe = page.frame_locator("#cms-iframe")
        cms_iframe.locator("#lookup_id_publisher").wait_for(state="visible", timeout=10000)

        # Open lookup in parent-hosted modal and pick object
        cms_iframe.locator("#lookup_id_publisher").click()
        lookup_iframe = page.frame_locator(".unfold-modal-iframe")
        lookup_iframe.locator("a:has-text('CMS Publisher')").click()

        # The value should be written back into source iframe field
        expect(cms_iframe.locator("#id_publisher")).to_have_value(re.compile(r"\d+"))

        context.close()


@pytest.mark.django_db(transaction=True)
class TestCmsModalRegression:
    """Existing non-CMS modal flows should not regress."""

    def test_sideframe_still_opens_inside_iframe(self, browser, live_server, admin_user):
        """Non-CMS iframe host (sideframe) should still open modal inside iframe."""
        context = browser.new_context()
        page = context.new_page()

        # Log in
        page.goto(f"{live_server.url}/admin/login/?next=/admin/")
        page.fill('input[name="username"]', "playwrightadmin")
        page.fill('input[name="password"]', "playwrightpass")
        page.click('button[type="submit"], input[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Use non-CMS iframe host (no .cms-modal wrapper)
        book_add_url = "/admin/testapp/book/add/"
        page.goto(f"{live_server.url}/iframe-host/?url={book_add_url}")
        page.wait_for_load_state("networkidle")

        sideframe = page.frame_locator("#sideframe")
        sideframe.locator("#add_id_category").wait_for(state="visible", timeout=10000)

        sideframe.locator("#add_id_category").click()

        # Modal should appear INSIDE the iframe (not in parent)
        iframe_overlay = sideframe.locator(".unfold-modal-overlay")
        expect(iframe_overlay).to_be_visible(timeout=5000)

        # Parent document should NOT have modal overlay
        parent_overlay_count = page.locator(".unfold-modal-overlay").count()
        assert parent_overlay_count == 0, "Modal appeared in parent instead of inside iframe"

        context.close()

    def test_direct_admin_still_works(self, authenticated_page, live_server):
        """Direct admin page (no iframe) should still open modal normally."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")

        overlay = page.locator(".unfold-modal-overlay")
        expect(overlay).to_be_visible(timeout=5000)
