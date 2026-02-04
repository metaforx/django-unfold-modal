# Task T10 - Modal Replacement Stack (Nested Modals)

Goal
- When a nested modal opens, replace the current modal. On save/close/abort, restore the previous modal.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus).
- Review with `$unfold-codex-reviewer`.

Scope
- Implement a modal stack in `related_modal.js`:
  - On open: push current modal state, hide it, then show the new modal.
  - On close/abort: remove current modal, pop and restore previous modal.
- Ensure message handling routes to the active modal only.
- Maintain scroll lock while any modal is open.

Non-goals
- No visual regression tests.
- No new JS libraries.

Deliverables
- Modal stack behavior implemented and documented.
- Previous modal is visible again after closing nested modal.

Acceptance Criteria
- Opening a nested modal hides the previous one.
- Closing/saving/aborting nested modal restores the previous modal with state intact.
- ESC/overlay/close button all follow the same restore behavior.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)
