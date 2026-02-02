# Task T02 - Package Scaffold (django-unfold-modal)

Goal
- Create the reusable Django app package with Hatch build config and Poetry for dependency management.

Scope
- Add a new Python package directory: `django_unfold_modal/`.
- Add `pyproject.toml` with `[project]` + `[build-system]` (Hatchling) for PyPI builds.
- Keep `tool.poetry` for dependency management (dev/test).
- Add minimal package metadata, version, and dependencies (Django, Unfold).
- Add AppConfig with default settings and static/template discovery.
- Add README with installation and basic usage.

Non-goals
- No functional modal behavior in this task.
- No tests beyond basic import checks.

Deliverables
- `pyproject.toml` for Hatch.
- `django_unfold_modal/__init__.py`, `apps.py`.
- `README.md` (package usage only).

Acceptance Criteria
- `python -c "import django_unfold_modal"` works in project environment.
- Package metadata is valid for build.

Tests to run
- `pytest -q` (if import tests added)
