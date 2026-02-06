"""Playwright UI tests for admin header suppression in modal iframes."""

import pytest
from playwright.sync_api import expect


@pytest.mark.django_db(transaction=True)
class TestHeaderSuppression:
    """Test admin header visibility in modal iframes."""

    def test_admin_header_hidden_in_modal_iframe(self, authenticated_page, live_server):
        """With default settings, admin header should be hidden inside modal iframe."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Open modal
        page.click("#add_id_category")

        # Wait for modal and iframe to load
        iframe = page.frame_locator(".unfold-modal-iframe")
        iframe.locator("input[name='name']").wait_for(state="visible", timeout=5000)

        # Check that the header is hidden (display: none)
        header_display = page.evaluate("""
            () => {
                const iframe = document.querySelector('.unfold-modal-iframe');
                const headerInner = iframe.contentDocument.getElementById('header-inner');
                if (!headerInner) return 'no-header-inner';
                const header = headerInner.closest('.border-b');
                if (!header) return 'no-header';
                return window.getComputedStyle(header).display;
            }
        """)

        assert header_display == "none", f"Expected header to be hidden, got display: {header_display}"

    def test_main_content_has_top_padding_when_header_hidden(self, authenticated_page, live_server):
        """When header is hidden, main content should have extra top padding."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Open modal
        page.click("#add_id_category")

        # Wait for modal and iframe to load
        iframe = page.frame_locator(".unfold-modal-iframe")
        iframe.locator("input[name='name']").wait_for(state="visible", timeout=5000)

        # Check main content has padding
        padding_top = page.evaluate("""
            () => {
                const iframe = document.querySelector('.unfold-modal-iframe');
                const main = iframe.contentDocument.getElementById('main');
                if (!main) return 'no-main';
                return main.style.paddingTop;
            }
        """)

        assert padding_top == "1rem", f"Expected paddingTop '1rem', got '{padding_top}'"

    def test_header_visible_on_parent_page(self, authenticated_page, live_server):
        """The header on the parent page should remain visible (not affected)."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Check parent page header is visible
        header_inner = page.locator("#header-inner")
        expect(header_inner).to_be_visible()

        # Open modal
        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")

        # Parent header should still be visible
        expect(header_inner).to_be_visible()

    def test_nested_modal_also_hides_header(self, authenticated_page, live_server):
        """Nested modals should also have their headers hidden."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/venue/add/")

        # Open first modal (City form)
        page.click("#add_id_city")
        page.wait_for_selector(".unfold-modal-iframe")
        page.wait_for_timeout(500)

        # Open nested modal (Country form) from within City form
        iframe_a = page.frame_locator(".unfold-modal-iframe")
        iframe_a.locator("#add_id_country").wait_for(state="visible", timeout=5000)
        iframe_a.locator("#add_id_country").click()
        page.wait_for_timeout(500)

        # Check that the nested modal's iframe also has header hidden
        # The nested modal is the second iframe
        nested_header_display = page.evaluate("""
            () => {
                const iframes = document.querySelectorAll('.unfold-modal-iframe');
                const nestedIframe = iframes[iframes.length - 1];
                if (!nestedIframe || !nestedIframe.contentDocument) return 'no-iframe';
                const headerInner = nestedIframe.contentDocument.getElementById('header-inner');
                if (!headerInner) return 'no-header-inner';
                const header = headerInner.closest('.border-b');
                if (!header) return 'no-header';
                return window.getComputedStyle(header).display;
            }
        """)

        assert nested_header_display == "none", f"Expected nested modal header hidden, got: {nested_header_display}"
