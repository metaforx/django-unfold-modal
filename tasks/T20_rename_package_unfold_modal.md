# Task T20 - Rename Package to unfold_modal

Goal
- Refactor the project to use `unfold_modal` as the primary package/import name (instead of `django_unfold_modal`) without changing runtime behavior.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Implementation Notes
- Package rename:
  - Rename the Python package folder from `django_unfold_modal/` to `unfold_modal/`.
  - Update all internal imports to `unfold_modal` (no behavioral changes).
- AppConfig:
  - In `unfold_modal/apps.py`, set `name = "unfold_modal"`.
  - Keep `default_settings` unchanged.
  - Decide whether to rename the config class to `UnfoldModalConfig` (and update tests/docs accordingly).
- URL namespace:
  - In `unfold_modal/urls.py`, set `app_name = "unfold_modal"`.
  - Update `reverse()` calls in `unfold_modal/utils.py` to use `unfold_modal:...`.
- Static asset namespace:
  - Move `django_unfold_modal/static/django_unfold_modal/` to `unfold_modal/static/unfold_modal/`.
  - Update all `static("django_unfold_modal/...")` references to `static("unfold_modal/...")`.
- Templates:
  - Move `django_unfold_modal/templates/` to `unfold_modal/templates/`.
  - Update any `{% static %}` references inside templates to the new namespace.
- Packaging metadata:
  - Update `pyproject.toml` to package `unfold_modal` (and only that package unless keeping a compatibility shim).
  - Decide whether to rename the distribution from `django-unfold-modal` to `unfold-modal`; update `project.name`, `tool.poetry.name`, and README install command if so.
  - Update repository URL if the repo is renamed (otherwise leave as-is).
- Docs and examples:
  - Update `README.md` (title, install command, `INSTALLED_APPS`, imports from `unfold_modal.utils`, and URL include path).
  - Update any other docs or notes referencing `django_unfold_modal` (use `rg -n "django_unfold_modal"` to locate).
- Tests and test app:
  - Update `tests/test_package.py` to import `unfold_modal` and assert the new AppConfig name.
  - Update `tests/server/testapp/settings.py` for `INSTALLED_APPS` and `unfold_modal.utils` imports.
  - Update `tests/server/testapp/urls.py` to include `unfold_modal.urls`.
- Compatibility (optional):
  - If backward compatibility is required, add a thin `django_unfold_modal` shim that re-exports from `unfold_modal` and document the deprecation. Ensure static/template paths and URL namespaces remain consistent with the new primary name.

Scope
- Rename package and static/template namespaces to `unfold_modal`.
- Update all imports, URLs, and docs accordingly.

Non-goals
- No UI/behavior changes.
- No refactors beyond renaming/migrating references.

Deliverables
- `unfold_modal/` package directory (renamed from `django_unfold_modal/`).
- Updated static and template paths under `unfold_modal/static/unfold_modal/` and `unfold_modal/templates/`.
- Updated docs/tests/config to reference `unfold_modal`.
- Updated packaging metadata in `pyproject.toml`.

Acceptance Criteria
- All references to the old package name are removed or intentionally retained as a compatibility shim.
- `pytest -q` and `pytest --browser chromium` pass without regressions.
- Behavior is unchanged; only naming and references are updated.

Tests to run
- `pytest -q`
- `pytest --browser chromium`
