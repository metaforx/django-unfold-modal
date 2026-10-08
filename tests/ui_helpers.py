"""Helpers for related-widget UI tests; work on a Page, Frame or FrameLocator."""

from __future__ import annotations

_ACTIONS = ("add", "change", "view", "delete")


def _toggle_locator(page_or_frame, name):
    """Locator for the related widget's dropdown toggle (Unfold >=0.86)."""
    return page_or_frame.locator(f'[x-ref="relatedWidgetWrapper{name}"]')


def _link_locator(page_or_frame, action, name):
    """Locator for the `action` link (add/change/view/delete) of `name`."""
    return page_or_frame.locator(f"#{action}_id_{name}")


def _any_action_link_locator(page_or_frame, name):
    """Locator matching whichever action link(s) of `name` are rendered."""
    selector = ", ".join(f"#{action}_id_{name}" for action in _ACTIONS)
    return page_or_frame.locator(selector)


def wait_related_ready(page_or_frame, name, timeout=5000):
    """Wait until the related widget `name` has rendered (toggle or link attached)."""
    toggle = _toggle_locator(page_or_frame, name)
    links = _any_action_link_locator(page_or_frame, name)
    toggle.or_(links).first.wait_for(state="attached", timeout=timeout)


def click_related(page_or_frame, action, name):
    """Click a related link of widget `name`, opening its dropdown if needed."""
    link = _link_locator(page_or_frame, action, name).first
    if not link.is_visible():
        _toggle_locator(page_or_frame, name).first.click()
        link.wait_for(state="visible")
    link.click()


def assert_no_native_modal(page):
    """Assert Unfold's native related modal is not open in any frame of `page`."""
    for frame in page.frames:
        locator = frame.locator("#modal-content iframe.related-modal-frame")
        for i in range(locator.count()):
            assert not locator.nth(i).is_visible(), (
                f"Unfold's native related modal is open in frame {frame.url!r}"
            )


def assert_owns_modal(page, stack_depth=None):
    """Assert one visible unfold-modal overlay, no native modal, optional depth."""
    if stack_depth is not None:
        page.wait_for_function(
            "depth => document.querySelectorAll('.unfold-modal-overlay').length === depth",
            arg=stack_depth,
        )
    visible_overlays = page.locator(".unfold-modal-overlay:visible")
    count = visible_overlays.count()
    assert count == 1, (
        f"expected exactly one visible .unfold-modal-overlay, found {count}"
    )
    assert_no_native_modal(page)
    if stack_depth is not None:
        actual = page.evaluate("window.UnfoldModal.stackDepth()")
        assert actual == stack_depth, (
            f"expected UnfoldModal.stackDepth() == {stack_depth}, got {actual}"
        )
