# Task T06 - Pytest Cases (Django)

Goal
- Add Django tests that verify permissions and popup response behavior.

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

