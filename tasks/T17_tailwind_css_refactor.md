# Task T17 - Move Inline Styles to Tailwind CSS

Goal
- Remove inline style strings from modal JS and move styling to Tailwind 4 CSS.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus).
- Review with `$unfold-codex-reviewer`.
- Optional worker (OpenCode / Qwen 2.5):
  - Use the `opencode` CLI with model `kimi-k2.5` for a lightweight review/execution pass.
  - Script: `scripts/opencode_coder.sh` (pipe input into it).
  - Example: `git diff | scripts/opencode_coder.sh`

Workflow (required)
- Claude orchestrates the subagent run (Opus or OpenCode/Kimi).
- Claude verifies the outcome against acceptance criteria.
- Run Codex CLI review (`$unfold-codex-reviewer`) and fix findings before merge.
- Do not merge automatically; hold on the feature branch for manual review.

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
