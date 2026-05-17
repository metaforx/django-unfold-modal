# Task T22a - Fix Popup Add Link Override

Context
- T22 implemented a template override in `unfold_modal/templates/unfold/helpers/add_link.html` using `is_popup` + a new setting.
- It does not work because the override is ignored when `unfold_modal` is installed *after* `unfold`, as currently documented in the README. Django resolves templates by app order, so `unfold` wins.

Goal
- Make the popup add-link suppression work without requiring users to reorder `INSTALLED_APPS`.

Preferred Approach
- Minimal changes, template-first.
- Update the original Unfold template directly rather than relying on a shadowed override.

Implementation Notes
- Move or duplicate the conditional into `django-unfold/src/unfold/templates/unfold/helpers/add_link.html`.
- Use a template tag (or settings access) that is always available, even when `unfold_modal` is installed after `unfold`.
  - Option A: add a safe template tag in `unfold` that defers to `django.conf.settings`.
  - Option B: load `unfold_modal_tags` defensively and fall back to `True` if tag not available.
- Ensure the condition only suppresses the header add link when `is_popup` is true; do not affect related-widget add buttons.
- Update docs to clarify behavior and keep `INSTALLED_APPS` order unchanged (unfold first, then unfold_modal).

Deliverables
- Template change in `django-unfold/src/unfold/templates/unfold/helpers/add_link.html`.
- Any supporting template tags/helpers needed for safe access to the setting.
- Doc note that the setting works regardless of app order.

Verification
- Manual: open a classic admin popup (`?_popup=1`) and confirm header add link is hidden when `UNFOLD_MODAL_SHOW_ADD_IN_POPUP = False`.
- Manual: confirm header add link appears when setting is `True` or unset.
- Manual: confirm related-widget "+" buttons still show in popups.

Tests to run
- `pytest -q`
- `pytest --browser chromium`
