# Task T21b - Simplify Django CMS Parent-Host Implementation (Lean Refactor)

Goal
- Keep all T21/T21a behavior intact while reducing complexity and duplicated code.
- Make the CMS parent-host path as close as possible to the original clean modal architecture from `origin/development`.
- Preserve backward compatibility for existing users who already adopted T21a integration.

Suggested Skill
- Use `$unfold-dev-advanced` (Opus) for architecture simplification and duplication mapping.
- Use `$unfold-dev-structured` (Sonnet) for implementation/tests.
- Review with `$unfold-codex-reviewer`.

Branching
- Keep development in the current branch (do not create a new feature branch for this task).

Worker Plan (required)
- Worker 1: Simplification analysis (Claude Opus)
  - Build a function-level duplication map between `related_modal.js` and `cms_host.js`.
  - Identify a minimal shared runtime boundary (open/close/stack/resize/maximize/title/header handling).
  - Propose the smallest safe refactor that removes duplicate runtime logic without changing behavior.
- Worker 2: Implementation (Claude Sonnet)
  - Consolidate runtime logic so modal rendering/stack behavior has one implementation path.
  - Reduce CMS-specific code to routing/host bridge responsibilities only.
  - Unify Python config/head generation paths to avoid duplicated assembly logic.
- Worker 3: Verification (Claude Sonnet)
  - Execute pytest + Playwright coverage.
  - Record diff-size reduction and architecture checks (duplicate runtime blocks removed).
- Worker 4: Review gate (Codex reviewer)
  - Run review on diff using pipe-first flow: `git diff | codex review`.
  - Fix findings before merge.

Problem Statement
- T21a fixed CMS parent-window behavior correctly, but introduced a second modal runtime (`cms_host.js`) that mirrors core behavior already implemented in `related_modal.js`.
- CMS configuration and asset-head assembly are also duplicated across `views.py`, template tags, and utility helpers.
- This increases long-term maintenance cost and risk of drift between regular modal and CMS modal flows.

Implementation Notes
- Runtime consolidation
  - Keep a single source of truth for modal stack/render lifecycle (open/close/resize/maximize/iframe load handling).
  - Replace full-featured `cms_host.js` runtime with a thin bridge that:
    - validates origin/sender,
    - tracks source iframe for top-level dismiss routing,
    - delegates rendering/lifecycle to shared runtime functions.
  - Keep message protocol (`django:modal:*`, `django:popup:*`) backward compatible.
- Context detection boundaries
  - Preserve strict Unfold iframe detection from T21 (`.unfold-modal-iframe`).
  - Keep CMS-specific detection where routing is decided (runtime layer), not in generic core state if avoidable.
  - Maintain cross-origin safety via guarded parent/frame access (`try/catch`).
- Config and integration unification
  - Introduce one config resolver used by both JS config endpoint and CMS-head integration.
  - Remove duplicated inline config/head-html assembly logic.
  - Keep one primary public integration path; if both template tag and utility remain, one must delegate to the other.
- Settings simplification
  - Keep current defaults/behavior, but resolve settings through one shared resolver.
  - Prefer fallback model: CMS values inherit from `UNFOLD_MODAL_*` unless explicitly overridden.
  - Avoid repeating preset-to-dimensions mapping in multiple files.

Scope
- JS refactor for shared modal runtime and thinner CMS host bridge.
- Python refactor for single-source config/head generation.
- Test and docs updates aligned with simplified architecture.
- Keep behavior and public integration compatibility from T21a.

Non-goals
- No user-facing UX redesign.
- No direct django CMS dependency in CI.
- No unrelated modal feature work.

Deliverables
- One shared modal runtime path (no second full copy of open/close/resize/maximize stack logic).
- CMS host layer reduced to routing/bridging responsibilities.
- Single source of truth for config generation and CMS head integration.
- Updated tests/docs reflecting simplified architecture.
- Short change notes (one-liners):
  - T21b one-liner: "Consolidate CMS parent-host support onto one shared modal runtime; keep behavior unchanged."
  - Prior T21a one-liner: "When admin iframe is inside Django CMS modal, open Unfold modal in parent document (outside iframe)."

Acceptance Criteria
- CMS modal context still opens Unfold modal in parent document.
- Non-CMS iframe context still opens modal inside iframe.
- Nested modal open/dismiss flow remains correct in CMS parent-host mode.
- No duplicated full runtime blocks remain across CMS host and regular modal JS paths.
- Refactor is net-reductive versus current `feat/t21-cms-sideframe-modal` code size.
- Existing modal/popup behaviors do not regress.

Verification Steps
- Manual (Django CMS simulation)
  1. Open CMS host page with admin iframe in modal wrapper.
  2. Trigger related add/change from admin iframe.
  3. Confirm `.unfold-modal-overlay` renders in parent document.
  4. Open nested related action and confirm dismiss/data propagation still works.
  5. Confirm non-CMS iframe host still renders modal locally in iframe.
- Automated
  - Run existing Playwright scenarios for:
    - CMS parent-host rendering,
    - non-CMS sideframe iframe behavior,
    - direct admin behavior and nested flow.
  - Add/adjust helper assertions that guard against runtime duplication regressions where practical.
- Architecture checks
  - Validate only one primary implementation remains for modal lifecycle functions.
  - Validate config/head generation path resolves through one shared helper.
- Diff checks
  - Compare against current branch head and record net line/file reduction in task/PR notes.

Tests to run
- `pytest -q`
- `pytest --browser chromium`
