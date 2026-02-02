# Task T04b - Popup Lookup (raw_id_fields)

Goal
- Handle the raw_id_fields lookup flow when popups are rendered inside the modal iframe.

Scope
- Ensure lookup selections from popup response (data-popup-opener links) communicate back to the parent window via postMessage.
- Update modal JS and/or popup response template to support `django:popup:lookup` with `chosenId`.

Non-goals
- No changes to non-lookup add/change/delete flows.
- No drawer/fetch modal variants.

Deliverables
- Preferred path: update `django_unfold_modal/templates/admin/popup_response.html` to handle lookup clicks when rendered inside an iframe.
- Add an inline script (or a small static JS file included by the template) that:
  - Detects iframe mode (`!window.opener && window.parent !== window`).
  - Intercepts clicks on `a[data-popup-opener]`, calls `event.preventDefault()`, and posts:
    - `{ type: "django:popup:lookup", chosenId: "<id>" }`
    - to `window.parent` with `window.location.origin` as the target origin.
- Keep the existing fallback to Django’s default popup behavior when `window.opener` exists.
- Parent modal JS already handles `django:popup:lookup` via `dismissRelatedLookupPopup`; no changes required unless needed for compatibility.

Acceptance Criteria
- Selecting a raw_id_fields lookup in the iframe closes the modal and updates the field in the parent.
- Default popup behavior still works when `window.opener` exists (no iframe).

Tests to run
- `pytest -q` (if any unit-level tests are introduced)
