# Task T12 - Drawer Presentation Mode

Goal
- Add opt-in drawer presentation using existing JS/CSS only.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Scope
- Support `UNFOLD_MODAL_PRESENTATION = "drawer"` alongside `"modal"`.
- Implement drawer layout via CSS classes.
- JS toggles container class based on setting.

Non-goals
- No new JS libraries.
- No changes to modal behavior beyond layout.

Deliverables
- Drawer styles + JS toggle.
- Document usage in README.

Acceptance Criteria
- Drawer opens from screen edge, overlay present, background scroll locked.
- Modal mode remains unchanged.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage if drawer UI changes)
