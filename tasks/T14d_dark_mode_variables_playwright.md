# Task T14d - Dark Mode Tokens + Playwright Regression

Goal
- Align modal styling with Unfold’s actual CSS variables/tokens and prevent dark‑mode regressions.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Scope
- Replace incorrect modal CSS vars (e.g., `--unfold-border-color`, `--unfold-bg-color`) with the correct Unfold tokens.
- Ensure modal header/background match Unfold’s dark mode patterns (e.g., `var(--color-base-900)` and related tokens).
- Add a Playwright test that validates dark‑mode styling with an empty modal.

Playwright steps (explicit)
- Force browser to dark mode.
- Open an empty modal (no content).
- Assert modal background is dark (matches Unfold base‑900 token).
- Assert `.unfold-modal-header` uses dark background color.

Non-goals
- No UI redesign.
- No new dependencies.

Deliverables
- Updated CSS token usage for modal surfaces.
- Playwright test covering dark‑mode modal background/header.

Acceptance Criteria
- Dark mode modal background/header are correct per Unfold tokens.
- Playwright test fails if modal uses light background in dark mode.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)
