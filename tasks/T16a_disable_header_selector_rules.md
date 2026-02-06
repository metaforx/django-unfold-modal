# Task T16a - Header Suppression: Stable Selectors + Strong Playwright Assert

Goal
- Fix header suppression so it works reliably and is validated by a strict Playwright check.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Optional: Opus for a short analysis pass to choose the most stable iframe header selectors, then Sonnet for implementation.
- Review with `$unfold-codex-reviewer`.

Scope
- Ensure `UNFOLD_MODAL_DISABLE_HEADER=True` actually hides the header in the iframe.
- Do **not** use styling classes (e.g., `border-b`) as selectors.
- Do **not** inline selectors in multiple places; define selector constants.
- Allowed selectors: stable IDs or structural containers (e.g., `#header-inner`, `#main`).
- Disallow selectors that only represent styling classes.

Playwright (must be strict)
- Add a visual/DOM assertion that header is **absent** when disabled.
- Add a visual/DOM assertion that header is **present** when disabled is false.
- Ensure the test fails if a styling-class selector silently stops matching.

Non-goals
- No UI changes beyond header visibility.
- No new dependencies.

Deliverables
- Stable selector constants used for header suppression logic.
- Playwright test(s) that actually verify header presence/absence.

Acceptance Criteria
- Header hides only when `UNFOLD_MODAL_DISABLE_HEADER=True`.
- Tests fail if header remains visible or selector breaks.
- `pytest -q` and `pytest --browser chromium` pass.

Tests to run
- `pytest -q`
- `pytest --browser chromium`
