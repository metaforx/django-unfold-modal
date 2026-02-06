"""Playwright UI tests for admin header suppression in modal iframes."""

import pytest
from playwright.sync_api import expect


# Constants matching modal_core.js SELECTORS
HEADER_INNER_ID = "header-inner"
MAIN_ID = "main"
HEADER_CONTAINER_DEPTH = 2


def get_header_container_in_iframe(page, iframe_index=-1):
    """
    Get the header container element from an iframe using structural navigation.
    Returns a dict with 'found', 'display', and 'element' info.

    Uses the same logic as the JS: navigate HEADER_CONTAINER_DEPTH levels up
    from #header-inner to find the header container.

    Args:
        page: Playwright page object
        iframe_index: Index of iframe to check. Use -1 for last iframe (default).
    """
    # Handle negative index in Python before passing to JS
    # JS doesn't support negative array indexing like Python
    js_index_expr = f"iframes.length + {iframe_index}" if iframe_index < 0 else str(iframe_index)

    return page.evaluate(f"""
        () => {{
            const iframes = document.querySelectorAll('.unfold-modal-iframe');
            const idx = {js_index_expr};
            const iframe = iframes[idx];
            if (!iframe || !iframe.contentDocument) {{
                return {{ found: false, reason: 'no-iframe', iframeCount: iframes.length, requestedIndex: idx }};
            }}

            const headerInner = iframe.contentDocument.getElementById('{HEADER_INNER_ID}');
            if (!headerInner) {{
                return {{ found: false, reason: 'no-header-inner' }};
            }}

            // Navigate up to header container (same logic as JS)
            let headerContainer = headerInner;
            for (let i = 0; i < {HEADER_CONTAINER_DEPTH}; i++) {{
                if (headerContainer.parentElement) {{
                    headerContainer = headerContainer.parentElement;
                }}
            }}

            if (!headerContainer || headerContainer === iframe.contentDocument.body) {{
                return {{ found: false, reason: 'container-not-found' }};
            }}

            const computedStyle = window.getComputedStyle(headerContainer);
            return {{
                found: true,
                display: computedStyle.display,
                visibility: computedStyle.visibility,
                height: headerContainer.offsetHeight
            }};
        }}
    """)


@pytest.mark.django_db(transaction=True)
class TestHeaderSuppression:
    """Test admin header visibility in modal iframes."""

    def test_header_inner_exists_in_iframe(self, authenticated_page, live_server):
        """Verify #header-inner exists in iframe (selector stability check)."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Open modal
        page.click("#add_id_category")

        # Wait for modal and iframe to load
        iframe = page.frame_locator(".unfold-modal-iframe")
        iframe.locator("input[name='name']").wait_for(state="visible", timeout=5000)

        # Verify #header-inner exists (this test fails if Unfold changes structure)
        header_inner_exists = page.evaluate(f"""
            () => {{
                const iframe = document.querySelector('.unfold-modal-iframe');
                return iframe.contentDocument.getElementById('{HEADER_INNER_ID}') !== null;
            }}
        """)

        assert header_inner_exists, \
            f"#{HEADER_INNER_ID} not found in iframe - Unfold structure may have changed"

    def test_header_hidden_when_disable_header_true(self, authenticated_page, live_server):
        """With UNFOLD_MODAL_DISABLE_HEADER=True (default), header container should be hidden."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Open modal
        page.click("#add_id_category")

        # Wait for modal and iframe to load
        iframe = page.frame_locator(".unfold-modal-iframe")
        iframe.locator("input[name='name']").wait_for(state="visible", timeout=5000)

        # Get header container state
        result = get_header_container_in_iframe(page)

        assert result['found'], f"Header container not found: {result.get('reason')}"
        assert result['display'] == 'none', \
            f"Expected header display 'none', got '{result['display']}'"

    def test_main_has_padding_when_header_hidden(self, authenticated_page, live_server):
        """When header is hidden, #main should have top padding for spacing."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Open modal
        page.click("#add_id_category")

        # Wait for modal and iframe to load
        iframe = page.frame_locator(".unfold-modal-iframe")
        iframe.locator("input[name='name']").wait_for(state="visible", timeout=5000)

        # Check #main padding
        padding = page.evaluate(f"""
            () => {{
                const iframe = document.querySelector('.unfold-modal-iframe');
                const main = iframe.contentDocument.getElementById('{MAIN_ID}');
                if (!main) return {{ found: false }};
                return {{ found: true, paddingTop: main.style.paddingTop }};
            }}
        """)

        assert padding['found'], f"#{MAIN_ID} not found in iframe"
        assert padding['paddingTop'] == '1rem', \
            f"Expected paddingTop '1rem', got '{padding['paddingTop']}'"

    def test_parent_page_header_unaffected(self, authenticated_page, live_server):
        """The parent page header should remain visible when modal opens."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Verify parent header exists and is visible
        header_inner = page.locator(f"#{HEADER_INNER_ID}")
        expect(header_inner).to_be_visible()

        # Open modal
        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")

        # Parent header should still be visible (not affected by iframe header hiding)
        expect(header_inner).to_be_visible()

    def test_nested_modal_header_also_hidden(self, authenticated_page, live_server):
        """Nested modals should also have their headers hidden."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/venue/add/")

        # Open first modal (City form)
        page.click("#add_id_city")
        page.wait_for_selector(".unfold-modal-iframe")
        page.wait_for_timeout(500)

        # Check first modal header is hidden
        first_result = get_header_container_in_iframe(page, iframe_index=0)
        assert first_result['found'], f"First modal header not found: {first_result.get('reason')}"
        assert first_result['display'] == 'none', \
            f"First modal header should be hidden, got display: {first_result['display']}"

        # Open nested modal (Country form) from within City form
        iframe_a = page.frame_locator(".unfold-modal-iframe")
        iframe_a.locator("#add_id_country").wait_for(state="visible", timeout=5000)
        iframe_a.locator("#add_id_country").click()
        page.wait_for_timeout(500)

        # Check nested modal header is also hidden (use last iframe)
        nested_result = get_header_container_in_iframe(page, iframe_index=-1)
        assert nested_result['found'], f"Nested modal header not found: {nested_result.get('reason')}"
        assert nested_result['display'] == 'none', \
            f"Nested modal header should be hidden, got display: {nested_result['display']}"
