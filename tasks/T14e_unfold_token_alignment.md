# Task T14e - Align Modal Styling to Unfold Tokens Only

Goal
- Remove hardcoded RGB values and incorrect variables in modal styles; use Unfold’s Tailwind token variables (`--color-base-*`, `--color-primary-*`) exclusively.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus) for accurate token mapping.
- Review with `$unfold-codex-reviewer`.

Scope
- Replace incorrect modal variables:
  - Remove `--unfold-border-color`, `--unfold-bg-color` usage.
  - Remove any hardcoded `rgb(...)` values in modal styles.
- Align dark mode styling to Unfold token values:
  - Use `var(--color-base-900)` (or correct dark background token) for modal container/header.
  - Use appropriate text tokens (e.g., `var(--color-base-200)` / `var(--color-base-500)` as appropriate).
- Verify Unfold’s actual dark theme palette usage and map modal elements accordingly.

Non-goals
- No UI redesign.
- No new dependencies.

Deliverables
- Modal styles use only Unfold token variables.
- No hardcoded RGB values remain in modal CSS.

Acceptance Criteria
- `rg "rgb\\("` finds no matches in modal CSS/JS styles.
- Dark mode modal background/header colors match Unfold’s token scheme.
- Theme overrides from Unfold continue to work.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)
