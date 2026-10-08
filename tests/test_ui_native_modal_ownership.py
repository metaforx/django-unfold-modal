"""Related-click ownership next to Unfold's native modal (T24/T24a)."""

import pytest
from playwright.sync_api import expect
from testapp.models import Author, Category, Country, Publisher

from tests.ui_helpers import (
    assert_no_native_modal,
    assert_owns_modal,
    click_related,
    wait_related_ready,
)


@pytest.fixture
def category(db):
    return Category.objects.create(name="T24 Fiction")


@pytest.fixture
def author(db):
    return Author.objects.create(name="Jane Doe")


@pytest.fixture
def publisher(db):
    return Publisher.objects.create(name="T24 Publishing")


@pytest.fixture
def country(db):
    return Country.objects.create(name="T24 Country")


@pytest.mark.django_db(transaction=True)
class TestOwnership:
    """A supported related action always opens exactly one unfold-modal modal."""

    @pytest.mark.parametrize("action", ["add", "change", "delete"])
    def test_single_action_opens_only_unfold_modal(
        self, authenticated_page, live_server, category, action
    ):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")
        page.select_option("#id_category", str(category.pk))

        click_related(page, action, "category")
        assert_owns_modal(page, stack_depth=1)

    def test_raw_id_lookup_opens_only_unfold_modal(
        self, authenticated_page, live_server
    ):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#lookup_id_publisher")
        assert_owns_modal(page, stack_depth=1)


@pytest.mark.django_db(transaction=True)
class TestAddRelated:
    def test_add_category_saves_closes_and_updates_field(
        self, authenticated_page, live_server
    ):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        click_related(page, "add", "category")
        assert_owns_modal(page, stack_depth=1)

        iframe = page.frame_locator(".unfold-modal-iframe")
        iframe.locator('input[name="name"]').fill("T24 New Category")
        iframe.locator('button[name="_save"]').click()

        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)

        selected_text = page.locator("#id_category option:checked").text_content()
        assert "T24 New Category" in selected_text


@pytest.mark.django_db(transaction=True)
class TestChangeRelated:
    def test_change_author_saves_closes_and_updates_label(
        self, authenticated_page, live_server, author
    ):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        page.click("#id_author ~ .select2-container")
        page.wait_for_timeout(300)
        page.keyboard.type("Jane")
        page.wait_for_timeout(500)
        page.click(".select2-results__option:has-text('Jane Doe')")
        page.wait_for_timeout(200)

        click_related(page, "change", "author")
        assert_owns_modal(page, stack_depth=1)

        iframe = page.frame_locator(".unfold-modal-iframe")
        name_input = iframe.locator('input[name="name"]')
        name_input.clear()
        name_input.fill("Jane T24 Updated")
        iframe.locator('button[name="_save"]').click()

        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)

        selected_text = page.locator(
            "#id_author ~ .select2-container .select2-selection__rendered"
        ).text_content()
        assert "Jane T24 Updated" in selected_text


@pytest.mark.django_db(transaction=True)
class TestDeleteRelated:
    def test_delete_category_removes_option(
        self, authenticated_page, live_server, category
    ):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")
        page.select_option("#id_category", str(category.pk))

        click_related(page, "delete", "category")
        assert_owns_modal(page, stack_depth=1)

        iframe = page.frame_locator(".unfold-modal-iframe")
        iframe.locator('form:has(input[name="post"]) button[type="submit"]').click()

        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)

        remaining = page.locator("#id_category option").all_text_contents()
        assert category.name not in remaining


@pytest.mark.django_db(transaction=True)
class TestNestedChain:
    def test_main_add_a_add_b_save_b_save_a_updates_main(
        self, authenticated_page, live_server
    ):
        """main -> add A -> add B -> save B -> A updated -> save A -> main updated."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/venue/add/")

        click_related(page, "add", "city")
        assert_owns_modal(page, stack_depth=1)

        iframe_a = page.frame_locator(".unfold-modal-iframe")
        wait_related_ready(iframe_a, "country")
        click_related(iframe_a, "add", "country")
        assert_owns_modal(page, stack_depth=2)

        iframe_b = page.frame_locator(".unfold-modal-iframe").last
        iframe_b.locator('input[name="name"]').fill("T24 Nested Country")
        iframe_b.locator('button[name="_save"]').click()

        page.wait_for_function("window.UnfoldModal.stackDepth() === 1")
        assert_owns_modal(page, stack_depth=1)

        iframe_a_restored = page.frame_locator(".unfold-modal-iframe")
        country_select = iframe_a_restored.locator("#id_country option:checked")
        expect(country_select).to_contain_text("T24 Nested Country")

        iframe_a_restored.locator('input[name="name"]').fill("T24 Nested City")
        iframe_a_restored.locator('button[name="_save"]').click()

        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)

        selected_text = page.locator("#id_city option:checked").text_content()
        assert selected_text.startswith("T24 Nested City")


@pytest.mark.django_db(transaction=True)
class TestRawIdLookup:
    def test_lookup_writes_value_once_with_no_console_error(
        self, authenticated_page, live_server, publisher
    ):
        page = authenticated_page
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # Setter trap: count writes, a double write can end in the same value.
        page.evaluate(
            """
            () => {
                const input = document.getElementById('id_publisher');
                window.__writeCount = 0;
                const proto = Object.getPrototypeOf(input);
                const desc = Object.getOwnPropertyDescriptor(proto, 'value');
                Object.defineProperty(input, 'value', {
                    get() { return desc.get.call(this); },
                    set(v) { window.__writeCount++; desc.set.call(this, v); },
                    configurable: true,
                });
            }
            """
        )

        page.click("#lookup_id_publisher")
        assert_owns_modal(page, stack_depth=1)

        iframe = page.frame_locator(".unfold-modal-iframe")
        iframe.locator(f"a:has-text('{publisher.name}')").click()

        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)

        assert page.input_value("#id_publisher") == str(publisher.pk)
        assert page.evaluate("window.__writeCount") == 1
        assert errors == []


@pytest.mark.django_db(transaction=True)
class TestCloseAndEsc:
    def test_close_button_closes_modal(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        click_related(page, "add", "category")
        assert_owns_modal(page, stack_depth=1)

        page.click(".unfold-modal-close")
        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)

    def test_esc_closes_modal(self, authenticated_page, live_server):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        click_related(page, "add", "category")
        assert_owns_modal(page, stack_depth=1)

        page.keyboard.press("Escape")
        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)


@pytest.mark.django_db(transaction=True)
class TestUnrelatedLinksNotIntercepted:
    def test_breadcrumb_home_link_still_navigates(
        self, authenticated_page, live_server
    ):
        """An ordinary admin navigation link must be left alone."""
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        breadcrumb_link = page.locator("#header-inner").get_by_role(
            "link", name="Books"
        )
        expect(breadcrumb_link).to_be_visible()
        breadcrumb_link.click()
        page.wait_for_url(f"{live_server.url}/admin/testapp/book/")


@pytest.mark.django_db(transaction=True)
class TestViewLinkOwnership:
    """T24a: unfold-modal owns the view-related link everywhere (own-all)."""

    def test_view_link_top_level_single_modal_preserves_form(
        self, authenticated_page, live_server, category
    ):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")
        page.fill("#id_title", "Unsaved Title")
        page.select_option("#id_category", str(category.pk))

        click_related(page, "view", "category")
        assert_owns_modal(page, stack_depth=1)

        iframe = page.frame_locator(".unfold-modal-iframe")
        expect(iframe.locator('input[name="name"]')).to_have_value(category.name)

        page.click(".unfold-modal-close")
        page.wait_for_selector(".unfold-modal-overlay", state="detached")
        assert_no_native_modal(page)

        # Underlying form kept its unsaved values; widget unchanged.
        assert page.input_value("#id_title") == "Unsaved Title"
        checked_value = page.locator("#id_category option:checked").get_attribute(
            "value"
        )
        assert checked_value == str(category.pk)

    def test_view_link_without_selection_is_inert(
        self, authenticated_page, live_server
    ):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        # No selection: the view link has no href, so click it via script.
        toggle = page.locator('[x-ref="relatedWidgetWrappercategory"]')
        if toggle.count() > 0:
            toggle.first.click()

        page.locator("#view_id_category").evaluate("el => el.click()")
        page.wait_for_timeout(300)

        assert page.locator(".unfold-modal-overlay").count() == 0
        assert_no_native_modal(page)

    def test_nested_view_modal_close_restores_previous_modal(
        self, authenticated_page, live_server, country
    ):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/venue/add/")

        click_related(page, "add", "city")
        assert_owns_modal(page, stack_depth=1)

        iframe_a = page.frame_locator(".unfold-modal-iframe")
        wait_related_ready(iframe_a, "country")
        iframe_a.locator('input[name="name"]').fill("Unsaved City")
        iframe_a.locator("#id_country").select_option(str(country.pk))

        click_related(iframe_a, "view", "country")
        assert_owns_modal(page, stack_depth=2)

        page.locator(".unfold-modal-close").last.click()
        page.wait_for_function("window.UnfoldModal.stackDepth() === 1")
        assert_owns_modal(page, stack_depth=1)

        iframe_a_restored = page.frame_locator(".unfold-modal-iframe")
        assert (
            iframe_a_restored.locator('input[name="name"]').input_value()
            == "Unsaved City"
        )


@pytest.mark.django_db(transaction=True)
class TestCoexistSetting:
    """Coexist mode: UNFOLD_MODAL_OVERRIDE_NATIVE = False."""

    def test_coexist_native_add_completes_without_unfold_modal(
        self, authenticated_page, live_server, settings
    ):
        settings.UNFOLD_MODAL_OVERRIDE_NATIVE = False
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")
        page.wait_for_load_state("load")
        assert page.evaluate("window.UnfoldModal.overrideNative") is False

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

    def test_coexist_without_native_modal_has_no_effect(
        self, authenticated_page, live_server, settings
    ):
        settings.UNFOLD_MODAL_OVERRIDE_NATIVE = False
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")
        page.wait_for_load_state("load")

        popup_opened = []
        page.on("popup", lambda p: popup_opened.append(p))

        click_related(page, "add", "category")

        overlay = page.locator(".unfold-modal-overlay")
        native_frame = page.locator("#modal-content iframe.related-modal-frame")
        overlay.or_(native_frame).first.wait_for(state="visible", timeout=5000)

        if native_frame.count() > 0 and native_frame.first.is_visible():
            pytest.skip("Native related modal is available on this Unfold version")

        expect(overlay).to_be_visible()
        assert len(popup_opened) == 0, (
            "a real popup window opened instead of the unfold-modal modal"
        )

    def test_coexist_cms_host_flow_still_owned(
        self, browser, live_server, admin_user, settings
    ):
        settings.UNFOLD_MODAL_OVERRIDE_NATIVE = False
        context = browser.new_context()
        page = context.new_page()

        page.goto(f"{live_server.url}/admin/login/?next=/admin/")
        page.fill('input[name="username"]', "playwrightadmin")
        page.fill('input[name="password"]', "playwrightpass")
        page.click('button[type="submit"], input[type="submit"]')
        page.wait_for_load_state("networkidle")

        book_add_url = "/admin/testapp/book/add/"
        page.goto(f"{live_server.url}/cms-modal-host/?url={book_add_url}")
        page.wait_for_load_state("networkidle")

        cms_iframe = page.frame_locator("#cms-iframe")
        wait_related_ready(cms_iframe, "category", timeout=10000)

        click_related(cms_iframe, "add", "category")

        expect(page.locator(".unfold-modal-overlay")).to_be_visible(timeout=5000)
        assert cms_iframe.locator(".unfold-modal-overlay").count() == 0
        assert_no_native_modal(page)

        context.close()


@pytest.mark.django_db(transaction=True)
class TestRealPopupWindow:
    """A related popup opened as a real window must still complete and write back."""

    def test_real_popup_window_completes_and_writes_back(
        self, authenticated_page, live_server
    ):
        page = authenticated_page
        page.goto(f"{live_server.url}/admin/testapp/book/add/")

        with page.expect_popup() as popup_info:
            page.evaluate(
                "showRelatedObjectPopup(document.getElementById('add_id_category'))"
            )
        popup = popup_info.value
        popup.wait_for_load_state()
        popup.fill('input[name="name"]', "Popup Window Category")
        with popup.expect_event("close"):
            popup.click('button[name="_save"]')

        selected_text = page.locator("#id_category option:checked").text_content()
        assert "Popup Window Category" in selected_text
