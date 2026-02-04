# Task T08 - Prepare for unfold_extra.contrib.modal Migration

Goal
- Refactor internal entry points so the app can be moved to `unfold_extra.contrib.modal` later with minimal changes.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).

Scope
- Centralize modal script URL construction in a single Python helper (e.g., `django_unfold_modal.utils.get_modal_scripts()`).
- Update docs/tests to use the helper in `UNFOLD["SCRIPTS"]` instead of hardcoding static paths.
- Ensure no runtime code relies on the app label string outside that helper.

Non-goals
- No rename to `unfold_extra` yet.
- No compatibility shim; keep current package name.

Deliverables
- Helper function that returns a list of static URLs for modal JS.
- README and test settings updated to use the helper.

Acceptance Criteria
- One place defines modal script paths.
- Swapping to `unfold_extra.contrib.modal` would require changing only the helper (and import path).

Tests to run
- `pytest -q`
