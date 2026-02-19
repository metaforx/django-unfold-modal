# Task T09 - Nested Relations + Long Form Models

Goal
- Add richer test models to exercise nested modals and scrollable iframe content.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Scope
- Add models with:
  - Long forms (many fields) to force iframe scrolling.
  - Nested relations (A -> B -> C) so creating B from A can open a modal to create C.
- Register in admin with related widgets that expose add/change links.

Non-goals
- No UI or JS changes beyond what is needed to expose the test scenarios.

Deliverables
- New models + admin registration in the test app.
- Fixtures for test data where needed.

Acceptance Criteria
- Long form in modal requires scrolling.
- Nested modal flow can be triggered (A opens modal for B, B opens modal for C).

Tests to run
- `pytest -q` (if any unit tests added)
