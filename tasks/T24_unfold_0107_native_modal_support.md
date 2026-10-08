# Task T24 - Unfold 0.107 Support: Related Widget Dropdown and Native Modal Ownership

Context
- The package is capped at `django-unfold>=0.52.0,<0.86` (see CHANGELOG, Unreleased) because the Playwright suite fails on newer Unfold. Two Unfold changes are behind this; both are handled in this task.
- Target version: django-unfold 0.107.0, the first release with native related modals. Testing against it also covers the dropdown change. Requires Python >=3.12 and Django >=5.2.

- Change 1: related widget dropdown (Unfold 0.86.0, PR #1918)
  - The related widget's add/change/view/delete links moved out of the widget row into a `more_vert` dropdown:
    - Toggle: `[x-ref="relatedWidgetWrapper<name>"]` inside `.related-widget-wrapper`.
    - Menu: `<nav id="related-widget-wrapper-<name>">`, teleported to `<body>` (`x-teleport`), hidden until the toggle is clicked.
    - The links keep their ids and classes (`#add_id_<name>`, `.related-widget-wrapper-link`, `data-popup="yes"`).
  - Measured on 0.104.1 (dropdown, no native modal; Python 3.12, Django 5.2.10):
    - Unit tests: 49 passed.
    - UI tests: 59 failed, 5 passed. The tests click `#add_id_<name>` directly and time out with "element is not visible".
    - The modal itself works: a probe that opens the dropdown first passed for add (with write-back), change (label update) and ESC close.

- Change 2: native related modals (Unfold 0.107.0)
  - `unfold/static/unfold/js/app.js` (`openPopupInModal()`) registers on `window` `load`:
    - A capture-phase `click` listener on `document` for `a.related-widget-wrapper-link, a.related-lookup`. It calls `preventDefault()` and `stopImmediatePropagation()`, then loads the popup URL in an iframe (`.related-modal-frame`) inside `#modal-content` and opens it through Alpine state on `<body>` (`openModal`).
    - A bubble-phase `click` listener on `document` for `a[data-popup-opener]` (lookup row selection inside a popup). It writes the chosen id to `window.parent.document.getElementById(...)` and closes the native modal via `Alpine.$data(window.parent.document.body)`.
  - Why this breaks unfold-modal:
    - The package does not listen for clicks. It listens for `django:show-related` / `django:lookup-related`, which Django's `RelatedObjectLookups.js` triggers from a bubble-phase click handler on `body` (`related_modal.js` `init()`).
    - Unfold's `stopImmediatePropagation()` at `document` capture stops the click before it reaches Django's handler, so those events never fire. The native modal opens and unfold-modal never sees the interaction.
    - Popup pages load `app.js` too, so the same applies inside the modal iframe (nested flows).
    - `popup_iframe.js` also handles `a[data-popup-opener]`. Inside an unfold-modal iframe both handlers run; the native one assumes the native modal's parent document.
  - Unfold's selector is wider than this package's: it also matches links without `data-popup="yes"` (the view-related link).

- Consequence: on 0.107 the existing UI tests cannot pass until the ownership adapter exists. Test helper and adapter land in the same branch.
- Python limits: Unfold >=0.82 requires Python >=3.11, >=0.92 requires Python >=3.12. Python 3.10 resolves at most 0.81.0, Python 3.11 at most 0.91.0.
- The local `django-unfold` checkout is at 0.105.0 and does not contain the native modal. Inspect the installed 0.107.0 package instead.

Decisions (approved by maintainer, 2026-10-02)
- No regression: with unfold-modal installed, every Django related popup is handled by this package by default, on every supported Unfold version. Existing users change nothing on upgrade.
- One new setting, default on, as the opt-out: `UNFOLD_MODAL_OVERRIDE_NATIVE = True`.
  - `True` (default, "own all"): unfold-modal handles add / change / delete / view / raw_id lookup everywhere. Unfold's native related modal never opens.
  - `False` ("coexist"), only meaningful on Unfold with native related modals (>=0.107):
    - Normal admin pages: Unfold's native modal handles its related popups, including nesting inside its own modal. unfold-modal does not intercept them, and Unfold's modal must be able to complete (today our `popup_response.html` override leaves it on "Popup closing…").
    - unfold-modal still owns: the whole chain when admin runs inside a Django CMS modal (CMS parent-window host), a chain it started itself (inside an unfold-modal iframe), and Filer file / folder widgets everywhere.
    - Filer (confirmed 2026-10-02): the package has supported Filer explicitly since 0.2.2 (`popup_iframe.js` forwards Filer's `.js-dismiss-popup` selection links out of the modal iframe) and keeps doing so in both modes. In coexist mode the adapter therefore keeps Filer's lookup links (`.filerFile .related-lookup`); Filer's picker cannot report back from Unfold's native modal. Filer is not installed in this repository's test app; real Filer flows are tested in django-unfold-extra.
    - On Unfold without native related modals the setting has no effect: unfold-modal owns all, as today.
- View-related link: opens in the unfold-modal stack on every Unfold version (T24a Option A, folded into this task). Behaviour change on Unfold <0.107, where it navigated away from the form.
- Real-popup fallback: the `window.opener` branch of `popup_response.html` is fixed in this release (it does not complete on Unfold 0.107, whose `popup_response.js` calls `window.parent.dismiss*`).
- Modifier-key clicks are not special-cased (review, Open points 3).

Outcome (2026-10-08)
- Delivered on `feat/unfold-modal-overwrite`; details in `reviews/feat-unfold-modal-overwrite__T24.md`.
- Range is `django-unfold>=0.52.0,<0.109`. Unfold 0.108.0 passed the full suite and replaced 0.107.0 in the lock for Python 3.12. Where this file says `<0.108` or names 0.107.0 as the tested version, read `<0.109` and 0.108.0.
- The popup response logic lives in `unfold_modal/static/unfold_modal/js/popup_response.js`; `admin/popup_response.html` only loads it (no inline script).
- Dependabot uses `versioning-strategy: lockfile-only`: it proposes updates inside the declared ranges only. A new Unfold minor is tested by raising the cap by hand.
- Follow-up: try a Dependabot strategy that proposes raising the cap (`widen` / `increase`) in a throwaway PR.

Goal
- Full test suite passes on django-unfold 0.107.0, and keeps passing on the older Unfold versions that Python 3.10 / 3.11 resolve to.
- With native related modals present, unfold-modal keeps exclusive ownership of the related-object interactions it supports: exactly one modal opens, it is the unfold-modal one, and nested, raw_id, autocomplete, CMS and Filer flows keep working.
- One new setting (`UNFOLD_MODAL_OVERRIDE_NATIVE`), no new template overrides, no dependency on script order.
- Supported range raised to `django-unfold>=0.52.0,<0.108`.

Suggested Skill / Model
- Use `$unfold-dev-advanced` (Opus) for the event-flow analysis and the adapter design.
- Use `$unfold-dev-structured` (Sonnet) for the test helper, test migration, CI and docs.
- Use `$unfold-debug-cleanup` (Sonnet) for failures that remain after helper and adapter are in.
- Review with `$unfold-codex-reviewer`.

Worker Plan (required)
- Worker 1: Analysis (Opus)
  - Change the dependency to `django-unfold>=0.52.0,<0.108`, run `uv lock`, and check what the lock resolves per Python version (expected: 0.107.0 for Python >=3.12, older Unfold for 3.10 / 3.11).
  - Reproduce on 0.107.0: which modal opens for add / change / delete / view / raw_id lookup, on the top-level page and inside a modal iframe.
  - Trace the current flow: Django click handler -> `django:show-related` / `django:lookup-related` -> `handleShowRelated` / `handleLookupRelated` (top level) or `handleShowRelatedInIframe` / `handleLookupRelatedInIframe` (iframe, CMS modal with host).
  - Confirm how the dismiss path is affected: `popup_response.html` postMessage, `handleForwardedDismiss`, Django's `dismiss*Popup` helpers, and the native `a[data-popup-opener]` handler inside our iframes.
  - Check the Filer path (`.js-dismiss-popup` capture in `popup_iframe.js`) and autocomplete (Select2) for interference.
  - Decide the open points below and record the decision in the review.
- Worker 2: Adapter (Sonnet)
  - Add the ownership adapter and wire it into the script list (see Implementation Notes).
- Worker 2b: Ownership setting, view link, popup response (Opus)
  - `UNFOLD_MODAL_OVERRIDE_NATIVE` (default `True`) in `apps.py`; the flag must reach the JS with plain `get_modal_scripts()` too (no config URL required).
  - Adapter: own-all vs coexist scope as listed under Decisions; view-related link added to the own-all scope (append `_popup=1`; a view modal closes without a dismiss payload unless the form is saved).
  - `popup_response.html`: three paths — unfold-modal iframe (postMessage, unchanged), Unfold native modal iframe (let Unfold's own flow complete), real popup window (`opener.dismiss*` called directly).
  - Unit tests for the setting and script helpers; probes on all three environments.
- Worker 3: Test helper and test migration (Sonnet)
  - Add a shared helper (e.g. `tests/ui_helpers.py`, or fixtures in `tests/conftest.py`) for related widget actions:
    - `click_related(page_or_frame, action, name)` with `action` in `add` / `change` / `view` / `delete`.
    - If `#<action>_id_<name>` is visible, click it (Unfold <0.86).
    - Otherwise click the dropdown toggle for `<name>` first, then the link (Unfold >=0.86).
    - Works on a `Page` and on a `FrameLocator`; nested tests click related links inside the modal iframe.
    - Decides by what is rendered, not by the installed Unfold version.
  - Replace the direct clicks and locators on `#add_id_*`, `#change_id_*`, `#view_id_*`, `#delete_id_*` (about 89 occurrences) in:
    - `tests/test_ui_modal.py`
    - `tests/test_ui_modal_ux.py`
    - `tests/test_ui_nested_modal.py`
    - `tests/test_ui_modal_size.py`
    - `tests/test_ui_dark_mode.py`
    - `tests/test_ui_header_suppression.py`
    - `tests/test_ui_iframe_host.py`
    - `tests/test_ui_cms_modal.py`
  - Add the regression tests (see Regression Tests).
- Worker 4: CI, docs, verification (Sonnet)
  - Dependabot, README, CHANGELOG.
  - Run the full suite on Python 3.10, 3.11 and 3.12. Triage any failure that is not a selector or ownership problem and report it.

Implementation Notes
- Interception
  - Register one `click` listener on `window` with `{ capture: true }`. `window` capture runs before `document` capture, so the result does not depend on which script loads first.
  - Scope it to the interactions the package already owns:
    - `.related-widget-wrapper-link[data-popup="yes"]`
    - `.related-lookup`
  - Ignore everything else and let it propagate untouched. Ignore non-primary buttons (`event.button !== 0`). Do not special-case modifier keys: Django's handler does not, and on 0.107 a skipped click would open the native modal (see review, Open points 3). Links Django treats as disabled (no `href`) are swallowed and do nothing.
  - For a matched click: `preventDefault()` and `stopPropagation()`, then hand over to the existing flow. `stopPropagation()` at `window` capture already keeps the event from reaching `document`; use `stopImmediatePropagation()` only if a test shows it is needed.
- Hand-over
  - Do not create modal UI in the adapter. Forward into the existing handlers, either by triggering `django:show-related` / `django:lookup-related` on the link (jQuery, as Django does) or by calling the existing handlers directly. Pick whichever keeps `related_modal.js` changes smallest.
  - The decision between top-level and delegate-to-parent handling stays in `related_modal.js` `init()`. The adapter must work in every context where the modal scripts load: admin page, modal iframe, CMS modal with host.
  - On Unfold without native modals the adapter must not open a second modal or trigger the event twice (Django's own handler still runs there). Guard this; the Python 3.10 / 3.11 legs cover it.
- Lookup selection inside the modal iframe
  - Make sure the native `a[data-popup-opener]` handler does not run, or runs harmlessly, in an unfold-modal iframe: no exception, no double write, value written back once by the existing `django:popup:lookup` path. `popup_iframe.js` may need to move its handler to capture phase and stop propagation.
- File layout
  - Keep the Unfold-specific code isolated, e.g. `unfold_modal/static/unfold_modal/js/unfold_related_adapter.js`, added to `get_modal_scripts` / `get_modal_scripts_with_config` and the CMS head helper where applicable. It only recognizes, intercepts and forwards.
- Tests
  - The dropdown `<nav>` is teleported to `<body>`, so it is not a descendant of `.related-widget-wrapper`. Locate the link by id, not relative to the wrapper.
  - The menu closes on outside click and on ESC (`x-on:keydown.escape`). Check that the ESC tests still close the modal and that an open menu does not swallow the key.
  - Inline forms use prefixed names (`<prefix>-<n>-<field>`); the helper takes the full field name.
  - Assertions that check a link's visibility or `href` need the menu opened first on Unfold >=0.86.
  - Run the Playwright runs one after another. Two parallel runs against the same test project hang.
  - The three conditional skips in `tests/test_ui_header_suppression.py` (`#header-inner` not found) exist on 0.67.0. Unfold 0.105 redesigned the admin index and the header add button; check on 0.107.0 whether the tests still skip and whether `UNFOLD_MODAL_DISABLE_HEADER` still hides the header.
- `UNFOLD_MODAL_SHOW_ADD_IN_POPUP`: upstream `unfold/helpers/add_link.html` contains no check for it, so the setting has no effect on upstream Unfold. Out of scope here; note it in the review.
- Open points (decide in Worker 1)
  - View-related link: decided, see Decisions (T24a Option A, folded into this task).
  - Python / Django minimums: keep `requires-python >=3.10` and let `uv.lock` fork per Python version unless there is a concrete reason to raise it.

Regression Tests
- New file `tests/test_ui_native_modal_ownership.py`; behavioural assertions only (no assertions on Unfold's listeners or source).
- Ownership (the explicit regression test for future Unfold changes): after clicking a supported related action, exactly one `.unfold-modal-overlay` exists and Unfold's native modal is not open (no `iframe.related-modal-frame` in `#modal-content`).
- Add related: open, save, modal closes, original field updated.
- Change related: open, edit, save, modal closes, label updated.
- Nested: main form -> add A -> add B inside A -> save B -> A restored and updated -> save A -> main form updated. Assert the unfold-modal stack is the only modal at every step and no native modal appears in the page or inside the iframe.
- raw_id lookup: selection writes the value back once; no console error from the native handler.
- Close: close button and ESC; focus restoration where it is supported today.
- Unrelated links are not intercepted (normal navigation still works).
- Existing suites for autocomplete, CMS host and header suppression pass unchanged. (There is no Filer suite in this repository; Filer is tested in django-unfold-extra.)
- Tests that depend on native modals being present skip on Unfold versions without them (detect by behaviour or DOM, not by version string where possible).
- View link (own all): top-level page and inside a modal open exactly one unfold-modal modal; the form underneath keeps unsaved values; closing leaves the widget unchanged; a view link without a selected value does nothing; closing a nested view modal restores the previous modal.
- Coexist (`UNFOLD_MODAL_OVERRIDE_NATIVE = False`), on Unfold with native modals: a related add on a normal admin page opens Unfold's native modal, no unfold-modal overlay, and completes (modal closes, field updated); inside the CMS-hosted flow the unfold-modal chain still owns everything. On Unfold without native modals the setting changes nothing.
- Real popup window: a related popup opened as a real window (`window.opener`) completes and writes back on every Unfold version.

Dependency / CI
- `django-unfold>=0.52.0,<0.108`: capped at the next untested minor, following the CHANGELOG practice.
- Old and new Unfold are covered through the existing Python matrix and the forked lock (3.10: inline links; 3.11: dropdown, no native modal; 3.12: dropdown and native modal). Do not add a version matrix.
- Add `.github/dependabot.yml` with the `uv` ecosystem, including `django-unfold` (see `django-unfold-extra/.github/dependabot.yml`). The CI workflow runs on pull requests, so each update inside the declared ranges gets the Playwright run.

Documentation
- README: Requirements line updated to the new range.
- README: short section on the relationship with Unfold's native related modals. Unfold covers the standard related-object case; unfold-modal takes ownership when installed because it provides nested modals, raw_id / autocomplete flows, CMS integration and third-party widgets. Neutral wording.
- README and `pyproject.toml` description: consider "Advanced modal workflows for Django Unfold".
- CHANGELOG (Unreleased): replace the `<0.86` Compatibility entry with the new range and the native modal coexistence; add Tests and CI entries.

Scope
- Ownership adapter and the minimal changes to existing JS needed to forward into it.
- Test helper, UI test migration, regression tests.
- Dependency range, `uv.lock`, Dependabot, docs.

Non-goals
- No fork, monkeypatch, copy or modification of Unfold JS or templates.
- No template overrides to control script order.
- No settings beyond `UNFOLD_MODAL_OVERRIDE_NATIVE`.
- No redesign of the modal stack, messaging protocol or CMS host.
- No support beyond the tested Unfold version; the cap is raised by hand (see Outcome).
- No Fobi-specific tests in this repository; verify Fobi in `unfold-fobi` after release.

Deliverables
- Isolated adapter JS, included in the script helpers.
- Shared related-widget test helper used by all UI tests.
- `tests/test_ui_native_modal_ownership.py`.
- `pyproject.toml`: `django-unfold>=0.52.0,<0.108`; updated `uv.lock`.
- `.github/dependabot.yml`.
- `UNFOLD_MODAL_OVERRIDE_NATIVE` setting, documented in README (Configuration, and the native-modal section).
- Fixed real-popup path in `popup_response.html`.
- README and CHANGELOG updates (including a "Changed" entry for the view link).

Acceptance Criteria
- Full suite passes on Python 3.12 with django-unfold 0.107.0.
- Full suite passes on Python 3.10 and 3.11 with the Unfold versions the lock resolves for them.
- On 0.107.0 a supported related action opens exactly one modal, and it is the unfold-modal one.
- Nested chain works end to end with no native modal at any step, on the top-level page and inside iframes.
- raw_id lookup, autocomplete and CMS host tests pass.
- No test clicks a related widget link without going through the helper.
- Behaviour does not depend on the order of `UNFOLD["SCRIPTS"]` relative to Unfold's own scripts.
- No new configuration is required from existing users; the default keeps unfold-modal in control of all related popups.
- With `UNFOLD_MODAL_OVERRIDE_NATIVE = False` on Unfold 0.107.0, Unfold's native modal completes on normal admin pages, and CMS-hosted and Filer flows stay with unfold-modal.
- The view-related link opens in the unfold-modal stack in own-all mode, on every Unfold version in the lock.
- A related popup opened as a real window completes on every Unfold version in the lock.
- `uv lock --check` passes.

Tests to run
- `uv run pytest --ignore-glob='tests/test_ui_*.py' -rs`
- `uv run pytest tests/test_ui_*.py --browser chromium -rs`
- `uv run pytest --browser chromium -k native_modal_ownership`
- Repeat the first two with `--python 3.10` and `--python 3.11`.
