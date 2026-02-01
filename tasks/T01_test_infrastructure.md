# Task T01 - Test Infrastructure and Demo Project

Goal
- Create a minimal Django test project with models and admin configurations that cover all required related-object scenarios.

Scope
- Add a Django test project inside this repo (not inside django-unfold).
- Include models and admin registrations to cover:
  - ForeignKey select
  - ManyToMany select
  - OneToOne
  - raw_id_fields lookup
  - autocomplete_fields (Select2)
  - inline form related fields (within inline forms only)
- Add pytest configuration and helpers for Django tests.
- Add Playwright configuration (pytest-playwright or JS runner) but do not write UI tests yet.

Non-goals
- Do not implement modal behavior in this task.
- Do not override templates in this task.

Deliverables
- New test project (settings, urls, admin site, models, fixtures).
- pytest.ini or pyproject pytest config.
- Playwright config stub.

Acceptance Criteria
- `pytest -q` runs and collects tests (even if empty) without errors.
- Test project can start via `python manage.py runserver` with Unfold enabled.

Tests to run
- `pytest -q`

Notes
- If Playwright needs browser installs, request escalated permissions only when required.

