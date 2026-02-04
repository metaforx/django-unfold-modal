# Task T10 - Playwright Tests for Nested Modals

Goal
- Verify nested modal behavior and scrolling using Playwright.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus).
- Review with `$unfold-codex-reviewer`.

Scope
- Add UI tests that:
  - Open modal A (related widget).
  - From within modal A, open modal B.
  - Save B and ensure A remains open and updates.
  - Save A and verify parent form updates.
  - Validate iframe scrolling (content taller than container).

Non-goals
- No visual regression/screenshot testing.

Deliverables
- Playwright tests covering nested modal flow and scrolling.

Acceptance Criteria
- Nested modal flow works end-to-end without breaking parent modal.
- Scroll behavior is confirmed in iframe (e.g., scrollHeight > clientHeight).

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)
