# Task T20a - Distribution Name Alignment (django-unfold-modal)

Goal
- Keep the PyPI distribution name as `django-unfold-modal` while the Python package/app name is `unfold_modal`, mirroring the `django-unfold` pattern (`pip install django-unfold` → `INSTALLED_APPS = ["unfold", ...]`).

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Implementation Notes
- Packaging metadata:
  - Keep `project.name = "django-unfold-modal"` and `tool.poetry.name = "django-unfold-modal"`.
  - Ensure the wheel packages only `unfold_modal` (update `tool.hatch.build.targets.wheel.packages` after rename).
  - Confirm `__version__` is still accessible from `unfold_modal.__init__`.
- Documentation:
  - Update README install command to `pip install django-unfold-modal`.
  - Use `unfold_modal` for all `INSTALLED_APPS` and import examples.
  - Add a short note explicitly stating: "Install name: django-unfold-modal, import/app name: unfold_modal."
- Tests:
  - Adjust tests to import `unfold_modal` and keep the distribution name unchanged.
  - Add/adjust a test that `unfold_modal.__version__` matches the distribution version.

Scope
- Documentation + packaging alignment only.
- No behavior changes.

Non-goals
- No attempt to provide `pip install django-unfold` for this package (reserved for upstream `django-unfold`).

Deliverables
- Updated `pyproject.toml` packaging metadata (if needed).
- README clarification on install vs import names.
- Updated tests.

Acceptance Criteria
- `pip install django-unfold-modal` remains the documented install command.
- `INSTALLED_APPS` uses `unfold_modal` everywhere.
- Tests pass with renamed package.

Tests to run
- `pytest -q`
- `pytest --browser chromium`
