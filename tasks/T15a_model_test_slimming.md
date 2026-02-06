# Task T15a - Slim Test Models + Align Pytests/Playwright

Goal
- Reduce test models to the minimum needed to cover all Django admin widgets and one level of nested modal interactions.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Scope
- Audit `tests/server/testapp/models.py` and identify redundant models.
- Keep only what’s needed to exercise:
  - standard related widget (FK/ManyToMany add/change)
  - autocomplete/select2 widget
  - raw_id lookup widget
  - inline related add/change
  - one nested modal scenario (optionally a second level in one place if justified)
- Align pytest and Playwright coverage to the reduced model set.
- Playwright coverage must retain all visually important scenarios; do not drop UI assertions because of model slimming.
- If Playwright covers a model that would otherwise be removed, keep it and add an inline comment in the model explaining the UI test dependency.

Non-goals
- No new features.
- No behavior changes in production code.

Deliverables
- Simplified test models with clear justification comments where needed.
- Updated pytest and Playwright tests aligned to the new model set.

Acceptance Criteria
- All widget types are still tested.
- `pytest -q` passes.
- `pytest --browser chromium` passes.
- Playwright still validates the same visual behaviors as before (no functional reduction).

Tests to run
- `pytest -q`
- `pytest --browser chromium`
