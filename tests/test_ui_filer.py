"""django-filer file and folder picker tests (T24)."""

import pytest
from django.core.files.base import ContentFile
from filer.models import File, Folder
from playwright.sync_api import expect

from tests.ui_helpers import assert_no_native_modal, assert_owns_modal, click_related


@pytest.fixture
def filer_file(db):
    return File.objects.create(
        folder=None,
        file=ContentFile(b"hello world", name="t24_filer.txt"),
        original_filename="t24_filer.txt",
        mime_type="text/plain",
    )


@pytest.fixture
def filer_folder(db):
    return Folder.objects.create(name="T24 Filer Folder")


def _open_file_picker(page):
    """Click the file widget's lookup link and drill into Unsorted Uploads."""
    page.click("#id_file_lookup")
    assert_owns_modal(page, stack_depth=1)
    iframe = page.frame_locator(".unfold-modal-iframe")
    iframe.get_by_role("link", name="Unsorted Uploads").first.click()
    return iframe


@pytest.mark.django_db(transaction=True)
class TestOwnAllFilePicker:
    def test_pick_file_writes_value_and_label(
        self, authenticated_page, live_server, filer_file
    ):
        page = authenticated_page
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(f"{live_server.url}/admin/testapp/mediaasset/add/")

        iframe = _open_file_picker(page)
        iframe.locator(
            f"a.js-dismiss-image:has-text('{filer_file.label}')"
        ).first.click()

        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)

        assert page.input_value("#id_file") == str(filer_file.pk)
        label = (
            page.locator("#id_file_lookup")
            .locator("xpath=ancestor::span[contains(@class,'filerFile')]")
            .locator(".description_text")
        )
        assert filer_file.label in label.text_content()
        assert errors == []

    def test_close_button_leaves_widget_unchanged(
        self, authenticated_page, live_server
    ):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/mediaasset/add/")

        page.click("#id_file_lookup")
        assert_owns_modal(page, stack_depth=1)

        page.click(".unfold-modal-close")
        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)
        assert page.input_value("#id_file") == ""

    def test_esc_leaves_widget_unchanged(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/mediaasset/add/")

        page.click("#id_file_lookup")
        assert_owns_modal(page, stack_depth=1)

        page.keyboard.press("Escape")
        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)
        assert page.input_value("#id_file") == ""


@pytest.mark.django_db(transaction=True)
class TestOwnAllFolderPicker:
    def test_pick_folder_writes_value_and_label(
        self, authenticated_page, live_server, filer_folder
    ):
        page = authenticated_page
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(f"{live_server.url}/admin/testapp/mediaasset/add/")

        page.click("#folder")
        assert_owns_modal(page, stack_depth=1)

        iframe = page.frame_locator(".unfold-modal-iframe")
        iframe.locator(
            f"a.js-dismiss-folder[data-label='{filer_folder.pretty_logical_path}']"
        ).first.click()

        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)

        assert page.input_value("#id_folder") == str(filer_folder.pk)
        assert errors == []

    def test_close_button_leaves_widget_unchanged(
        self, authenticated_page, live_server
    ):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/mediaasset/add/")

        page.click("#folder")
        assert_owns_modal(page, stack_depth=1)

        page.click(".unfold-modal-close")
        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)
        assert page.input_value("#id_folder") == ""

    def test_esc_leaves_widget_unchanged(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/mediaasset/add/")

        page.click("#folder")
        assert_owns_modal(page, stack_depth=1)

        page.keyboard.press("Escape")
        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)
        assert page.input_value("#id_folder") == ""


@pytest.mark.django_db(transaction=True)
class TestCoexistFiler:
    """UNFOLD_MODAL_OVERRIDE_NATIVE = False: Filer stays owned everywhere."""

    def test_coexist_file_picker_still_opens_and_completes(
        self, authenticated_page, live_server, filer_file, settings
    ):
        settings.UNFOLD_MODAL_OVERRIDE_NATIVE = False
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/mediaasset/add/")
        page.wait_for_load_state("load")
        assert page.evaluate("window.UnfoldModal.overrideNative") is False

        iframe = _open_file_picker(page)
        iframe.locator(
            f"a.js-dismiss-image:has-text('{filer_file.label}')"
        ).first.click()

        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)
        assert page.input_value("#id_file") == str(filer_file.pk)

    def test_coexist_folder_picker_still_opens_and_completes(
        self, authenticated_page, live_server, filer_folder, settings
    ):
        settings.UNFOLD_MODAL_OVERRIDE_NATIVE = False
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/mediaasset/add/")
        page.wait_for_load_state("load")

        page.click("#folder")
        assert_owns_modal(page, stack_depth=1)

        iframe = page.frame_locator(".unfold-modal-iframe")
        iframe.locator(
            f"a.js-dismiss-folder[data-label='{filer_folder.pretty_logical_path}']"
        ).first.click()

        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)
        assert page.input_value("#id_folder") == str(filer_folder.pk)

    def test_coexist_ordinary_related_add_on_same_page_goes_native(
        self, authenticated_page, live_server, settings
    ):
        """A plain FK next to the Filer widgets still opens Unfold's native modal."""
        settings.UNFOLD_MODAL_OVERRIDE_NATIVE = False
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/mediaasset/add/")
        page.wait_for_load_state("load")

        click_related(page, "add", "category")

        overlay = page.locator(".unfold-modal-overlay")
        native_frame = page.locator("#modal-content iframe.related-modal-frame")
        overlay.or_(native_frame).first.wait_for(state="visible", timeout=5000)

        if not (native_frame.count() > 0 and native_frame.first.is_visible()):
            pytest.skip("Native related modal is not available on this Unfold version")

        assert overlay.count() == 0, "unfold-modal overlay opened in coexist mode"

        native_iframe = page.frame_locator("#modal-content iframe.related-modal-frame")
        native_iframe.locator('input[name="name"]').fill("Coexist Category")
        native_iframe.locator('button[name="_save"]').click()

        expect(native_frame).to_be_hidden()
        selected_text = page.locator("#id_category option:checked").text_content()
        assert "Coexist Category" in selected_text
