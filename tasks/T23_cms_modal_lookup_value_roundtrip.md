# Task T23 - CMS Modal Lookup Value Roundtrip Loss (raw_id_fields)

Context
- In CMS parent-host mode (`{% unfold_modal_cms_head %}`), opening Unfold modals works.
- Selecting an object in a lookup popup (`raw_id_fields`) closes the modal, but the chosen ID is not written back to the source widget.
- Symptom: FK raw-id input in the source modal/iframe remains empty after selection.

Goal
- Make lookup selection roundtrip reliable in CMS-hosted modal flows (top-level and nested).

Suggested Skill / Model
- Use `$unfold-dev-advanced` (Opus) for root-cause analysis and message-flow validation.
- Use `$unfold-dev-structured` (Sonnet) for implementation and tests.
- Review with `$unfold-codex-reviewer`.

Worker Plan (required)
- Worker 1: Root-cause analysis (Opus)
  - Trace event flow end-to-end:
    - `popup_iframe.js` (`django:popup:lookup` emit)
    - `cms_host.js` (`django:modal:dismiss` forwarding)
    - `related_modal.js` (`handleForwardedDismiss` -> `dismissRelatedLookupPopup`)
  - Confirm where target field resolution fails (`win.name` / popup index / iframe source checks).
- Worker 2: Implementation (Sonnet)
  - Apply minimal fix for reliable writeback to raw-id input.
  - Keep existing add/change/delete dismiss behavior unchanged.
  - Add robust fallback path if Django dismiss helper cannot resolve target field.
- Worker 3: Verification (Sonnet)
  - Add regression test for CMS-hosted raw_id lookup writeback.
  - Run targeted and full test suites.

Implementation Notes
- Primary target files:
  - `unfold_modal/static/unfold_modal/js/related_modal.js`
  - `unfold_modal/static/unfold_modal/js/cms_host.js` (if forwarding payload/source checks need adjustment)
  - `unfold_modal/static/unfold_modal/js/popup_iframe.js` (if lookup payload needs enrichment)
- Ensure behavior works for:
  - Top-level CMS-hosted lookup (source field in CMS iframe admin form)
  - Nested lookup from inside an Unfold modal iframe (source field in previous modal iframe)
- Preserve security checks (same-origin validation) while avoiding brittle source matching.

Scope
- Lookup selection roundtrip in CMS host mode.
- Regression tests and documentation note.

Non-goals
- No changes to modal visuals.
- No protocol redesign beyond what is needed for lookup reliability.

Deliverables
- Stable raw_id lookup writeback in CMS-hosted flows.
- Regression coverage for CMS lookup selection value propagation.
- Brief README/docs note in CMS section if behavior assumptions changed.

Acceptance Criteria
- Selecting a lookup row in CMS-hosted flow updates the correct raw-id input value.
- Works for both top-level and nested modal contexts.
- No regressions in existing add/change/delete popup dismiss flows.

Tests to run
- `pytest -q`
- `pytest --browser chromium -k cms`
