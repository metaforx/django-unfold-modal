# Task T14b - Modal Event Invariants (Topmost Routing + Single Listeners)

Goal
- Enforce a clear event-handling invariant: all global event handlers act on the topmost modal only.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus) for deeper refactor reasoning.
- Review with `$unfold-codex-reviewer`.

Scope
- Register global listeners once (e.g., `document`/`window` handlers for ESC, resize, mouseup).
- In each handler, resolve the active modal at execution time (`getActiveModal()`).
- Remove any per‑modal global listener registration or cleanup logic.
- Keep modal‑local listeners (e.g., overlay click inside a specific modal) scoped to that modal instance.

Non-goals
- No UI changes.
- No changes to modal stack behavior beyond enforcing the routing invariant.

Deliverables
- Event handling refactor applied to modal JS modules.
- A short note in code comments explaining the “topmost modal only” invariant.

Acceptance Criteria
- Only one global handler per event type is registered.
- ESC, resize, and mouseup always act on the current active modal.
- No regressions in nested modal behavior.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)

Guidelines (What not to do)
- Do not add new dependencies.
- Do not reintroduce inline CSS strings.
