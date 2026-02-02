# Review Instructions - feat/t02-package-scaffold (T02)

Branch: feat/t02-package-scaffold  
Task: tasks/T02_package_scaffold.md

Scope
- Package scaffold only (Hatch build + Poetry deps).
- AppConfig + README.
- No modal behavior or template/JS changes.

Checklist
- `pyproject.toml` includes `[project]` + `[build-system]` (Hatchling) and `tool.poetry` with `package-mode = false`.
- `django_unfold_modal/` package exists with `__init__.py` + `apps.py`.
- README includes install + INSTALLED_APPS guidance.
- Basic import tests exist and pass.

Notes
- Resolved: removed `default_app_config` from `django_unfold_modal/__init__.py` (deprecated in modern Django).
- Resolved: avoid settings mutation in `AppConfig.ready()`; use `getattr(settings, ...)` at read time.

Commands
- poetry install --with test,dev
- poetry run pytest -q
