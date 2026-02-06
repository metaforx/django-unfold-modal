"""Playwright UI tests for dark mode modal styling."""

import pytest
from playwright.sync_api import expect


@pytest.mark.django_db(transaction=True)
class TestDarkModeModal:
    """Test modal styling in dark mode matches Unfold tokens."""

    def test_dark_mode_container_background(self, authenticated_page, live_server):
        """Modal container should have dark background in dark mode."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Enable dark mode by adding .dark class (Unfold's pattern)
        page.evaluate("document.documentElement.classList.add('dark')")

        # Open modal
        page.click("#add_id_category")

        # Wait for modal
        container = page.locator(".unfold-modal-container")
        expect(container).to_be_visible()

        # Get computed background color
        bg_color = page.evaluate("""
            () => {
                const container = document.querySelector('.unfold-modal-container');
                return getComputedStyle(container).backgroundColor;
            }
        """)

        # Unfold base-900 token fallback: rgb(24, 24, 27)
        # Should be a dark color (low RGB values)
        # Parse rgb(r, g, b) format
        assert "rgb" in bg_color
        # Extract RGB values
        import re
        match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', bg_color)
        assert match, f"Could not parse background color: {bg_color}"
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))

        # Dark background should have low RGB values (< 50 each)
        assert r < 50 and g < 50 and b < 50, \
            f"Expected dark background, got rgb({r}, {g}, {b})"

    def test_dark_mode_header_border(self, authenticated_page, live_server):
        """Modal header should have dark border in dark mode."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Enable dark mode
        page.evaluate("document.documentElement.classList.add('dark')")

        # Open modal
        page.click("#add_id_category")

        header = page.locator(".unfold-modal-header")
        expect(header).to_be_visible()

        # Get computed border color
        border_color = page.evaluate("""
            () => {
                const header = document.querySelector('.unfold-modal-header');
                return getComputedStyle(header).borderBottomColor;
            }
        """)

        # Unfold base-700 token fallback: rgb(63, 63, 70)
        # Should be darker than light mode border
        assert "rgb" in border_color
        import re
        match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', border_color)
        assert match, f"Could not parse border color: {border_color}"
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))

        # Dark border should have lower values than light mode (229, 231, 235)
        # base-700 is around (63, 63, 70)
        assert r < 100 and g < 100 and b < 100, \
            f"Expected dark border, got rgb({r}, {g}, {b})"

    def test_dark_mode_title_color(self, authenticated_page, live_server):
        """Modal title should have light color in dark mode."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Enable dark mode
        page.evaluate("document.documentElement.classList.add('dark')")

        # Open modal
        page.click("#add_id_category")

        title = page.locator(".unfold-modal-title")
        expect(title).to_be_visible()

        # Get computed text color
        text_color = page.evaluate("""
            () => {
                const title = document.querySelector('.unfold-modal-title');
                return getComputedStyle(title).color;
            }
        """)

        # Unfold base-100 token fallback: rgb(244, 244, 245)
        # Should be a light color (high RGB values)
        assert "rgb" in text_color
        import re
        match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', text_color)
        assert match, f"Could not parse text color: {text_color}"
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))

        # Light text should have high RGB values (> 200 each)
        assert r > 200 and g > 200 and b > 200, \
            f"Expected light text, got rgb({r}, {g}, {b})"

    def test_dark_mode_button_hover(self, authenticated_page, live_server):
        """Modal buttons should have correct hover color in dark mode."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Enable dark mode
        page.evaluate("document.documentElement.classList.add('dark')")

        # Open modal
        page.click("#add_id_category")

        close_btn = page.locator(".unfold-modal-close")
        expect(close_btn).to_be_visible()

        # Get button color (should be base-400 in dark mode)
        btn_color = page.evaluate("""
            () => {
                const btn = document.querySelector('.unfold-modal-close');
                return getComputedStyle(btn).color;
            }
        """)

        # Unfold base-400 token fallback: rgb(161, 161, 170)
        # Should be a medium gray
        assert "rgb" in btn_color
        import re
        match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', btn_color)
        assert match, f"Could not parse button color: {btn_color}"
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))

        # Medium gray should be around 150-180
        assert 100 < r < 200 and 100 < g < 200 and 100 < b < 200, \
            f"Expected medium gray button, got rgb({r}, {g}, {b})"

    def test_light_mode_baseline(self, authenticated_page, live_server):
        """Sanity check: light mode should have light background."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Ensure no dark mode class
        page.evaluate("document.documentElement.classList.remove('dark')")

        # Open modal
        page.click("#add_id_category")

        container = page.locator(".unfold-modal-container")
        expect(container).to_be_visible()

        # Get computed background color
        bg_color = page.evaluate("""
            () => {
                const container = document.querySelector('.unfold-modal-container');
                return getComputedStyle(container).backgroundColor;
            }
        """)

        # Light mode should be white or near-white
        assert "rgb" in bg_color
        import re
        match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', bg_color)
        assert match, f"Could not parse background color: {bg_color}"
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))

        # White is rgb(255, 255, 255)
        assert r > 240 and g > 240 and b > 240, \
            f"Expected light background, got rgb({r}, {g}, {b})"
