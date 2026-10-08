# Task T24a - View-Related Link Ownership

Status
- Folded into T24 (2026-10-02). Option A approved by the maintainer: unfold-modal owns the view link everywhere in own-all mode. Implement and test it as part of T24; this file stays as the background and acceptance reference.

Context
- Follow-up to T24 (open point "View-related link"). T24 takes ownership of `.related-widget-wrapper-link[data-popup="yes"]` and `.related-lookup` only.
- The view-related link (`#view_id_<name>`, class `view-related`) is different from add / change / delete:
  - It has no `data-popup="yes"`, and its URL carries only `_to_field` (no `_popup=1`).
  - Django's `RelatedObjectLookups.js` does not trigger `django:show-related` for it. Clicking it is a plain navigation to the change view in the same window.
  - unfold-modal has never handled it, and no test covers it (`view_id_` / `view-related` do not appear in `tests/`).
- Behaviour today, by Unfold version:
  - Unfold <0.107, top-level page: the browser leaves the form and opens the related object's page. Unsaved form data is lost.
  - Unfold <0.107, inside an unfold-modal iframe: the iframe navigates to the non-popup change view (full admin chrome inside the modal, no popup response on save).
  - Unfold >=0.107: Unfold's native handler matches `a.related-widget-wrapper-link` without checking `data-popup`, adds `_popup=1` and opens the link in its native modal. This happens on the top-level page and inside an unfold-modal iframe.
- The last case mixes ownership within one chain: a native Unfold modal opens inside an unfold-modal modal. T24 requires that this never happens.

Goal
- Decide who owns the view-related link, implement the decision, and cover it with tests, so that no native Unfold modal opens inside an unfold-modal chain.

Suggested Skill / Model
- Use `$unfold-dev-advanced` (Opus) for the decision and the dismiss-path check.
- Use `$unfold-dev-structured` (Sonnet) for implementation and tests.
- Review with `$unfold-codex-reviewer`.

Options
- Option A (recommended): unfold-modal owns the view link everywhere
  - Add `.related-widget-wrapper-link.view-related` to the adapter's selectors; open it in the unfold-modal stack with `_popup=1`, like change-related.
  - One owner in every context and on every Unfold version; the user no longer loses the form when viewing a related object.
  - Behaviour change on Unfold <0.107, where the link currently navigates. Needs a CHANGELOG "Changed" entry.
- Option B: split ownership
  - Top-level page: leave the link to Unfold (native modal on >=0.107, navigation before).
  - Inside an unfold-modal iframe or CMS-hosted modal: intercept and forward to the unfold-modal stack.
  - No behaviour change on the top-level page, but two different modals for the same widget depending on context.
- Option C: leave untouched
  - Not acceptable on its own: it keeps the native modal inside the unfold-modal chain on >=0.107.
- The choice changes user-visible behaviour, so it needs human approval before implementation.

Worker Plan (required)
- Worker 1: Analysis (Opus)
  - Confirm when the view link renders (permissions: view without change, and for a superuser) on Django's and Unfold's widget templates, old and new.
  - Reproduce the three behaviours listed in Context on Unfold 0.107.0 and on the Unfold version the Python 3.11 leg resolves.
  - Check what a view-only popup does on close: a read-only change view has no save, so the modal must close through the close button / ESC without a dismiss payload, and the parent widget must stay unchanged.
  - Check the nested case: a view modal opened from inside a modal restores the previous modal on close.
  - Record the chosen option in the review and get approval.
- Worker 2: Implementation (Sonnet)
  - Extend the T24 adapter; do not add modal UI. Keep `related_modal.js` changes minimal.
  - Add `_popup=1` when forwarding, since the link's URL does not carry it.
  - Links without `href` (nothing selected) stay inert.
- Worker 3: Tests and docs (Sonnet)
  - Add the test cases below; update README and CHANGELOG.

Implementation Notes
- The test app needs a way to render the view link: a staff user with view but not change permission on the related model, or whatever Worker 1 finds is required.
- Use the related-widget test helper from T24 (`click_related(..., "view", name)`); the link sits in the dropdown on Unfold >=0.86.
- Detect the native modal by behaviour or DOM (`iframe.related-modal-frame` in `#modal-content`), not by version string.

Scope
- View-related link handling in the adapter, tests, docs.

Non-goals
- No changes to add / change / delete / lookup handling from T24.
- No new settings.
- No modification of Unfold or Django templates or JS.
- No redesign of the modal stack.

Deliverables
- Adapter update implementing the approved option.
- Tests for the view link on the top-level page and inside a modal.
- README: view action listed under the supported related actions (if Option A or B).
- CHANGELOG (Unreleased): "Changed" entry describing the new view-link behaviour.

Acceptance Criteria
- Clicking the view link inside an unfold-modal modal never opens Unfold's native modal, on any Unfold version in the lock.
- With Option A: clicking the view link on the top-level page opens exactly one unfold-modal modal, the form underneath keeps its unsaved values, and closing the modal leaves the widget unchanged.
- With Option B: top-level behaviour is unchanged from Unfold's own; the in-modal case opens in the unfold-modal stack.
- Nested: closing a view modal restores the previous modal.
- A view link without a selected value does nothing.
- Full suite passes on Python 3.10, 3.11 and 3.12.

Tests to run
- `uv run pytest --ignore-glob='tests/test_ui_*.py' -rs`
- `uv run pytest tests/test_ui_*.py --browser chromium -rs`
- Repeat both with `--python 3.10` and `--python 3.11`.
