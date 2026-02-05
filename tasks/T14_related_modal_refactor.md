# Task T14 - Refactor related_modal.js (Decompose + Simplify)

Goal
- Reduce `related_modal.js` complexity and size by decomposing into smaller modules and simplifying behavior without changing user-facing functionality.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus).
- Review with `$unfold-codex-reviewer`.

Scope
- Identify feature groups and extract into separate files (loaded via `UNFOLD["SCRIPTS"]`), e.g.:
  - `modal_state.js` (stack, size, fullscreen, active modal)
  - `modal_dom.js` (DOM creation, header buttons, title updates)
  - `modal_events.js` (event listeners, postMessage handling)
  - `modal_resize.js` (resize + maximize)
- Implement a DRY modal stack manager:
  - Single overlay shared across all modals.
  - `openModal()` hides current and pushes it; `closeModal()` pops and restores.
  - Overlay removed only when stack is empty.
- Keep a thin orchestrator file that wires modules.
- No new libraries; use only Django/Unfold-provided JS.
- Maintain existing public behavior: open/close, stack replace/restore, title, resize, fullscreen, dark mode, postMessage.
- Bug to fix while refactoring:
  - When `UNFOLD_MODAL_RESIZE=True`, initial size must still respect `UNFOLD_MODAL_SIZE` preset; currently modal opens larger than the preset.

Non-goals
- No UI redesign.
- No behavior changes beyond bug fixes required by decomposition.

Deliverables
- `related_modal.js` reduced and delegated to smaller files.
- Updated script includes in settings/README if new files are added.

Acceptance Criteria
- Overall logic is easier to audit; no monolithic 900+ line file.
- Functional parity preserved (manual test + existing automated tests).
- Initial modal dimensions match the configured `UNFOLD_MODAL_SIZE` even when resize is enabled.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)
- Add/verify a Playwright assertion for initial modal size vs preset when `UNFOLD_MODAL_RESIZE=True`.

Guidelines (What not to do)
- Do not reintroduce inline CSS strings (T15 will handle CSS refactor).
- Do not add new dependencies or bundlers.
- Do not change the modal stack behavior semantics.
