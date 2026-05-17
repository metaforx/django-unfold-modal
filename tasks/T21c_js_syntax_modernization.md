# Task T21c - Modernize JS Syntax in New Modal Additions

Goal
- Align newly added JS files with the modern syntax style already used in `unfold_modal/static/unfold_modal/js/modal_core.js`.
- Keep behavior identical; syntax-only cleanup.

Suggested Skill
- Use `$unfold-dev-structured` (Opus).
- Review with `$unfold-codex-reviewer`.

Implementation Notes
- Use `modal_core.js` as the syntax reference.
- Audit JS files added in the T21/T21a/T21b stream and modernize declaration style where needed.
- Primary target: `unfold_modal/static/unfold_modal/js/cms_host.js`.
- Replace `var` with `const` or `let` based on reassignment semantics.
- Keep function and control-flow behavior unchanged; no functional refactors.
- Preserve all event wiring, message payloads, guard checks, and try/catch boundaries.

Scope
- JS syntax updates only (declaration/style-level modernization).
- No behavior changes.

Non-goals
- No protocol changes for `postMessage`.
- No modal lifecycle logic changes.
- No CSS/template/Python changes.

Deliverables
- Updated JS files using modern declaration patterns consistent with `modal_core.js`.
- Clean diff with no behavior or API changes.

Acceptance Criteria
- No `var` remains in targeted new JS additions unless technically required (and justified in review notes).
- Runtime behavior for modal open/close/dismiss and nested flow is unchanged.
- Existing tests pass.

Tests to run
- `pytest -q`
- `pytest --browser chromium`
