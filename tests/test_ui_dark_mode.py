"""Playwright UI tests for dark mode modal styling."""

import re
import pytest
from playwright.sync_api import expect


def parse_color(color_str):
    """
    Parse a CSS color string and return a dict with RGB-like values.
    Handles both rgb() and oklch() formats.

    For oklch, lightness (L) maps roughly to brightness:
    - L < 0.3 = dark
    - L > 0.9 = light
    """
    # Try RGB format first
    rgb_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str)
    if rgb_match:
        r, g, b = int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3))
        return {'format': 'rgb', 'r': r, 'g': g, 'b': b, 'lightness': (r + g + b) / 765}

    # Try OKLCH format: oklch(L C H) where L is lightness 0-1
    oklch_match = re.search(r'oklch\(([\d.]+)\s+([\d.]+)\s+([\d.]+)\)', color_str)
    if oklch_match:
        l = float(oklch_match.group(1))
        return {'format': 'oklch', 'lightness': l}

    return None


def is_dark_color(color_str):
    """Check if a color is dark (low lightness)."""
    parsed = parse_color(color_str)
    if not parsed:
        return False
    return parsed['lightness'] < 0.3


def is_light_color(color_str):
    """Check if a color is light (high lightness)."""
    parsed = parse_color(color_str)
    if not parsed:
        return False
    return parsed['lightness'] > 0.9


def is_medium_color(color_str):
    """Check if a color is medium gray (mid lightness)."""
    parsed = parse_color(color_str)
    if not parsed:
        return False
    return 0.4 < parsed['lightness'] < 0.8


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

        # Dark background should have low lightness
        assert is_dark_color(bg_color), \
            f"Expected dark background, got {bg_color}"

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

        # Dark border should have low-medium lightness (darker than light mode)
        parsed = parse_color(border_color)
        assert parsed, f"Could not parse border color: {border_color}"
        # base-700 is a medium-dark gray
        assert parsed['lightness'] < 0.5, \
            f"Expected dark border, got {border_color}"

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

        # Light text should have high lightness
        assert is_light_color(text_color), \
            f"Expected light text, got {text_color}"

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

        # Get button color (should be base-400 in dark mode - medium gray)
        btn_color = page.evaluate("""
            () => {
                const btn = document.querySelector('.unfold-modal-close');
                return getComputedStyle(btn).color;
            }
        """)

        # Medium gray should have mid lightness
        assert is_medium_color(btn_color), \
            f"Expected medium gray button, got {btn_color}"

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

        # Light mode should have high lightness (near white)
        assert is_light_color(bg_color), \
            f"Expected light background, got {bg_color}"
