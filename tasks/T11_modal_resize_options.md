# Task T11 - Modal Resize Options

Goal
- Support preset sizes and manual resize for the modal without adding new JS libraries.

Suggested Skill
- Presets only: `$unfold-dev-structured` (Sonnet).
- Manual resize JS: `$unfold-dev-advanced` (Opus).
- Review with `$unfold-codex-reviewer`.

Scope
- Add settings:
  - `UNFOLD_MODAL_SIZE` with presets (e.g., `default`, `large`, `full`).
  - `UNFOLD_MODAL_RESIZE` (boolean) to enable manual resize.
- Implement presets via CSS variables/classes.
- Implement manual resize using plain JS/CSS (no external libs).

Non-goals
- No auto-resize based on iframe content (can be a later task).

Deliverables
- Modal size presets applied from settings.
- Optional manual resize handle/behavior.

Acceptance Criteria
- Preset sizes change modal dimensions.
- Manual resize works when enabled and does not break scroll lock.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage if modal UI changes)
