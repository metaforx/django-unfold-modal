# Task T11 - Playwright Tests for Nested Modals

Goal
- Verify nested modal behavior and scrolling using Playwright.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus).
- Review with `$unfold-codex-reviewer`.

Scope
- Add UI tests that:
  - Open modal A (related widget).
  - From within modal A, open modal B.
  - Verify modal A is hidden/replaced when modal B opens (single active modal).
  - Save/close B and ensure A is restored and updates.
  - Save A and verify parent form updates.
  - Validate iframe scrolling (content taller than container).

Non-goals
- No visual regression/screenshot testing.

Deliverables
- Playwright tests covering nested modal flow and scrolling.

Acceptance Criteria
- Nested modal flow works end-to-end with replace/restore behavior.
- Only one modal is visible at a time; previous modal is restored after closing nested modal.
- Scroll behavior is confirmed in iframe (e.g., scrollHeight > clientHeight).

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)
