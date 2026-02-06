# Task T14a - related_modal.js Refactor Follow-up (Init + Close + Legacy)

Goal
- Apply targeted cleanup rules discovered during review to reduce complexity and remove legacy behavior.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.
- Model note:
  - Qwen‑coder‑3 may be used only for isolated mechanical extraction (e.g., helper functions), not the full refactor.

Scope
- DRY cleanup across all modal JS files:
  - Extract repeated URL/popup parameter handling into a shared helper.
  - Centralize selector/target lookup where the same DOM targets are reused.
  - Reduce duplicate event binding patterns; use single helper to bind or delegate.
  - Keep helpers in a shared module that can be imported by `related_modal.js` and `popup_iframe.js`.
- Additional refactor cleanups across JS modules:
  - Consolidate postMessage types/payloads into shared constants and helpers.
  - Replace JS hover style handlers with CSS (`:hover`) where possible.
  - Avoid per-modal global listeners; register once and route to active modal.
  - Extract repeated SVG/icon strings into helper functions or templates.
- Remove `window.unfoldModal` export unless there is a proven, in-repo consumer.
- Replace `setTimeout(..., 150)` teardown in close logic with `transitionend` handling.
- Collapse the two-stage wait logic into a single initializer:
  - Do not combine `DOMContentLoaded` + polling unless necessary.
  - Prefer a single `initWhenReady()` that either waits for `django.jQuery` or falls back once DOM is ready.
- DRY event handling:
  - Centralize key handling (ESC) into a shared handler function rather than inline anonymous listeners.

Non-goals
- No behavior changes beyond these cleanup rules.
- No new dependencies or build tooling.

Deliverables
- `related_modal.js` (or refactored modules) updated with the above changes.
- If legacy API is retained, document the specific consumer and reason.

Acceptance Criteria
- No hardcoded teardown timers; close uses `transitionend` or equivalent deterministic signal.
- Only one initialization pathway; no redundant wait mechanisms.
- Legacy global export removed unless explicitly justified.

Tests to run
- `pytest -q`
- `pytest --browser chromium` (Playwright UI coverage)

Guidelines (What not to do)
- Do not reintroduce inline CSS strings (T16 covers CSS refactor).
- Do not change modal stack semantics.
