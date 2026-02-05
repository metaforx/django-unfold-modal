# Task T14 - Move Inline Styles to Tailwind CSS

Goal
- Remove inline style strings from modal JS and move styling to Tailwind 4 CSS.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus).
- Review with `$unfold-codex-reviewer`.

Scope
- Replace JS `style.cssText` usage with CSS classes.
- Add a dedicated stylesheet (Tailwind 4) for modal components.
- Follow Tailwind setup patterns from `unfold_extra/src/` (package.json, vite.config.ts, build pipeline).
- Titlebar has to respect dark mode. Follow unfold dark mode implementation for consistency.

Non-goals
- No UI/behavior changes beyond CSS refactor.
- No new JS libraries.

Deliverables
- Tailwind CSS file for modal styles.
- JS updated to use classes only.
- Build instructions updated if required.

Acceptance Criteria
- Modal renders identically (layout, colors, spacing, transitions).
- No inline `style.cssText` remains in modal JS.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)
