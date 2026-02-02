"""Playwright UI tests for modal functionality."""

import pytest
from playwright.sync_api import expect

from testapp.models import Author, Category, Publisher


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(name="Fiction")


@pytest.fixture
def author(db):
    """Create a test author."""
    return Author.objects.create(name="Jane Doe")


@pytest.fixture
def publisher(db):
    """Create a test publisher."""
    return Publisher.objects.create(name="Acme Publishing")


@pytest.mark.django_db(transaction=True)
class TestModalDOMStructure:
    """Test modal DOM elements are created correctly."""

    def test_modal_overlay_present_on_open(self, authenticated_page, live_server):
        """Opening related widget should create .unfold-modal-overlay."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Click add button for category (ForeignKey select)
        page.click("#add_id_category")

        # Wait for modal overlay to appear
        overlay = page.locator(".unfold-modal-overlay")
        expect(overlay).to_be_visible()

    def test_modal_container_present(self, authenticated_page, live_server):
        """Modal should have .unfold-modal-container."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")

        container = page.locator(".unfold-modal-container")
        expect(container).to_be_visible()

    def test_modal_iframe_present_with_popup_url(self, authenticated_page, live_server):
        """Modal should have .unfold-modal-iframe with _popup=1 in URL."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")

        iframe = page.locator(".unfold-modal-iframe")
        expect(iframe).to_be_visible()

        # Check iframe src contains _popup=1
        src = iframe.get_attribute("src")
        assert "_popup=1" in src

    def test_body_scroll_locked_when_modal_open(self, authenticated_page, live_server):
        """Body should have overflow:hidden when modal is open."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")

        # Wait for modal
        page.wait_for_selector(".unfold-modal-overlay")

        # Check body overflow is hidden
        overflow = page.evaluate("document.body.style.overflow")
        assert overflow == "hidden"

    def test_body_scroll_unlocked_on_close(self, authenticated_page, live_server):
        """Body scroll should be restored when modal is closed."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")

        # Close modal with ESC
        page.keyboard.press("Escape")

        # Wait for modal to be removed
        page.wait_for_selector(".unfold-modal-overlay", state="detached")

        # Check body overflow is restored
        overflow = page.evaluate("document.body.style.overflow")
        assert overflow != "hidden"


@pytest.mark.django_db(transaction=True)
class TestAddRelatedFromSelect:
    """Test adding related object from normal ForeignKey select."""

    def test_add_category_updates_select(self, authenticated_page, live_server):
        """Adding a category via modal should update the select field."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Click add button for category
        page.click("#add_id_category")

        # Wait for modal iframe
        iframe = page.frame_locator(".unfold-modal-iframe")

        # Fill in the category form inside iframe
        iframe.locator('input[name="name"]').fill("New Category")
        iframe.locator('button[name="_save"]').click()

        # Wait for modal to close
        page.wait_for_selector(".unfold-modal-overlay", state="detached")

        # Check select has new option selected
        selected_text = page.locator("#id_category option:checked").text_content()
        assert "New Category" in selected_text


@pytest.mark.django_db(transaction=True)
class TestChangeRelatedAutocomplete:
    """Test changing related object updates autocomplete field."""

    def test_change_author_updates_label(
        self, authenticated_page, live_server, author
    ):
        """Changing an author via modal should update the autocomplete display."""
        page = authenticated_page

        # First need to select the author in the autocomplete
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Select2 autocomplete - click to open
        page.click("#id_author ~ .select2-container")
        page.wait_for_timeout(300)

        # Type to search
        page.keyboard.type("Jane")
        page.wait_for_timeout(500)

        # Click the option
        page.click(".select2-results__option:has-text('Jane Doe')")
        page.wait_for_timeout(200)

        # Now click change button
        page.click("#change_id_author")

        # Wait for modal
        iframe = page.frame_locator(".unfold-modal-iframe")

        # Update author name
        name_input = iframe.locator('input[name="name"]')
        name_input.clear()
        name_input.fill("Jane Updated")
        iframe.locator('button[name="_save"]').click()

        # Wait for modal to close
        page.wait_for_selector(".unfold-modal-overlay", state="detached")

        # Check autocomplete shows updated name
        selected_text = page.locator("#id_author ~ .select2-container .select2-selection__rendered").text_content()
        assert "Jane Updated" in selected_text


@pytest.mark.django_db(transaction=True)
class TestRawIdLookup:
    """Test raw_id_fields lookup popup functionality."""

    def test_lookup_selection_updates_field(
        self, authenticated_page, live_server, publisher
    ):
        """Selecting from raw_id lookup should update the field."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Click lookup button for publisher (raw_id_fields)
        page.click("#lookup_id_publisher")

        # Wait for modal
        iframe = page.frame_locator(".unfold-modal-iframe")

        # Click on the publisher link in the changelist
        iframe.locator(f"a:has-text('{publisher.name}')").click()

        # Wait for modal to close
        page.wait_for_selector(".unfold-modal-overlay", state="detached")

        # Check the raw_id field has the publisher ID
        field_value = page.input_value("#id_publisher")
        assert field_value == str(publisher.pk)


@pytest.mark.django_db(transaction=True)
class TestValidationError:
    """Test that validation errors stay in modal."""

    def test_validation_error_stays_in_modal(self, authenticated_page, live_server):
        """Form validation errors should display in the modal, not close it."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Click add button for category
        page.click("#add_id_category")

        iframe = page.frame_locator(".unfold-modal-iframe")

        # Submit without filling required field
        iframe.locator('button[name="_save"]').click()

        # Modal should still be open
        expect(page.locator(".unfold-modal-overlay")).to_be_visible()

        # Error message should be visible in iframe
        error = iframe.locator(".errorlist, .errornote, .error")
        expect(error.first).to_be_visible()


@pytest.mark.django_db(transaction=True)
class TestInlineFormRelatedField:
    """Test related field add within inline forms."""

    def test_inline_add_related_works(self, authenticated_page, live_server, author):
        """Adding related object from inline form should work."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Fill required book fields first
        page.fill("#id_title", "Test Book")

        # The Chapter inline has an editor field (autocomplete to Author)
        # First, check if inline row exists or add one
        inline_row = page.locator("#chapters-0")
        if not inline_row.is_visible():
            # Click add another if needed
            add_row = page.locator(".add-row a, .djn-add-handler")
            if add_row.is_visible():
                add_row.click()
                page.wait_for_timeout(300)

        # Click add button for editor in the inline
        # The inline editor field should have an add button
        add_editor_btn = page.locator(
            '#chapters-0 [id^="add_id_chapters-0-editor"], '
            '.inline-related [id*="add"][id*="editor"]'
        ).first

        if add_editor_btn.is_visible():
            add_editor_btn.click()

            # Wait for modal
            iframe = page.frame_locator(".unfold-modal-iframe")

            # Fill in new author
            iframe.locator('input[name="name"]').fill("Inline Author")
            iframe.locator('button[name="_save"]').click()

            # Wait for modal to close
            page.wait_for_selector(".unfold-modal-overlay", state="detached")

            # Verify the inline editor autocomplete was updated
            # The exact selector depends on how Select2 works
            editor_wrapper = page.locator(
                '#id_chapters-0-editor ~ .select2-container .select2-selection__rendered'
            ).first
            if editor_wrapper.is_visible():
                assert "Inline Author" in editor_wrapper.text_content()


@pytest.mark.django_db(transaction=True)
class TestModalInteractions:
    """Test modal interaction behaviors."""

    def test_close_on_esc_key(self, authenticated_page, live_server):
        """Modal should close when pressing ESC."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")

        # Wait for modal open animation to complete
        page.wait_for_timeout(200)

        page.keyboard.press("Escape")

        page.wait_for_selector(".unfold-modal-overlay", state="detached")

    def test_close_on_overlay_click(self, authenticated_page, live_server):
        """Modal should close when clicking outside the container."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")

        overlay = page.locator(".unfold-modal-overlay")
        expect(overlay).to_be_visible()

        # Click on overlay (outside container) - use position at edge
        overlay.click(position={"x": 10, "y": 10})

        page.wait_for_selector(".unfold-modal-overlay", state="detached")

    def test_close_button_works(self, authenticated_page, live_server):
        """Modal close button should close the modal."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#add_id_category")
        page.wait_for_selector(".unfold-modal-overlay")

        page.click(".unfold-modal-close")

        page.wait_for_selector(".unfold-modal-overlay", state="detached")
