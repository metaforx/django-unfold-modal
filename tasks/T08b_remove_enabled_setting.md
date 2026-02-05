# Task T08B - Remove UNFOLD_MODAL_ENABLED Setting

Goal
- Remove `UNFOLD_MODAL_ENABLED` since enablement should be driven by installed apps + Unfold SCRIPTS.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Scope
- Remove `UNFOLD_MODAL_ENABLED` from:
  - `django_unfold_modal/apps.py` defaults
  - `django_unfold_modal/templatetags/unfold_modal.py`
  - README and `CLAUDE.md`
  - `plans/IMMUTABLE_BASE_PLAN.md` (settings list)
  - Tests (`tests/test_package.py`, test settings)
  - Task docs where referenced
- Ensure script inclusion relies solely on `UNFOLD["SCRIPTS"]`.

Non-goals
- No behavior changes beyond removing the unused setting.

Deliverables
- All references removed.
- Tests updated accordingly.

Acceptance Criteria
- No `UNFOLD_MODAL_ENABLED` usage remains in the repo.

Tests to run
- `pytest -q`
