# Task T13C - Modal UX Follow-up (Fullscreen Button + Resize Limit)

Goal
- Finalize remaining UX details after T13B: fullscreen button placement and resize limits.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Scope
- Fullscreen button placement:
  - Move fullscreen/maximize button to the **left** corner of the modal topbar (not next to close).
- Resize limits:
  - Allow resizing beyond `UNFOLD_MODAL_SIZE="large"` up to the fullscreen/maximized bounds.

Non-goals
- No new JS libraries.
- No changes to modal stack behavior.

Deliverables
- Updated modal header layout and resize logic in `related_modal.js` (and CSS if needed).

Acceptance Criteria
- Fullscreen button appears on the left side of the titlebar.
- Resize can exceed "large" preset up to fullscreen bounds.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)
