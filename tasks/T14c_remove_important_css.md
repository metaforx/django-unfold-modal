# Task T14c - Remove `!important` CSS Overrides

Goal
- Eliminate `!important` usage from modal-related styles and replace with proper specificity/token usage.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Scope
- Search modal CSS (including inline style injections) and remove `!important`.
- Replace with correct selectors or Unfold tokens so dark/light mode works without force.
- If a rule relies on `!important`, document the original conflict and fix the selector instead.
- Dark mode fixes (explicit):
  - `unfold-modal-header` must use the same dark theme tokens/behavior as Unfold’s dark mode implementation.
  - `unfold-modal-iframe` background must respect dark mode (no forced light background).
- Hover states must work without `!important` (use proper selectors or tokens).
- Header controls must follow Unfold’s Material Symbols pattern:
  - Replace inline SVGs with `<span class="material-symbols-outlined">…</span>` icons.
  - Use the same button classes/patterns as Unfold’s `related-widget-wrapper-link` controls.
  - Use appropriate icons for close, expand, and minimize (matching Unfold conventions).
  - Example (Material Design Icons / Material Symbols):
    - `<span class="material-symbols-outlined">visibility</span>`

Non-goals
- No functional changes beyond styling correctness.
- No new dependencies or build tooling.

Deliverables
- No `!important` usage in modal CSS or injected styles.
- Dark mode styling remains correct after removal.

Acceptance Criteria
- `rg "!important"` returns no matches in modal CSS/JS.
- Visual regression check passes in light and dark mode.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)
