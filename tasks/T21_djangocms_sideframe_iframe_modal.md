# Task T21 - Fix Modal Opening in Django CMS Sideframe Iframe

Goal
- Fix related-object modal opening when Django admin runs inside an iframe (e.g. Django CMS `cms-sideframe`), where modal should open but currently falls back to popup behavior.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus) for investigation.
- Use `$unfold-dev-structured` (Sonnet) for implementation/tests.
- Review with `$unfold-codex-reviewer`.

Worker Plan (required)
- Worker 1: Root-cause analysis (Claude Opus)
  - Reproduce iframe scenario locally and confirm why modal open path is skipped.
  - Validate current iframe mode detection (`window.parent !== window`) and event routing (`postMessage` to parent) against Django CMS sideframe behavior.
  - Produce a short diagnosis note before code changes.
- Worker 2: Implementation (Claude Sonnet)
  - Apply minimal code fix so sideframe admin opens modal in-place.
  - Keep nested modal behavior inside real modal iframes unchanged.
  - Add/adjust automated tests.
- Worker 3: Verification (Claude Sonnet)
  - Execute pytest + Playwright coverage for modal behavior.
  - Run manual reproduction against Django CMS and record observed result.
- Worker 4: Review gate (Codex reviewer)
  - Run review on diff using pipe-first flow: `git diff | codex review`.
  - Fix findings before merge.

Root-Cause Hypothesis
- Current logic treats any iframe context as "modal-iframe child" and forwards related-link open requests to `window.parent`.
- In Django CMS sideframe, parent page is CMS frontend (not modal host), so parent does not open modal.
- Result: modal path is bypassed; Django fallback popup behavior is used.

Implementation Notes
- Context detection:
  - Replace broad iframe check with "inside Unfold modal iframe" check.
  - Suggested approach: use `window.frameElement` and verify it has `.unfold-modal-iframe` (guard with `try/catch`).
  - Only use parent `postMessage` flow when inside actual Unfold modal iframe.
  - If inside non-modal iframe (e.g. CMS sideframe), initialize top-level handlers (`handleShowRelated` / `handleLookupRelated`) and open modal locally.
- Preserve existing nested modal flows:
  - ESC forwarding and dismiss forwarding should still work for true modal-iframe nesting.
  - Keep popup index behavior and dismiss payload compatibility intact.

Scope
- JS runtime context detection and event-routing fix.
- Tests proving modal opens from non-modal iframe hosts.
- Optional tiny test fixture route/template for iframe host page (if needed for Playwright).

Non-goals
- No Django CMS package integration in CI.
- No UI redesign or modal style changes.

Deliverables
- Updated iframe context logic in modal JS core/init path.
- Playwright regression test for "admin inside non-modal iframe host" scenario.
- Short manual verification notes for Django CMS sideframe flow.

Acceptance Criteria
- In Django CMS sideframe (`cms-sideframe`), clicking related-object add/change opens Unfold modal (not popup window).
- Nested modal flow from inside Unfold modal iframe still works.
- No regressions in existing modal/popup tests.

Verification Steps
- Manual (Django CMS):
  1. Open Django CMS page tree and preview page.
  2. Click `.cms-icon-view` to open content preview.
  3. From toolbar (`.cms-toolbar-item`) open Administration (admin in `cms-sideframe` iframe).
  4. Trigger related-object add/change from this admin view.
  5. Confirm `.unfold-modal-overlay` appears and no separate popup window opens.
- Automated:
  - Add a Playwright scenario that loads admin inside a same-origin non-modal iframe host and triggers related add.
  - Assert modal overlay appears in iframe document and popup page count does not increase.

Tests to run
- `pytest -q`
- `pytest --browser chromium`
