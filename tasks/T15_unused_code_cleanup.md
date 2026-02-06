# Task T15 - Unused Code/Test Cleanup

Goal
- Identify and remove unused code or tests, or wire them in if they are required but currently unreferenced.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Scope
- Audit for unused files and dead code paths.
- Remove or integrate the following if confirmed unused:
  - `django_unfold_modal/static/django_unfold_modal/css/related_modal.css` (not referenced in templates or settings).
  - `django_unfold_modal/templatetags/unfold_modal.py` and `UNFOLD_MODAL_ENABLED` setting (no template usage).
- Verify there are no stray or non‑collected tests in `tests/`.
- If a file is needed, add the missing wiring (e.g., include CSS via Unfold `STYLES`) instead of deleting.

Non-goals
- No feature changes beyond cleanup/wiring.
- No new dependencies.

Deliverables
- Unused files removed or properly referenced.
- Documentation updated if behavior changes (e.g., new required `STYLES` include).

Acceptance Criteria
- `pytest -q` passes.
- `rg -n "related_modal\\.css" -S` shows either a valid inclusion or the file is gone.
- No unused tests remain (all test files are collected by pytest).

Tests to run
- `pytest -q`
