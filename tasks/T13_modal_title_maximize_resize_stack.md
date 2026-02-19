# Task T13 - Modal Title, Maximize, Resize UX, Stack Smoothness

Goal
- Improve modal chrome and UX: show iframe page title, add maximize, fix resize/stack behavior, and ensure dark mode styling.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus).
- Review with `$unfold-codex-reviewer`.

Scope
- Titlebar:
  - Display the iframe `<title>` text in the modal header, centered.
  - Respect dark mode colors.
- Maximize:
  - Add a maximize toggle button in the header (icon next to close).
  - Maximize should fill available viewport while keeping a minimal margin (use Unfold container paddings as reference).
- Resize:
  - Refactor resize so mouseup outside the modal/overlay does **not** close the modal; it should only end resize.
  - Allow resizing above preset sizes up to the maximize bounds (not exceeding fullscreen toggle).
- Modal stack UX:
  - On nested modal close, avoid flicker: the top modal fades quickly, previous modal is already present.
  - Keep overlay active until the last modal is closed.

Non-goals
- No new JS libraries.
- No visual regression snapshots.

Deliverables
- Updated `related_modal.js` behavior + styles to support title, maximize, and resize UX fixes.
- CSS updates for titlebar and dark mode.

Acceptance Criteria
- Titlebar shows iframe title, centered, and readable in dark mode.
- Maximize toggles modal size with a visible margin.
- Resizing ends cleanly even if mouseup occurs over overlay.
- Resizing cannot exceed maximize bounds.
- Nested modal close does not flicker; overlay remains until stack is empty.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)
