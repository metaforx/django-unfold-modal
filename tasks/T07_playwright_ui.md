# Task T07 - Playwright UI Tests

Goal
- Add Playwright tests for end-to-end admin modal behavior.

Scope
- Implement UI tests for:
  - Add related from normal select updates field.
  - Change related updates label (Select2 autocomplete).
  - raw_id lookup selection updates field.
  - Validation error stays in modal.
  - Inline form related field add works.
  - Modal DOM assertions after opening related widget:
    - `.unfold-modal-overlay` is present and visible.
    - `.unfold-modal-container` is present.
    - `.unfold-modal-iframe` is present and has a `_popup=1` URL.
    - `body` scroll is locked (overflow hidden) while modal is open.

Non-goals
- No visual regression tests.

Deliverables
- Playwright test suite integrated with the test project.

Acceptance Criteria
- All Playwright tests pass locally.

Tests to run
- `pytest -q` (if using pytest-playwright)
- or `npx playwright test` (if using JS runner)
