# Task T06 - Pytest Cases (Django)

Goal
- Add Django tests that verify permissions and popup response behavior.

Implementation Notes
- Enable modal scripts via Unfold settings (no template override):
  - In `tests/server/testapp/settings.py`, add:
    - `django_unfold_modal` after `unfold` and **before** `django.contrib.admin` (template override for `admin/popup_response.html` must win).
    - `UNFOLD_MODAL_ENABLED = True`
    - `UNFOLD["SCRIPTS"]` to include:
      - `django_unfold_modal/js/related_modal.js`
      - `django_unfold_modal/js/popup_iframe.js`
- Keep `django_unfold_modal` installed so static files resolve and popup_response override is active.

Scope
- Write pytest tests for:
  - Permission checks for add/change/view/delete links on related widgets.
  - _popup=1 rendering and is_popup context.
  - popup_response payloads for add/change/delete.
  - CSRF enforcement.
- Use the test project models/admin created in T01.

Non-goals
- No Playwright UI tests.

Deliverables
- `tests/` pytest files with clear, isolated cases.

Acceptance Criteria
- `pytest -q` passes with new tests.

Tests to run
- `pytest -q`
