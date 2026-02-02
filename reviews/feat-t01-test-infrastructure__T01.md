# Review Instructions - feat/t01-test-infrastructure (T01)

Branch: feat/t01-test-infrastructure  
Task: tasks/T01_test_infrastructure.md

Scope
- Test project and pytest/Playwright scaffolding only.
- No packaging or modal behavior changes.

Scope Guard (must flag)
- pyproject.toml and CLAUDE.md packaging config changes belong to T02 and should not appear in this branch.

Checklist
- Test project includes models/admin for FK, M2M, OneToOne, raw_id_fields, autocomplete, inline-related fields.
- pytest config points to testapp settings and runs.
- No out-of-scope packaging changes.

Commands
- poetry install --with test,dev
- poetry shell → pytest -q
- (optional) cd tests/server && poetry run python manage.py runserver
