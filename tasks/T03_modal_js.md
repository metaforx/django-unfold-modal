# Task T03 - Modal JS Core (iframe)

Goal
- Implement the JS module that intercepts related-object events and opens a modal iframe.

Scope
- Create `django_unfold_modal/static/django_unfold_modal/js/related_modal.js`.
- Use django.jQuery to listen for:
  - `django:show-related` (add/change/view/delete)
  - `django:lookup-related` (raw_id lookup)
- Prevent default popup behavior and open a modal overlay.
- Ensure iframe URL includes `_popup=1`.
- Set iframe `name` to match Django's expected naming scheme for dismiss* functions.
- Add scroll lock on body without page jump.
- ESC closes modal.
- Modal body scrolls; background does not.

Non-goals
- Do not add drawer implementation.
- Do not add fetch-inject adapter (reserve hook only).

Deliverables
- JS module with modal creation, open/close, and message handling.
- Optional minimal CSS only if needed.

Acceptance Criteria
- Manual flow: clicking related widget actions opens modal (not popup).
- Modal closes via ESC.
- Background does not scroll while modal open.

Tests to run
- `pytest -q` (if any unit-level JS tests are introduced)

