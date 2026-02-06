# Task T17a - Remove JS Style Injection (Complete CSS Move)

Goal
- Eliminate `injectStyles()` and inline style injection from JS; all modal styles must live in the CSS bundle.

Context
- `modal_core.js` still injects a `<style>` block and uses inline `style.cssText`. External CSS currently only covers the iframe spinner.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Scope
- Remove `injectStyles()` and `stylesInjected` logic.
- Move all injected CSS rules into the Tailwind CSS file from T17.
- Replace `style.cssText` usage with class assignments + CSS rules.
- Ensure CSS is loaded via Unfold `STYLES` (or equivalent) in testapp config.

Non-goals
- No UI changes beyond CSS relocation.
- No new dependencies.

Deliverables
- No `<style>` injection in JS.
- Modal renders identically using CSS only.

Acceptance Criteria
- `rg -n "injectStyles|style\\.textContent|stylesInjected" django_unfold_modal/static/django_unfold_modal/js` returns no matches.
- Modal visuals unchanged (light/dark mode, hover, header, iframe background).
- `pytest -q` and `pytest --browser chromium` pass.

Tests to run
- `pytest -q`
- `pytest --browser chromium`

Workflow
- Do not merge automatically; keep changes on the feature branch for manual review.
