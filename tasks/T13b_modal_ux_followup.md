# Task T13B - Modal UX Follow-up (Stack/Resize/Fullscreen)

Goal
- Fix remaining UX issues after T13: overlay flicker, resize edge cases, and fullscreen persistence across nested modals.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus).
- Review with `$unfold-codex-reviewer`.

Scope
- Overlay/stack:
  - Closing a nested modal must not flicker; overlay remains untouched until the last modal closes.
- Resize:
  - Dragging resize handle and releasing over the overlay must not close the modal; only end resize.
  - Maximize past Unfold max screen size when fullscreen is enabled.
- Fullscreen persistence:
  - If modal is fullscreen, opening and closing a nested modal should restore fullscreen state on the previous modal.

Non-goals
- No new JS libraries.

Deliverables
- Updated modal stack/resize logic in `related_modal.js`.
- Tests adjusted if needed.

Acceptance Criteria
- Overlay remains stable when closing nested modals.
- Resize release over overlay does not close the modal.
- Fullscreen state persists when returning from nested modal.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)
