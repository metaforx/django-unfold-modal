# Task T21a - Django CMS Parent-Window Modal Host (Render Outside Iframe)

Goal
- When Django admin is embedded inside a Django CMS modal, open Unfold related-object modals in the parent window (CMS modal container), not inside the admin iframe.
- Keep existing behavior for non-CMS iframe hosts unchanged.
- Allow CMS-parent modal presentation settings to differ from regular admin modal settings.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus) for upstream selector analysis and cross-window architecture.
- Use `$unfold-dev-structured` (Sonnet) for implementation/tests.
- Review with `$unfold-codex-reviewer`.

Branching
- Keep development in the current branch (do not create a new feature branch for this task).

Worker Plan (required)
- Worker 1: Upstream Django CMS targeting analysis (Claude Opus)
  - Inspect django CMS source on GitHub and identify exact modal container selectors/classes for active CMS modal wrappers.
  - Document exact selectors and version compatibility notes in the PR/task comments.
  - Define safe fallback selector strategy if upstream classes differ across versions.
- Worker 2: Implementation (Claude Sonnet)
  - Add parent-window host rendering path for CMS modal context.
  - Add frontend asset-loading integration for non-admin parent pages.
  - Add separate CMS modal settings (fullscreen default).
- Worker 3: Verification (Claude Sonnet)
  - Execute pytest + Playwright coverage.
  - Run manual scenario notes for CMS modal flow.
- Worker 4: Review gate (Codex reviewer)
  - Run review on diff using pipe-first flow: `git diff | codex review`.
  - Fix findings before merge.

Problem Statement
- T21 fixed non-modal iframe hosts by opening modal locally in iframe.
- For Django CMS modal usage, this creates nested modals where Unfold modal is inside iframe instead of being rendered in the CMS parent modal layer.
- Desired behavior: if admin iframe is inside Django CMS modal, render Unfold modal in parent document.

Implementation Notes
- Context detection
  - Keep existing Unfold iframe detection for true Unfold nested modal iframes (`.unfold-modal-iframe`).
  - Add new detection path: "iframe is embedded inside Django CMS modal container in parent document".
  - Determine exact selector(s) from django CMS GitHub source; do not hardcode guessed selectors without verification.
  - Guard parent DOM access with `try/catch` (cross-origin-safe fallback).
- Parent host rendering
  - Introduce a parent-host runtime module (frontend-safe) that can:
    - Listen for child iframe `postMessage` open requests.
    - Render Unfold modal overlay/container in parent document.
    - Route dismiss/ESC/nested modal messages correctly.
  - Keep message types backward compatible with existing modal protocol.
- Frontend (non-admin parent) integration
  - Parent page is not Django admin; it must still load required modal JS/CSS and config.
  - Add template-tag based integration path compatible with CMS templates (`cms_tags` / Sekizai flow).
  - Follow the same integration pattern used in `django-unfold-extra` for frontend theme/script loading where appropriate.
  - If a simpler/cleaner integration is found, use it and document why.
- Settings split (regular modal vs CMS-parent modal)
  - Add dedicated CMS modal settings independent from regular `UNFOLD_MODAL_*`.
  - Defaults:
    - CMS modal presentation should default to fullscreen.
    - Regular Unfold modal settings remain unchanged.
  - Proposed setting group (exact names can be adjusted consistently):
    - `UNFOLD_CMS_MODAL_SIZE` (default: `"full"`)
    - `UNFOLD_CMS_MODAL_RESIZE` (default: `False`)
    - `UNFOLD_CMS_MODAL_DISABLE_HEADER` (default: `True`)
  - Ensure config JS exposes both normal modal config and CMS-parent modal config.

Scope
- JS context detection and message-routing extension for CMS modal parent host.
- Parent-host rendering runtime for non-admin frontend container.
- Template tag + documentation for CMS frontend asset loading.
- Settings + config transport for CMS modal presentation overrides.
- Automated tests (pytest + Playwright) and manual verification notes.
- Keep JS changes minimal and localized; avoid broad refactors.
- README must be updated with end-user implementation steps for CMS mode.

Non-goals
- No direct django CMS dependency in CI.
- No visual redesign beyond settings-driven size/presentation changes.
- No breaking changes to existing Unfold admin modal behavior.

Deliverables
- Updated modal runtime supporting parent-window rendering for CMS modal context.
- New frontend host integration entrypoint (template tag and required assets/config).
- Separate CMS modal settings with fullscreen default.
- Playwright coverage for CMS modal simulation and regression checks.
- README/docs section describing CMS frontend integration and settings.
- README "How to use in Django CMS frontend" instructions (user-facing), including:
  - Required settings and defaults for CMS modal mode.
  - How to keep regular Unfold modal settings different from CMS modal settings.
  - Template integration snippet for CMS frontend/container page (how to load styles/scripts/config outside admin).
  - Minimal migration note for existing T21 users ("inside iframe" behavior vs new optional parent-render mode).
- Short change notes (one-liners):
  - T21a one-liner: "When admin iframe is inside Django CMS modal, open Unfold modal in parent document (outside iframe)."
  - Prior T21 one-liner: "Non-modal iframe hosts (e.g. CMS sideframe) open Unfold modal locally in iframe; only true `.unfold-modal-iframe` forwards to parent."

Acceptance Criteria
- If admin runs in iframe inside Django CMS modal container, related-object action opens Unfold modal in parent document (outside iframe).
- If admin runs in non-CMS iframe host, existing T21 behavior remains (modal opens inside iframe).
- Nested modal flow still works when opened from within CMS-parent rendered modal.
- CMS modal settings are independent from regular modal settings; fullscreen is default for CMS mode.
- Existing modal/popup flows do not regress.
- README contains complete user setup steps for CMS mode with copy-paste-ready settings/template examples.

Verification Steps
- Manual (Django CMS)
  1. Open CMS frontend page and launch a CMS modal that embeds admin iframe.
  2. Trigger related-object add/change from iframe admin form.
  3. Confirm `.unfold-modal-overlay` is rendered in parent CMS page (not iframe document).
  4. Confirm nested related open/dismiss still works.
  5. Confirm CMS-specific fullscreen default is applied.
- Automated
  - Add Playwright fixture route/template simulating CMS modal host:
    - Parent page contains a modal wrapper div with verified django CMS class selector(s).
    - Admin is loaded in iframe within that wrapper.
  - Assertions:
    - Overlay appears in parent document.
    - Overlay does not appear in iframe document for CMS modal host case.
    - Non-CMS iframe host still opens inside iframe (regression guard).
    - No popup window opens.
    - CMS settings override (fullscreen default / custom override) is respected.
- Docs validation
  - Verify README instructions are sufficient for a user to enable CMS parent-render mode without reading source code.
  - Verify documented defaults match actual runtime defaults for both regular and CMS modal settings.

Tests to run
- `pytest -q`
- `pytest --browser chromium`
