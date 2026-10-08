# Review: feat/unfold-modal-overwrite — T24

## Status

- **Scope delivered:** adapter (`unfold_related_adapter.js`) and ownership logic,
  `UNFOLD_MODAL_OVERRIDE_NATIVE` setting, view-related link support, popup response in its
  own script (`popup_response.js`) with a working real-popup path, shared Playwright helper
  and full UI test migration, native-modal ownership regression suite, real django-filer
  picker tests, dependency range `django-unfold>=0.52.0,<0.109`, `.github/dependabot.yml`,
  README and CHANGELOG updates.
- **Final test counts per environment** (2026-10-08, lock as merged; unit =
  `pytest --ignore-glob='tests/test_ui_*.py'`, UI = `pytest tests/test_ui_*.py --browser chromium`):
  - Python 3.12.9, django-unfold 0.108.0: unit 67 passed; UI 91 passed, 1 skipped.
  - Python 3.11.1, django-unfold 0.91.0: unit 67 passed; UI 90 passed, 2 skipped.
  - Python 3.10.17, django-unfold 0.81.0: unit 67 passed; UI 90 passed, 2 skipped.
  - Skips are the native-modal tests on Unfold without native modals, and the mirror-image
    test on Unfold with them. `uv lock --check` passes.
- **Open / unverified items:** the GitHub workflow and Dependabot config have not run yet;
  real Django CMS (only the test app's simulated host pages were exercised); related links
  in dynamically added inline rows on Unfold >=0.86; Unfold 0.92–0.107 are not in the lock
  (0.107.0 passed the same suite on 2026-10-08 before the lock moved to 0.108.0); Filer's
  own edit / "New Folder" / cancel flows inside the modal, which need django-unfold-extra's
  Filer integration; Unfold-native limitations in coexist mode that are Unfold's own
  behaviour (nested native flow does not update the outer field; native view-link save does
  not update the label); the `FilerFolderField` + Unfold `ModelAdmin` `empty_label`
  incompatibility, worked around in the test app only.
- **Codex review: done.** `gpt-6.1-sol`, reasoning effort low, diff `development...c06e35b`
  without `uv.lock` (2026-10-08): "No issues found." An earlier pass on 2026-10-02 covered
  the state before the changes listed below, with the same result.
- **Follow-ups:** try a Dependabot strategy that proposes raising the `django-unfold` cap
  (`widen` / `increase`) in a throwaway PR; version bump and changelog date at release.

## Changes during maintainer review (2026-10-08)

The work was committed by the maintainer in reviewed steps. These changes were made during
that review and supersede the worker notes below where they differ:

- `var` replaced with `const` / `let` in all package JavaScript.
- The popup response logic moved out of `admin/popup_response.html` into
  `unfold_modal/static/unfold_modal/js/popup_response.js`. The template only loads it and
  passes the payload and the admin's own script URL as data attributes.
- Comments shortened: a few lines at most in package code, one line in tests.
- `polymorphic` removed from the test app's `INSTALLED_APPS`; Filer works without it.
- The simulated Filer markup test was replaced by real django-filer tests
  (`tests/test_ui_filer.py`).
- Cap raised from `<0.108` to `<0.109`; the lock for Python 3.12 moved from django-unfold
  0.107.0 to 0.108.0 after the full suite passed on it.
- Dependabot keeps `versioning-strategy: lockfile-only`: it stays inside the declared ranges,
  so the Unfold cap is raised by hand.
- README: shorter native-modal section, a paragraph on when Unfold's native modal is enough,
  and the configuration block reduced to the settings that have an effect.

## Worker notes (2026-10-02)

The sections below are the workers' notes as written. Version numbers, test counts and
descriptions of the popup response there reflect the state at that time.

Working tree after this step: `pyproject.toml` (range), `uv.lock` (forked), this note.
No package JS, tests, README or CHANGELOG touched. All probe files were removed.

Legend for every claim below: **[run]** = verified by running a Playwright probe or a
command; **[read]** = inferred from reading installed source, not executed.

## Summary

- The task file's background is confirmed by reproduction: on Unfold 0.107.0 every related
  action opens Unfold's native modal, on the top-level page and inside an unfold-modal
  iframe, and `django:show-related` / `django:lookup-related` never fire.
- It is worse than "the wrong modal opens": the native modal cannot complete with this
  package installed. Our `popup_response.html` replaces the marker Unfold looks for, so
  after save the native modal stays open on "Popup closing…" and nothing is written back.
- A `window` capture-phase click adapter that re-triggers Django's jQuery events fixes all
  flows with **zero changes to `related_modal.js`**. A prototype passed add / change /
  delete / lookup / autocomplete / M2M / nested (3 levels) / CMS host / sideframe on
  0.107.0, 0.91.0 and 0.81.0, registered both before and after Unfold's listener.
- Three points differ from the task file (details in "Open points"): modified clicks must
  **not** be ignored; `uv lock` alone does not move the lock; there is no Filer test suite
  in this repo.
- One extra defect found outside the adapter: the `window.opener` fallback in
  `popup_response.html` is broken on 0.107.0. Needs a decision.

## Lock resolution per Python

`uv lock` after the range change was a no-op: 0.67.0 still satisfied `<0.108`, so the lock
kept it for all Pythons (only the specifier line changed). The fork appears with
`uv lock --upgrade-package django-unfold` **[run]**:

```
Updated django-unfold v0.67.0 -> v0.81.0, v0.91.0, v0.107.0
```

| Python (env used) | django-unfold | Django | Related widget | Native modal |
|---|---|---|---|---|
| 3.12 (3.12.9) | 0.107.0 | 5.2.10 | dropdown | yes |
| 3.11 (3.11.1) | 0.91.0 | 5.2.10 | dropdown | no |
| 3.10 (3.10.17) | 0.81.0 | 5.2.10 | inline links | no |

- `resolution-markers` in `uv.lock`: `>= '3.12'`, `== '3.11.*'`, `< '3.11'`. **[run]**
- `uv lock --check` passes. **[run]**
- Only `django-unfold` moved; Django stays 5.2.10 for all three, nothing else was upgraded.
- Unit tests (`--ignore-glob='tests/test_ui_*.py'`): 49 passed on each of the three
  environments. **[run]**
- `requires-python >=3.10` and `django>=5.0` are unchanged and need no change. Note for
  docs: Unfold 0.107.0 itself declares `Requires-Python >=3.12` and `django>=5.2`
  **[read: dist-info METADATA]**.

## Reproduction results

Environment: Chromium, test app, superuser. "ours" = `.unfold-modal-overlay`,
"native" = `iframe.related-modal-frame` in `#modal-content` with Alpine `openModal === true`.
Events were recorded with a jQuery listener on `document`.

### Unfold 0.107.0 without adapter (current package) **[run]**

| Action | Context | Modal | `django:*` event fired |
|---|---|---|---|
| add (FK select, autocomplete, M2M, inline FK) | top-level | native | no |
| change | top-level | native | no |
| delete | top-level | native | no |
| view | top-level | native (Unfold adds `_popup=1`) | no (never has) |
| raw_id lookup | top-level | native | no |
| add / change | inside unfold-modal iframe | native, **inside the iframe** (parent stack stays 1) | no |
| view | inside unfold-modal iframe | native, inside the iframe | no |
| raw_id lookup | inside unfold-modal iframe | native, inside the iframe | no |
| add | CMS modal with host (`/cms-modal-host/`) | native, inside the CMS iframe | no |
| add | plain sideframe (`/iframe-host/`) | native, inside the sideframe | no |

- Click trace: listeners on `document` registered after Unfold's (capture) and Django's
  delegated `body` handler never see the click; only listeners registered before Unfold's
  on `document` capture do. This matches `stopImmediatePropagation()` at `document` capture.
- Native modal + this package is a dead end: add category in the native modal, save →
  iframe shows "Popup closing…", `openModal` stays `true`, select unchanged. Cause: Unfold
  closes its modal when the iframe document contains `#django-admin-popup-response-constants`;
  our template only creates that element in the `window.opener` branch, and the
  `postMessage` it sends instead is dropped by `handleParentMessage` (no active modal).
- Delete link for `City.country` is not rendered in the popup (Django hides it for the
  CASCADE FK); not an Unfold change.

### Unfold 0.107.0 with prototype adapter **[run]**

| Action | Context | Modal | Event |
|---|---|---|---|
| add / change / delete | top-level | ours (1 overlay, stack 1), no native | `django:show-related` once |
| raw_id lookup | top-level | ours | `django:lookup-related` once |
| view | top-level | native (not in adapter scope → T24a) | none |
| add / change | inside unfold-modal iframe | ours (stack 2), no native in any frame | once, in the iframe |
| raw_id lookup | inside unfold-modal iframe | ours (stack 2) | once, in the iframe |
| view | inside unfold-modal iframe | native inside the iframe (→ T24a) | none |
| add, lookup | CMS modal with host | ours, in the host document; 0 overlays in CMS iframe | once |
| add | plain sideframe | ours, inside the sideframe | once |

End-to-end with write-back, all passing: add (option selected, change link href updated),
change (label updated), delete (option removed, change link loses `href`), raw_id lookup
(value written once), autocomplete add and change (Select2 label), M2M add
(`#id_tags_to`), inline FK add opens, nested Event → Venue → City → Country saved back up
level by level with exactly one visible overlay and no native modal at each step, CMS host
add + lookup, ESC close.

### Listener order **[run]**

- Adapter registered at document start (before every page script): works.
- Adapter registered ~50 ms after `window` `load`, i.e. **after** Unfold's
  `openPopupInModal()` listener: same result, full basic + nested flows pass.
- `preventDefault()` + `stopPropagation()` is sufficient; `stopImmediatePropagation()` is
  not needed. Unfold's handler never ran in either registration order.
- A probe that registered the adapter 400 ms after load and clicked before that got the
  native modal. So the adapter must register synchronously at script execution, not behind
  `DOMContentLoaded`, `load` or the `django.jQuery` poll.

### Unfold 0.91.0 (Python 3.11) and 0.81.0 (Python 3.10) **[run]**

| | without adapter | with adapter |
|---|---|---|
| add / change / delete / lookup, top-level and nested | ours, event once (Django's handler) | ours, event once (adapter); Django's `body` handler does not run |
| overlays / stack after one click | 1 / 1 | 1 / 1 — no double open |
| nested 3-level chain, CMS host, sideframe, autocomplete, M2M | pass | pass |
| view link | plain navigation away from the form | unchanged |
| Meta / Shift / Alt + click on add link | opens ours (Django's handler ignores modifiers) | opens ours |
| `window.open` fallback + `opener` dismiss | works | n/a |

What an adapter must not do there: let the click continue after forwarding. Django's own
handler would fire the event a second time. With `stopPropagation()` at `window` capture
this cannot happen on any version, so no Unfold-version or DOM detection is needed.

## Dismiss path

- `popup_response.html` postMessage → `handleParentMessage` → `callDismissFunction` →
  Django `dismiss*Popup`: **not affected** on 0.107.0 once our modal is the one that
  opened. add / change / delete write back correctly. **[run]**
- Nested: `handleForwardedDismiss` in the previous iframe works on 0.107.0 (3-level chain).
  **[run]**
- CMS host: `cms_host.js` forwarding works on 0.107.0 (add + lookup). **[run]**
- `updateRelatedObjectLinks`: Unfold ships its own `admin/js/admin/RelatedObjectLookups.js`
  (it shadows Django's because `unfold` precedes `django.contrib.admin`). Since 0.86-era it
  finds the links through the teleported `<nav>` (`data-id` on the wrapper). After add the
  change link gets the new pk, after delete it loses `href`. **[run]** on 0.107.0 / 0.91.0.
- Pre-existing, all three versions: Unfold's `dismissRelatedLookupPopup` does not trigger
  `change` on the field (Django's does). 0 `change` events after lookup. **[run]**
  Not caused by 0.107; out of scope, but do not assert on a `change` event in tests.
- **Broken on 0.107.0: the `window.opener` fallback.** Unfold 0.107.0 adds its own
  `admin/js/popup_response.js` (absent in 0.91.0 **[read]**) that calls
  `window.parent.dismiss*` instead of `opener.dismiss*`. Our template's `window.opener`
  branch loads `{% static "admin/js/popup_response.js" %}`, which now resolves to that file.
  In a real popup window `window.parent === window`, so:
  `window.parent.dismissAddRelatedObjectPopup is not a function`, popup stays on
  "Popup closing…", nothing written back. **[run]** (opened with Django's
  `showRelatedObjectPopup`, saved). Works on 0.91.0 and 0.81.0 **[run]**.
  Reachable when anything opens a real popup: the adapter's fallback when
  `related_modal.js` has not initialised yet, or third-party code calling `window.open`.
  Fix is small and inside the allowed surface (call `opener.dismiss*` directly in that
  branch instead of loading the static file) — see "Needs human approval".

## Lookup handler conflict

Inside an unfold-modal iframe showing a changelist, clicking a row link
(`a[data-popup-opener]`) runs up to three handlers:

1. jQuery handler bound directly on the link by `RelatedObjectLookups.js`.
   - 0.81.0 / 0.91.0: calls `opener.dismissRelatedLookupPopup(...)`; `opener` is `null` →
     uncaught `Cannot read properties of null (reading 'dismissRelatedLookupPopup')`.
     **[run]** This exists today, with or without the adapter.
   - 0.107.0: Unfold commented that call out; only `preventDefault()`. No error. **[read]**
2. `popup_iframe.js` handler on `document.body` (bubble) → `django:popup:lookup`.
3. 0.107.0 only: Unfold's handler on `document` (bubble). It strips `lookup_` from
   `window.name` (ours is `id_publisher__1`), finds no such element in the parent, sets the
   parent's `openModal = false` (harmless), then throws
   `Cannot read properties of null (reading 'classList')`. **[run]**

Result today on every version: the value is written exactly once by our path (setter trap
on the input recorded one write, top-level and nested), the modal closes, and one uncaught
error is logged — a different one per version. No double write.

Minimal neutralisation, verified **[run]** on 0.107.0 and 0.91.0 (top-level, nested and
CMS lookup; value written once, zero page errors): in `popup_iframe.js` register the
`a[data-popup-opener]` handler on `document` in **capture** phase and call
`preventDefault()` + `stopPropagation()`, exactly like the Filer handler below it. That
stops both the jQuery handler (1) and Unfold's (3). The `DOMContentLoaded` wrapper is then
unnecessary. Only adding `stopPropagation()` to the existing `body` bubble handler would
silence (3) but not the pre-existing error (1), so a "no console error" regression test
would still fail on Python 3.10 / 3.11.

## Filer / autocomplete

- Autocomplete (Select2): add and change through the adapter update the rendered label on
  all three versions; no errors. **[run]**
- Filer: **not installed in the test app and not in the dependency groups; there is no
  Filer test in `tests/`.** Nothing could be run. From django-filer 3.6.0 source
  (wheel unpacked outside the repo) **[read]**:
  - File / folder widgets open through `a.related-lookup` links (`#<id>_lookup`,
    `#<id>_change`, folder `lookup_name`). On 0.107.0 Unfold's selector matches them, so
    they would open the native modal today. The adapter's `.related-lookup` scope covers
    them; no Filer-specific selector is needed.
  - Selection links are `.js-dismiss-popup` without `related-lookup`,
    `related-widget-wrapper-link` or `data-popup-opener`. Neither Unfold handler matches
    them, so the capture handler in `popup_iframe.js` should be unaffected.
  - Must be verified by hand or in a project that has Filer (see "Could not verify").

## Header suppression

- `#header-inner` exists in the popup page on 0.107.0, 0.91.0 and 0.81.0 with the same
  nesting (`#header-inner` → container div → header div), so `HEADER_CONTAINER_DEPTH = 2`
  still lands on the header element. **[run]** + **[read: `unfold/helpers/header.html`]**
- With `UNFOLD_MODAL_DISABLE_HEADER = True`: header container `display: none`,
  `#main` `padding-top: 1rem`, parent page header still visible, on all three. **[run]**
- `tests/test_ui_header_suppression.py` on 0.107.0 (through a temporary click shim, see
  "Notes for test migration"): 5 passed, **0 skipped**. The three conditional skips do not
  trigger on any locked version.
- 0.105 redesign: the header add button (`a.addlink`) is no longer present on the popup add
  form on 0.107.0 (present on 0.91.0 / 0.81.0). **[run]** No existing test selects it.
- `UNFOLD_MODAL_SHOW_ADD_IN_POPUP`: only defined in `apps.py` `default_settings`. No
  template or tag in the package reads it (the `add_link.html` override described in the
  T22 review is not in the tree), and upstream `add_link.html` has no check. The setting
  has no effect on any version. **[read]** Out of scope; noted as the task asks.

## Other selector changes (0.107.0)

- Related links: dropdown as described in the task. Ids and classes unchanged. The change
  link's class attribute starts with a space (`" related-widget-wrapper-link change-related"`);
  harmless for CSS selectors.
- Link hrefs on 0.107.0 already contain `_popup=1` for add / change / delete; the view link
  has only `_to_field`.
- Toggle: `[x-ref="relatedWidgetWrapper<name>"]`, `<name>` is the full field name
  (`category`, `chapters-0-editor`). **[run]**
- The dropdown stays open after a link click, while the modal is open and after it closes
  (0.91.0 and 0.107.0). A second "click toggle" would close it. **[run]**
- ESC with the modal open closes the modal on every version. Menu state afterwards
  differs: still open on 0.91.0 without adapter, closed with the adapter (0.91.0 and
  0.107.0). Focus
  after ESC is `<body>` on dropdown versions and the link on 0.81.0. There is no focus
  restoration to assert on with the dropdown. **[run]**
- A disabled change link (no selection) has no `href`; it is rendered (214×30) but
  Playwright's actionability check reports it "not visible" on 0.107.0. With the adapter a
  scripted click on it is inert: no modal, no navigation, no error. **[run]** Natively
  Unfold would call `new URL("")` on it.
- Save / delete buttons (`button[name="_save"]`, `button[type="submit"]`), `.select2-*`,
  `#id_tags_to`, `#lookup_id_publisher`, `a[data-popup-opener]`: unchanged. **[run]**
- raw_id lookup link is not in a dropdown on any version; it is clicked directly.

## Recommended adapter design

New file `unfold_modal/static/unfold_modal/js/unfold_related_adapter.js`. Prototype that
passed every probe above (instrumentation removed):

```js
'use strict';
(function() {
    var SHOW = '.related-widget-wrapper-link[data-popup="yes"]';
    var LOOKUP = '.related-lookup';

    function onClick(event) {
        if (event.button !== 0) return;
        var target = event.target;
        if (!target || typeof target.closest !== 'function') return;
        var link = target.closest(SHOW + ', ' + LOOKUP);
        if (!link) return;
        var $ = window.django && window.django.jQuery;
        if (!$) return;                      // no Django admin JS: leave untouched

        var isLookup = link.matches(LOOKUP);
        event.preventDefault();
        event.stopPropagation();

        if (!isLookup && !link.href) return; // disabled link, same as Django

        var relatedEvent = isLookup
            ? $.Event('django:lookup-related')
            : $.Event('django:show-related', { href: link.href });
        $(link).trigger(relatedEvent);
        if (!relatedEvent.isDefaultPrevented()) {
            var fallback = isLookup
                ? window.showRelatedObjectLookupPopup
                : window.showRelatedObjectPopup;
            if (typeof fallback === 'function') fallback(link);
        }
    }

    window.addEventListener('click', onClick, true);
})();
```

- **Hand-over: trigger the jQuery event on the link**, exactly as Django's handler does.
  The delegated handlers in `init()` (`$('body').on('django:show-related', selector, …)`)
  receive it with `event.currentTarget === link`, so `handleShowRelated`,
  `handleLookupRelated` and both `…InIframe` variants work unchanged. The top-level vs
  delegate-to-parent decision stays in `init()`. **No change to `related_modal.js`,
  `modal_core.js` or `cms_host.js`.** Calling the handlers directly would mean exporting
  four functions and duplicating the `delegateToParent` decision.
- **Selector scope:** `.related-widget-wrapper-link[data-popup="yes"]` and
  `.related-lookup` — the same two selectors `init()` binds, nothing wider. The view link
  (no `data-popup`) falls through untouched (→ T24a adds it here). Filer needs no extra
  selector.
- **Double-handling guard:** structural. The click is stopped at `window` capture on every
  Unfold version, so Django's delegated `body` handler and Unfold's `document` handler
  never see it; the adapter is the only trigger. No version check, no DOM sniffing, no
  flag. Verified on 0.81.0 and 0.91.0: one event, one overlay. Add an idempotence guard
  (e.g. a flag on `window.UnfoldModal`) so a script list included twice does not register
  two listeners.
- **Fallback mirrors Django:** if nothing prevented the event (handlers not bound yet),
  call Django's `showRelatedObjectPopup` / `showRelatedObjectLookupPopup`. This keeps
  <0.107 behaviour identical to today. On 0.107.0 that popup cannot dismiss (see "Dismiss
  path") unless the template fix is approved.
- **`href` / disabled links:** read `link.href` at click time, so
  `updateRelatedObjectLinks` (Unfold's override, driven by the select's `change`) stays the
  single source for change / delete URLs. No `href` → `preventDefault()` +
  `stopPropagation()` and nothing else, the same outcome as Django's `if (this.href)`.
  Stopping it also keeps Unfold 0.107.0 from throwing on `new URL("")`.
- **Do not filter modifier keys.** See "Open points". Only `event.button !== 0` is checked
  (middle click fires `auxclick`, not `click`, so it is unaffected anyway).
- **Register synchronously** at script execution. Look up `django.jQuery` at click time,
  not at load time.
- **Contexts and registration:** add the file to `get_modal_scripts()` and
  `get_modal_scripts_with_config()` in `unfold_modal/utils.py` (position does not matter;
  put it after `related_modal.js`). `UNFOLD["SCRIPTS"]` is rendered on admin pages and
  popup pages, which covers the top-level page, unfold-modal iframes, the CMS admin iframe
  and sideframes — all verified. **Do not** add it to `get_cms_modal_head_html()`: the CMS
  host page has no related links and no `django.jQuery`; clicks happen in the admin iframe's
  document. `tests/test_cms_head.py` and `tests/test_package.py` may assert on the script
  lists — check them when adding the file.
- **`popup_iframe.js`:** move the `a[data-popup-opener]` handler to `document` capture with
  `preventDefault()` + `stopPropagation()` (see "Lookup handler conflict"). Keep it inside
  the existing `isInModalIframe` guard.

## Notes for test migration (Worker 3)

- To see what fails for reasons other than the dropdown, the existing UI files were run on
  0.107.0 through a temporary out-of-repo pytest plugin that injected the prototype adapter
  + lookup fix and opened the dropdown before `page.click("#add_id_…")` /
  `locator.click()`. This was a shimmed probe (8 s default timeout, 3.5 min total), not the
  bare suite. **[run]** Result: **48 passed, 16 failed, 0 skipped** of 64.
  - All 16 failures are the same thing: an explicit
    `locator("#add_id_<name>").wait_for(state="visible")` used as a "form is ready" signal
    before the click (9× `#add_id_country` in `test_ui_nested_modal.py`, 1× in
    `test_ui_modal_ux.py`, 3× `#sideframe … #add_id_category`, 3× `#cms-iframe …
    #add_id_category`). The link is attached but hidden until the menu opens.
  - `test_ui_modal.py` (13), `test_ui_dark_mode.py` (5), `test_ui_modal_size.py` (4),
    `test_ui_header_suppression.py` (5) passed completely. No colour-token, sizing, header
    or Select2 differences on 0.107.0.
- Helper requirements that follow from the probes:
  - Decide by visibility of the link, not by version. Open the toggle only if the link is
    not visible — the menu stays open after the first use, so toggling blindly closes it.
  - Replace "wait for `#add_id_*` visible" readiness checks with a wait on the toggle
    (`[x-ref="relatedWidgetWrapper<name>"]`) or on the link being attached, falling back to
    the link being visible on Unfold <0.86.
  - Works on `Page`, `Frame` and `FrameLocator`; the toggle and the link are both reachable
    by id / `x-ref` from the frame root (the `<nav>` is teleported to that frame's `<body>`).
  - Disabled links (no `href`) fail Playwright's visibility check on 0.107.0; a test for
    "disabled link is inert" needs `evaluate("el => el.click()")` or `dispatch_event`.
- Regression test file:
  - Native-modal detection across frames: `#modal-content iframe.related-modal-frame`
    evaluated in every `page.frames` entry; on <0.107 it is simply never present, so the
    ownership assertions can run on all versions without a skip.
  - raw_id "no console error": only valid once the `popup_iframe.js` capture change is in;
    before it, 0.81.0 / 0.91.0 log the `opener` error and 0.107.0 logs the `classList` error.
  - Do not assert on a `change` event after raw_id lookup (Unfold never fires it).
  - Focus restoration: nothing to assert on dropdown versions (focus ends on `<body>`).
  - Modifier clicks: `Control`+click on macOS is a context-menu click and produces no
    `click` event; use `Meta` / `Shift` / `Alt` if this is tested.
  - Unrelated link: sidebar links are hidden at the default viewport; use a visible link
    (e.g. breadcrumb / `a[href^='/admin/']:visible`).
- The delete link is absent for CASCADE FKs (`City.country`); use `Book.category` for
  delete flows.
- Run UI runs one at a time; never two in parallel.

## Open points / decisions

1. **View-related link** — moved to T24a, not handled. Observations only **[run]**:
   - Rendered for a superuser next to the change link on 0.81.0, 0.91.0 and 0.107.0.
   - 0.81.0 / 0.91.0 top-level: plain navigation to `/category/<pk>/change/?_to_field=id`,
     the form is left.
   - 0.107.0 top-level: Unfold's native modal, with or without the adapter.
   - 0.107.0 inside an unfold-modal iframe: native modal inside the iframe, with or without
     the adapter. This is the one remaining case where a native modal appears inside our
     chain after T24. A T24 regression test asserting "no native modal anywhere" must not
     click the view link.
2. **Python / Django minimums** — keep `requires-python >=3.10`; the forked lock covers the
   three legs. No reason to raise it.
3. **Modified clicks — differs from the task file.** The Implementation Notes say to ignore
   ctrl / meta / shift clicks. Probes show that is wrong for this package:
   - Today (0.81.0 / 0.91.0) a Meta / Shift / Alt click opens the unfold-modal modal,
     because Django's handler does not look at modifiers.
   - On 0.107.0 an adapter that ignores modified clicks hands them to Unfold, which also
     does not look at modifiers: the native modal opens (and then cannot dismiss).
   - Recommendation: do not special-case modifiers. Behaviour is then identical on all
     versions and identical to today.
4. **Lock command** — `uv lock` alone leaves 0.67.0 in place. Dependabot / Worker 4 docs
   should use `uv lock --upgrade-package django-unfold`.
5. **Filer suite** — the task lists "existing suites for … Filer … pass unchanged". There is
   none in this repository.

## Needs human approval

- **`popup_response.html` `window.opener` branch on Unfold 0.107.0.** Broken as described
  under "Dismiss path". Options: (a) fix in this task by calling `opener.dismiss*` directly
  in that branch — small, within the allowed template, but outside the "adapter" scope of
  T24; (b) leave it and document that real popup windows do not complete on Unfold ≥0.107.
  Recommendation: (a).
- **Modified clicks** (point 3 above): confirm the deviation from the task's
  Implementation Notes.
- Nothing else needs approval: no change to `requires-python`, Django minimum, settings or
  template overrides is proposed.

## Could not verify

- Filer flows on any Unfold version (not installed; source read only).
- Related links in dynamically added inline rows on Unfold ≥0.86 (teleported `<nav>` of the
  `__prefix__` template row). The initial inline row (`chapters-0-editor`) works.
- The bare existing UI suite on 0.107.0 (not run, as instructed), and the full UI suite on
  3.10 / 3.11 with the new lock (only the probes ran there).
- Unfold versions between 0.92 and 0.106 (not in the lock).
- Real django CMS; only the test app's simulated host pages.

## Worker 2 (Adapter) — implementation notes

**Status: DONE — adapter implemented exactly as the prototype above; no deviation.**

### Files changed

- `unfold_modal/static/unfold_modal/js/unfold_related_adapter.js` (new). Same selectors,
  guard order and hand-over as the prototype in "Recommended adapter design": `window`
  capture-phase `click` listener, scope `.related-widget-wrapper-link[data-popup="yes"]` +
  `.related-lookup`, only `event.button !== 0` filtered (no modifier-key special-casing, per
  Open point 3), `preventDefault()` + `stopPropagation()`, trigger `django:show-related` /
  `django:lookup-related` via `window.django.jQuery` on the link, fallback to
  `showRelatedObjectPopup` / `showRelatedObjectLookupPopup` if not default-prevented, no-op
  on links without `href` (disabled links). Idempotence guard via
  `window.UnfoldModal._relatedAdapterInstalled` (consistent with `modal_core.js`'s own
  `window.UnfoldModal = window.UnfoldModal || {}` pattern, works regardless of whether
  `modal_core.js` has executed yet). Header comment explains the Unfold ≥0.107
  `document`-capture interception this file exists to pre-empt. No modal UI, no state beyond
  the guard flag.
- `unfold_modal/static/unfold_modal/js/popup_iframe.js`: moved the `a[data-popup-opener]`
  handler from a `DOMContentLoaded` → bubble-phase `body` listener to a `document`
  capture-phase listener with `preventDefault()` + `stopPropagation()`, right next to the
  existing Filer capture handler, both still inside the pre-existing `isInModalIframe` guard
  (early `return` at the top of the IIFE). The `DOMContentLoaded` wrapper is now redundant
  and was dropped, as the review's "Lookup handler conflict" section anticipated. The Filer
  handler below it is untouched.
- `unfold_modal/utils.py`: added `unfold_related_adapter.js` to both `get_modal_scripts()`
  and `get_modal_scripts_with_config()`, positioned after `related_modal.js` and before
  `popup_iframe.js` (position does not matter functionally; kept consistent between both
  functions). `get_cms_modal_head_html()` / `_build_cms_config()` untouched — the adapter is
  not in the CMS head output.
- `tests/test_package.py`: new `TestModalScriptLists` class — two unit tests asserting the
  adapter URL is present in both `get_modal_scripts()` and `get_modal_scripts_with_config()`.
- `tests/test_cms_head.py`: one new test, `test_does_not_include_related_adapter_js`,
  asserting the adapter is absent from `get_cms_modal_head_html()`.
  `tests/test_modal_config.py` asserts only on the config endpoint's JSON content, not on any
  script list, so it needed no change.

No changes to `related_modal.js`, `modal_core.js`, `cms_host.js`, any template, README,
CHANGELOG, `pyproject.toml`, `uv.lock`, or anything in `tasks/`. The `window.opener` branch
in `popup_response.html` was not touched (still waiting on the human-approval decision above).

### Deviation from the prototype

None. The implementation is the prototype verbatim (selectors, guard order, hand-over,
fallback, disabled-link handling, no modifier-key filtering), plus the idempotence guard and
header comment the task asked for on top of it.

### Verification

- Unit tests, `pytest --ignore-glob='tests/test_ui_*.py' -q -p no:cacheprovider`:
  - venv-312 (Python 3.12.9, django-unfold 0.107.0): **52 passed** (49 pre-existing + 3 new).
  - venv-311 (Python 3.11.1, django-unfold 0.91.0): **52 passed**.
  - venv-310 (Python 3.10.17, django-unfold 0.81.0): **52 passed**.
- `ruff check --no-fix` on `unfold_modal/utils.py`, `tests/test_package.py`,
  `tests/test_cms_head.py`: **all checks passed** on all three environments (checked on
  venv-312; same ruff config applies to all). `unfold_modal/static/.../*.js` is not Python,
  so ruff does not apply to it.
- Temporary Playwright probe (`tests/test_ui_t24_probe.py`, deleted after the run): 4 tests —
  add with write-back (Category), change with label update (Author via Select2
  autocomplete), raw_id lookup (Publisher; asserted value written once and
  `errors == []` from a `pageerror` listener), one nested add inside a modal (Venue → City →
  Country, asserting exactly one visible `.unfold-modal-overlay` and no
  `#modal-content iframe.related-modal-frame` in any `page.frames` entry at every step: after
  opening the outer modal, after opening the nested modal, and after the nested save).
  `page.set_default_timeout(8000)` was used throughout.
  - venv-312 (0.107.0, dropdown + native modal): **4 passed**.
  - venv-311 (0.91.0, dropdown, no native modal): **4 passed**.
  - venv-310 (0.81.0, inline links): **4 passed**.
  - The click helper in the probe opened the dropdown toggle
    (`[x-ref="relatedWidgetWrapper<name>"]`) only when `#<action>_id_<name>` was not already
    visible, matching the task's instruction and the review's "decide by visibility, not
    version" note. No native-modal assertion needed a version check or skip — on <0.107 the
    `iframe.related-modal-frame` selector is simply never present.

### Could not verify

- Filer flows (still not installed in this repo; out of scope for this worker, matches
  Worker 1's note).
- Full existing UI suites (`tests/test_ui_*.py`) — explicitly out of scope for Worker 2;
  Worker 3 migrates them. Not run here.
- Dynamically added inline rows' related links on Unfold ≥0.86 (same gap Worker 1 flagged;
  not exercised by this worker's probe either).

## Worker 2b (Ownership setting, view link, popup response) — implementation notes

**Status: DONE — setting, view link and all three popup-response contexts implemented and
probed on 0.107.0 / 0.91.0 / 0.81.0. Uncommitted. No maintainer decision turned out to be
impossible.** Legend as above: **[run]** / **[read]**.

### Design choices

- **Flag transport: URL fragment on the adapter script.** `get_modal_scripts()` is called
  inside `settings.py`, so the setting can only be read per request, inside the callable.
  Unfold's `skeleton.html` renders `<script src="{{ script }}">` for every entry without a
  falsy check (all three versions **[read]**), so a callable cannot "add a script only when
  the setting is off" — it must always return a URL. The adapter entry is therefore one
  callable (`utils._related_adapter_script`) that returns
  `…/unfold_related_adapter.js` or `…/unfold_related_adapter.js#coexist`; the adapter reads
  `document.currentScript.src`. No extra request, no extra file, no config URL, CSP-safe
  (unlike a `data:` URL), not sent to the server (unlike a query string, which would also
  break signed static URLs). The same callable is used by `get_modal_scripts()` and
  `get_modal_scripts_with_config()`; `config.js` was not extended (it would be a second
  mechanism for the same flag). The adapter also exposes the result as
  `window.UnfoldModal.overrideNative` (boolean) for inspection/tests. If
  `document.currentScript` is unavailable (script bundled or loaded async by a project) the
  adapter falls back to own-all.
- **CMS head helper: no flag emitted, deliberately.** The CMS host page does not load the
  adapter and has no related links; it only opens modals on request from its child frames.
  The ownership decision is taken in the admin iframe, which gets its scripts (and the
  fragment) from `UNFOLD["SCRIPTS"]`. Verified with the CMS host page in coexist mode
  **[run]**. If the maintainer wants the flag in the inline CMS config anyway it is a
  one-line addition, but nothing would read it.
- **Native-modal detection: none — purely behavioural, at click time.** In coexist mode the
  adapter does not take the click at `window` capture (unless owned, below). It registers a
  second listener on `window` in the **bubble** phase that forwards any matched click that
  arrives with `defaultPrevented === false`:
  - Unfold with native modals: its `document`-capture handler calls
    `stopImmediatePropagation()`, the click never reaches the bubble listener → native modal.
  - Unfold without native modals: add / change / delete / lookup are claimed by Django's own
    `body` handler, which fires `django:show-related` / `django:lookup-related` into
    `related_modal.js` as before T24; the view link is claimed by nobody and is picked up by
    the bubble listener → unfold-modal. So the setting has no effect there.
  - No version string, no dependency on Unfold internals (`openPopupInModal`, DOM ids).
    Correct on 0.81.0, 0.91.0, 0.107.0 **[run]**; for future versions it degrades to "whoever
    claims the click first owns it, otherwise unfold-modal", never to a real popup window.
- **Owned in coexist mode** (`isOwned()` in the adapter, taken at capture phase):
  `UnfoldModal.state.isInIframe` (inside an unfold-modal iframe → a chain we started),
  `UnfoldModal.state.isInCmsModal` (admin inside a `.cms-modal` iframe, with or without the
  host scripts on the parent), or the link matches the Filer selector. A plain sideframe
  (`/iframe-host/`, not `.cms-modal`) is a normal admin page → native.
- **Filer selector: `.filerFile .related-lookup`.** From django-filer 3.6.0 **[read]**:
  the file widget (`admin_file.html`: `#<id>_lookup`, `#<id>_change`) and the folder widget
  (`admin_folder.html`: `#<lookup_name>`) both put their `a.related-lookup` links inside
  `span.filerFile`, and Filer's own `dismissRelatedImageLookupPopup` /
  `dismissRelatedFolderLookupPopup` depend on `lookup.closest('.filerFile')`, so the class is
  part of Filer's own contract rather than styling. `.js-related-lookup` exists only on the
  file widget, `.filer-dropzone` is layout.
- **View link:** selector `.related-widget-wrapper-link.view-related` added to the adapter's
  show selector and forwarded through `django:show-related`. `related_modal.js` needed one
  change: the delegated selector for `django:show-related` (was `[data-popup="yes"]` only,
  which the view link does not match) is now a constant `SHOW_RELATED_SELECTOR` used in both
  `.on()` calls. `ensurePopupParam()` and `SHOW_RELATED_PREFIX` already handled `_popup=1`
  and the `view_` id prefix. Fallback when `related_modal.js` is not bound yet: plain
  navigation (stock behaviour), not `showRelatedObjectPopup` (Django would open a non-popup
  URL in a window that cannot dismiss).
- **`popup_response.html` branching.** The inline script itself now carries Django's marker
  (`id="django-admin-popup-response-constants"`, `data-popup-response="{{ popup_response_data }}"`),
  so the element exists in every context and the payload is read from
  `document.currentScript.dataset` (no `escapejs`). Order:
  1. `window.frameElement` has class `unfold-modal-iframe` → `postMessage` (unchanged
     payloads).
  2. `window.opener` → `opener.dismissAdd/Change/DeleteRelatedObjectPopup(window, …)`, the
     same three calls as Django's `popup_response.js`; the dismiss functions close the
     window. The static file is no longer loaded in this branch.
  3. otherwise → append `{% static "admin/js/popup_response.js" %}`, i.e. exactly what runs
     without this package. In Unfold's native modal that is Unfold's own script
     (`window.parent.dismiss*`), and Unfold's iframe `load` handler finds the marker and
     closes the modal.
  Changed semantics, on purpose: previously *any* iframe got `postMessage(…, '*')`. Now only
  our own iframe does; an unknown embedding gets the admin's own flow. Every unfold-modal
  context (top-level, nested, CMS host, sideframe-local) creates `.unfold-modal-iframe`, so
  nothing of ours changes. This also keeps coexist working if Unfold renames
  `related-modal-frame`.

### Files changed

- `unfold_modal/apps.py` — `UNFOLD_MODAL_OVERRIDE_NATIVE: True` in `default_settings`.
- `unfold_modal/utils.py` — `_related_adapter_script(request)`; used in both script helpers
  in place of the static lambda.
- `unfold_modal/static/unfold_modal/js/unfold_related_adapter.js` — coexist flag, view link,
  `isOwned()`, bubble-phase listener (registered only in coexist mode), view-link fallback.
- `unfold_modal/static/unfold_modal/js/related_modal.js` — `SHOW_RELATED_SELECTOR` (see above).
- `unfold_modal/templates/admin/popup_response.html` — three branches.
- `tests/test_package.py` (+5), `tests/test_modal_config.py` (+3), `tests/test_popup.py` (+6).
- Not touched: `modal_core.js`, `cms_host.js`, `popup_iframe.js`, `views.py`,
  `get_cms_modal_head_html()`, `tests/test_cms_head.py`, `tests/test_ui_*.py`, README,
  CHANGELOG, `pyproject.toml`, `uv.lock`, `tasks/`.

### Verification

Unit tests, `pytest --ignore-glob='tests/test_ui_*.py' -q -p no:cacheprovider` **[run]**:
venv-312 **66 passed**, venv-311 **66 passed**, venv-310 **66 passed** (52 + 14 new).
`ruff check --no-fix` on the changed Python files: one finding, `I001` in
`tests/test_popup.py`, which is one of the 13 pre-existing ones (identical on `HEAD`);
repo total is still 13.

Temporary probe `tests/test_ui_t24b_probe.py` (8 s timeouts, run per environment one after
another, deleted): 0.107.0 **25 passed / 9 skipped**, 0.91.0 **21 passed / 13 skipped**,
0.81.0 **21 passed / 13 skipped**. Skips are by design (own-flow class not repeated in
coexist on 0.107, where the native class runs instead; native classes skipped on <0.107).
Every row asserted zero `pageerror` and zero popup windows unless noted. "ours" = exactly
one visible `.unfold-modal-overlay`, `UnfoldModal.stackDepth()` as expected, no
`#modal-content iframe.related-modal-frame` in any frame.

| Flow | 0.107.0 own-all | 0.107.0 coexist | 0.91.0 own-all / coexist | 0.81.0 own-all / coexist |
|---|---|---|---|---|
| `UnfoldModal.overrideNative` matches setting | pass | pass | pass / pass | pass / pass |
| add category, write-back | ours, pass | **native**, completes, write-back | ours / ours | ours / ours |
| change category, label update | ours, pass | **native**, completes | ours / ours | ours / ours |
| delete category, option removed | ours, pass | **native**, completes | ours / ours | ours / ours |
| raw_id lookup, value written | ours, pass | **native**, completes, 0 errors | ours / ours | ours / ours |
| view link top-level: `_popup=1`, form keeps unsaved title, close button and ESC leave select unchanged | ours, pass | native (Unfold's) | ours / ours | ours / ours |
| view link, save in modal → change dismiss, label updated | pass | see limitation 2 | pass / pass | pass / pass |
| view link disabled (no `href`), scripted click | inert | not probed | inert / inert | inert / inert |
| nested: add city → view country (stack 2) → close restores city modal with its unsaved values → add country → save → save | pass | — | pass / pass | pass / pass |
| nested native (add city → add country inside native iframe) | — | Unfold's own flow fails, see limitation 1 | — | — |
| CMS host, venue add: add city → add country (stack 2) → save → view country → close → save; all in host document | (Worker 2) | **ours**, pass | — | — |
| CMS host, raw_id lookup | (Worker 2) | **ours**, pass | — | — |
| simulated Filer markup (raw_id link wrapped in `span.filerFile`) | — | **ours**, completes; category add on the same page still native | — | — |
| plain sideframe (`/iframe-host/`) add | — | native inside the sideframe, completes | — | — |
| real popup window: add (both modes), change, delete — window closes, field updated | pass | pass | pass / pass | pass / pass |
| stock Unfold (unfold_modal removed from `INSTALLED_APPS`, `UNFOLD = {}`): add completes | reference: pass | | | |

### Notes for Worker 3

- **Switching the setting:** pytest-django's `settings` fixture works
  (`settings.UNFOLD_MODAL_OVERRIDE_NATIVE = False`) — the adapter URL is computed per
  request and `live_server` runs in the same process. Set it before `page.goto()`. Check
  with `page.evaluate("UnfoldModal.overrideNative")`.
- **Native present?** Behavioural check, no version string: in coexist mode click a related
  add and see whether `#modal-content iframe.related-modal-frame` becomes visible or
  `.unfold-modal-overlay` appears. (The probe used the installed version only to pick the
  test class.)
- **Coexist on 0.107 needs `page.wait_for_load_state("load")` before the click.** Unfold
  registers its handler on `window` `load`; a click before that is unclaimed and opens the
  unfold-modal modal (see limitation 3). Inside iframes (`#cms-iframe`, `#sideframe`, native
  iframe) wait for a form field plus a short pause, or for the frame's load state.
- Native modal: open = `page.locator("#modal-content iframe.related-modal-frame")` visible;
  completed = the same locator hidden (the iframe stays in the DOM). Content via
  `page.frame_locator("#modal-content iframe.related-modal-frame")`.
- Nested unfold-modal frames: `page.frame_locator(".unfold-modal-iframe").last`; close button
  of the visible modal: `.unfold-modal-overlay:visible .unfold-modal-close`. Wait on
  `page.wait_for_function("UnfoldModal.stackDepth() === N")` before asserting — "one visible
  overlay" is already true before a nested modal opens.
- View link: `#view_id_<name>` (in the dropdown on ≥0.86, same helper). It only has an
  `href` after a value is selected. A superuser gets the change form (editable), so "form
  saved → label updated" is testable; a read-only view needs a view-only staff user, which
  the test app does not have. Disabled link: `locator.evaluate("el => el.click()")`.
- Delete confirmation button: `button[type="submit"]` matches two elements on 0.107 (the
  command search has one); use `form:has(input[name="post"]) button[type="submit"]`.
- Real popup: `with page.expect_popup() as info:
  page.evaluate("showRelatedObjectPopup(document.getElementById('add_id_category'))")`,
  then `with popup.expect_event("close"): popup.click('button[name="_save"]')`.
- `City.__str__` includes the country (`"Name, Country"`); compare with `startswith`.
- CMS chain in coexist: assert `.unfold-modal-overlay` in the host page and 0 inside
  `#cms-iframe`, and no `iframe.related-modal-frame` in any `page.frames` entry.

### Limitations

1. **Nested native flow is broken in Unfold 0.107.0 itself.** Add city (native) → add
   country inside the native iframe → save: the inner modal closes, the country is saved in
   the database, but the outer form's select is not updated and
   `SelectBox is not defined` is thrown. Identical with unfold_modal removed from the project
   **[run]**. Cause **[read]**: the outer iframe's `window.name` is `add_id_city` (no `__N`),
   Unfold's `setPopupIndex()` yields `NaN`, `removePopupIndex("id_country__1")` does not strip
   the suffix, the element is not found and the M2M branch runs. Not fixable here without
   patching Unfold. In coexist mode nested native is therefore "as good as Unfold"; own-all
   is unaffected.
2. **Native view link + save (coexist, 0.107.0):** the native modal closes but the label of
   the select is not updated; identical on stock Unfold **[run]** (its `popup_response.js`
   does not strip the `view_` prefix). Own-all handles this correctly.
3. **Coexist, before `window` `load` on 0.107.0:** Unfold's handler is not registered yet, so
   a related click in that window is unclaimed and opens the unfold-modal modal (which
   completes normally). Reasoned from the listener order **[read]**, not reproduced: the
   probes always waited for `load`.
4. **Coexist, Filer widget inside a native modal iframe:** the Filer link is owned, but the
   page is neither an unfold-modal iframe nor a CMS modal, so the unfold-modal modal opens
   locally inside the native iframe's document (limited to its size). Not probed.
5. **Real popup + raw_id lookup on 0.107.0** is still broken, by Unfold: its
   `RelatedObjectLookups.js` commented out `opener.dismissRelatedLookupPopup` and its
   `app.js` handler writes to `window.parent`. This is row selection, not
   `popup_response.html`; out of scope and not reachable through this package's own flows.

### Unverified

- Filer: implemented from django-filer 3.6.0 source; only simulated markup was executed
  (a raw_id link wrapped in `span.filerFile`), not Filer's widgets, JS or dismiss functions.
- The adapter's fallback paths when `related_modal.js` has not bound its handlers
  (`showRelated*Popup`, view-link navigation) — not executed.
- `document.currentScript` being unavailable (bundled / async-loaded adapter) — reasoned only.
- Autocomplete, M2M, inline related links, and the CMS host / sideframe in **own-all** mode
  were not re-probed after the adapter restructuring (same code path as the probed add /
  change; Worker 2 probed them before it, and the existing UI suites cover them once
  Worker 3 migrates them). CMS host was re-probed in coexist mode only.
- Real django CMS; a `.cms-modal` iframe whose parent lacks the host scripts in coexist mode.
- The existing full UI suite (not run, as instructed).

## Worker 3 (Tests) — notes

**Status: DONE.** Test helper, migration of all 8 existing UI suites, and the new
regression file. No package code, README, CHANGELOG, `pyproject.toml`, `uv.lock`,
`.github`, or `tasks/` touched. Everything left uncommitted.

### Helper (`tests/ui_helpers.py`, new)

- `click_related(page_or_frame, action, name)` — clicks `#<action>_id_<name>` directly if
  visible; otherwise opens `[x-ref="relatedWidgetWrapper<name>"]` first, waits for the link,
  then clicks. Decides by visibility, never version. Never re-toggles an already-open menu.
- `wait_related_ready(page_or_frame, name, timeout=5000)` — readiness replacement for the old
  `locator("#add_id_<name>").wait_for(state="visible")`; waits for the toggle or any
  add/change/view/delete link to be attached, whichever the version renders.
- `assert_no_native_modal(page)` — asserts `#modal-content iframe.related-modal-frame` is not
  visible in any of `page.frames`.
- `assert_owns_modal(page, stack_depth=None)` — exactly one visible `.unfold-modal-overlay`,
  no native modal anywhere; optionally also checks `UnfoldModal.stackDepth()`. When
  `stack_depth` is given it first waits for the DOM overlay count to settle at that depth,
  since `closeModal()` keeps the closing overlay around (transparent) until its CSS
  transition ends — right after `stackDepth()` drops, both overlays can briefly be
  Playwright-"visible" at once.
- All four work on `Page`, `Frame`, and `FrameLocator` (uses `Locator.or_()`, Playwright
  1.58.0). `raw_id_fields` lookup links (`#lookup_id_*`) are never in the dropdown and stay
  direct everywhere, per the task.

### Migration

All 89 direct `#add_id_*` / `#change_id_*` / `#view_id_*` / `#delete_id_*` occurrences across
the 8 files listed in the task now go through the helper (counts matched the task's estimate
exactly: modal.py 11, modal_ux.py 23, nested_modal.py 29, modal_size.py 1, dark_mode.py 5,
header_suppression.py 7, iframe_host.py 4, cms_modal.py 9). One occurrence needed manual
handling: `test_ui_modal.py::TestInlineFormRelatedField` used a compound CSS selector
(`[id^="add_id_chapters-0-editor"], ...`) with an `is_visible()` presence guard; rewritten to
detect presence via toggle-or-link attachment (not visibility, which the dropdown breaks) and
then call `click_related`. `#lookup_id_publisher` raw_id links were left untouched, as
specified. No test intent or assertions changed — only how the link is reached. Added
`from tests.ui_helpers import ...` to each of the 8 files; two pre-existing `ruff` I001
import-order findings (`test_ui_dark_mode.py`, `test_ui_header_suppression.py`) were
incidentally fixed by the new import block's correct ordering.

### New tests (`tests/test_ui_native_modal_ownership.py`, new)

Behavioural only, no assertions on Unfold's listeners/source. 21 tests:

- `TestOwnership` — add/change/delete/raw_id lookup each open exactly one unfold-modal modal.
- `TestAddRelated`, `TestChangeRelated`, `TestDeleteRelated` — save/edit/delete closes the
  modal and updates the field, with an ownership assertion while the modal is open.
- `TestNestedChain` — Venue → add City → add Country → save Country → City restored and
  updated → save City → Venue updated, with `assert_owns_modal` at every step.
- `TestRawIdLookup` — value written back exactly once (setter-trap instrumentation, not just
  final-value comparison) and zero `pageerror`.
- `TestCloseAndEsc` — close button and ESC.
- `TestUnrelatedLinksNotIntercepted` — an ordinary breadcrumb link still navigates.
- `TestViewLinkOwnership` (T24a) — top-level view opens once and preserves unsaved form
  values; closing leaves the widget unchanged; a view link with no selection is inert
  (dispatched via `evaluate`, since a disabled link fails Playwright's actionability check);
  closing a nested view modal restores the previous modal with its unsaved value intact.
- `TestCoexistSetting` (`settings.UNFOLD_MODAL_OVERRIDE_NATIVE = False` via the pytest-django
  `settings` fixture) — native add completes with write-back and no unfold-modal overlay when
  a native modal is available (skips otherwise); the setting has no effect when no native
  modal exists (skips otherwise); the CMS-hosted flow stays owned by unfold-modal; simulated
  django-filer markup (`span.filerFile` wrapped around the existing raw_id lookup link via
  `page.evaluate` — no django-filer dependency or test-app model change) stays owned, while an
  ordinary related link on the same page is left to native/fallback behaviour. Real django-filer
  is not covered in this repository (tested in django-unfold-extra per the task's non-goals).
- `TestRealPopupWindow` — `showRelatedObjectPopup` via `page.evaluate` inside
  `page.expect_popup()` completes and writes back, on every Unfold version.

Native-modal (un)availability is always detected behaviourally (waiting on
`.unfold-modal-overlay` OR `#modal-content iframe.related-modal-frame` via `Locator.or_()`,
then checking which one matched) and `pytest.skip`s the mismatched branch — no version string
check anywhere in this file.

No sideframe-specific coexist test was added (not in the task's required Regression Tests
list; the Decisions section states a plain sideframe behaves like a normal admin page).

### Test-app changes

None. All fixtures (`category`, `author`, `publisher`, `country`) reuse existing
`tests/server/testapp` models.

### Results (final verification, one environment at a time)

| Environment | django-unfold | `pytest --ignore-glob='tests/test_ui_*.py'` | `pytest tests/test_ui_*.py --browser chromium` |
|---|---|---|---|
| venv-312 (Python 3.12.9) | 0.107.0 | 66 passed | 83 passed, 1 skipped |
| venv-311 (Python 3.11.1) | 0.91.0 | 66 passed | 83 passed, 1 skipped |
| venv-310 (Python 3.10.17) | 0.81.0 | 66 passed | 83 passed, 1 skipped |

The one skip differs by environment and is the expected complementary half of the coexist
pair: on venv-312 (native modal present) `test_coexist_without_native_modal_has_no_effect`
skips ("Native related modal is available on this Unfold version"); on venv-311/-310 (no
native modal) `test_coexist_native_add_completes_without_unfold_modal` skips ("Native related
modal is not available on this Unfold version"). No xfail; no suspected package bug found by
these tests.

`ruff check --no-fix tests/` is identical on all three environments: 11 findings, all
pre-existing and none in files this worker created (`ui_helpers.py`,
`test_ui_native_modal_ownership.py` are both clean). Baseline on `git HEAD` was 13; two
(`test_ui_dark_mode.py`, `test_ui_header_suppression.py` I001) were incidentally fixed by this
worker's import additions. `ruff format` was run only on the two new files.

`grep` proof: no `click("#add_id_`/`#change_id_`/`#view_id_`/`#delete_id_` or
`.locator("#...").click()` usage remains outside `tests/ui_helpers.py` anywhere in
`tests/test_ui_*.py`.

## Filer worker — notes

**Status: DONE.** Real django-filer coverage added as a TEST-only dependency.
No package code (`unfold_modal/`), README, CHANGELOG, `.github`, or `tasks/`
touched. Everything left uncommitted. Legend: **[run]** / **[read]**.

### Dependency + lock

- `pyproject.toml`: `django-filer>=3.0` added to the `test` dependency group
  (lower bound only, not in `[project].dependencies`).
- Plain `uv lock` (no upgrade flags) resolved: `django-filer==3.6.0`,
  `django-polymorphic==4.11.7`, `easy-thumbnails==2.10.1`, `pillow==12.3.0`,
  `py-svg-hush==0.3.0` added. **[run]** Verified via `git diff uv.lock` /
  programmatic extraction that `django-unfold` stays exactly 0.81.0
  (`python_full_version < '3.11'`), 0.91.0 (`== '3.11.*'`), 0.107.0
  (`>= '3.12'`), and `django` stays 5.2.10 for every fork — only Filer and its
  own dependencies were added. `uv lock --check` passes.
- All three scratchpad envs (venv-312/3.12, venv-311/3.11, venv-310/3.10)
  synced with `uv sync --frozen --python <x>` and `UV_PROJECT_ENVIRONMENT`
  pointed at the scratchpad venvs (never the repo's own `.venv`). **[run]**

### Test-app changes (`tests/server/testapp`)

- `settings.py`: `polymorphic`, `easy_thumbnails`, `filer` added to
  `INSTALLED_APPS` (filer's only hard requirements beyond Django, confirmed
  from `django_filer-3.6.0.dist-info` METADATA and `filemodels.py` imports:
  `django-polymorphic`, `easy-thumbnails`, `py-svg-hush`; no `mptt` needed —
  Folder uses a custom tree, not django-mptt). `MEDIA_ROOT` set to
  `tempfile.mkdtemp(prefix="unfold-modal-filer-")` (outside the repo, nothing
  tracked), `MEDIA_URL = "/media/"`.
- `urls.py`: added `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`
  so uploaded/created file content is servable in DEBUG.
- `models.py`: new `MediaAsset` model — `file` (`FilerFileField`), `folder`
  (`FilerFolderField`), both `null=True, blank=True, on_delete=SET_NULL`, plus
  a plain `category` FK (reused `Category`) for the coexist "ordinary related
  add on the same page" half of the task, per the task's explicit fallback
  option (rather than touching `Book`'s admin).
- `admin.py`: `MediaAssetAdmin(ModelAdmin)` registered, `fields = ["name",
  "file", "folder", "category"]`.
- Migration: `tests/server/testapp/migrations/0004_mediaasset.py`, generated
  with `manage.py makemigrations testapp` on venv-312 (the test app already
  uses real migrations, not syncdb-style creation). `manage.py
  makemigrations --check --dry-run` and `manage.py check` both clean
  afterwards. **[run]**
- `tests/server/db.sqlite3` is gitignored (`.gitignore` has a literal
  `db.sqlite3` entry) and was never touched; pytest-django uses Django's
  default in-memory sqlite test DB since `DATABASES["default"]["TEST"]` sets
  no explicit `NAME`. `git status --short` after every run shows no DB or
  media artefacts. **[run]**

### Real incompatibility found and worked around (not an unfold_modal bug)

- **Unfold's `formfield_for_foreignkey` unconditionally injects
  `empty_label` for every plain FK** (any field not in `raw_id_fields`,
  `autocomplete_fields` or `radio_fields` —
  `unfold/mixins/formfield_model_admin.py`, `FormFieldModelAdminMixin.formfield_for_foreignkey`).
  `FilerFolderField`'s custom form field (`filer/fields/folder.py`,
  `AdminFolderFormField.__init__`) bypasses `ModelChoiceField.__init__` and
  calls `forms.Field.__init__` directly, which does not accept `empty_label`
  → `TypeError: Field.__init__() got an unexpected keyword argument
  'empty_label'` on every admin page rendering a `FilerFolderField`, with or
  without `blank=True` (the injection is unconditional on field blank-ness).
  **[run]**, reproduced on venv-312/0.107.0 with the exact traceback
  recorded during this work. Confirmed by code reading this is independent
  of `unfold_modal`: stock Django admin never passes `empty_label` here, so
  plain Django + Filer would not crash; it is specifically Unfold's
  `ModelAdmin` that collides with Filer's folder widget. `FilerFileField`'s
  own form field (`AdminFileFormField`) is unaffected — it goes through
  `ModelChoiceField.__init__`, which accepts `empty_label` natively, and it
  discards any `widget` Unfold injects anyway, always rendering Filer's own
  `AdminFileWidget`.
  - **Worked around entirely in the test app**, not in `unfold_modal` or
    Unfold: `MediaAssetAdmin.formfield_overrides = {FilerFolderField:
    {"widget": None}}`. Django's `formfield_for_dbfield` merges
    `formfield_overrides` into `kwargs` before calling
    `formfield_for_foreignkey`, so by the time Unfold's (and Django's own)
    `if "widget" not in kwargs:` check runs, the key is already present and
    the whole block — including the `empty_label` injection — is skipped.
    `FilerFolderField.formfield()`/`AdminFolderFormField.__init__` always
    discard the `widget` kwarg and build their own `AdminFolderWidget`
    regardless of its value, so passing `None` is inert and the real Filer
    picker still renders. Verified end-to-end (folder picker opens, selects,
    writes back) after this change. **[run]**
  - This is reported as a finding, not fixed upstream (out of scope: not an
    `unfold_modal` bug, and Unfold/Filer internals must not be touched).
    Anyone integrating `FilerFolderField` with django-unfold hits this
    regardless of unfold-modal; the workaround pattern is a one-line
    `formfield_overrides` entry any such project would need.

### Step 1 probe (viability check)

Two throwaway probe files (deleted after the run, per instructions): one for
the file widget, one for the folder widget, both on venv-312 (Unfold
0.107.0, default own-all mode):
- File: create `filer.models.File` (root/unfiled — `FolderRoot.files` is
  always empty by design in Filer; unfiled files only show under the
  "Unsorted Uploads" virtual folder, which required one extra navigation
  click inside the iframe) → open `MediaAsset` add form → click
  `#id_file_lookup` → `unfold-modal` overlay opens (not native) → navigate
  into "Unsorted Uploads" inside the iframe → click the file's
  `a.js-dismiss-image` selection link → modal closes, `#id_file` holds the
  file pk, the widget's `.description_text` shows the label. **4/4 assertions
  passed.**
- Folder: create `filer.models.Folder` → click `#folder` (the folder widget's
  lookup anchor id is the bare field name per Filer's `AdminFolderWidget`,
  not `lookup_id_<field>`) → overlay opens → click the folder's
  `a.js-dismiss-folder` link → modal closes, `#id_folder` holds the folder
  pk. **Passed.**

Both probes passed cleanly once the `formfield_overrides` workaround was in
place; no other package-code changes were needed. Step 1 is therefore a
**pass** — proceeded to Step 2.

### Tests added/removed

- New `tests/test_ui_filer.py` (9 tests):
  - `TestOwnAllFilePicker` — pick a file writes value + label, exactly one
    `.unfold-modal-overlay`, no native modal, zero `pageerror`; close button
    and ESC leave the widget unchanged.
  - `TestOwnAllFolderPicker` — same three for the folder widget.
  - `TestCoexistFiler` (`settings.UNFOLD_MODAL_OVERRIDE_NATIVE = False`) —
    file picker and folder picker both still open in the unfold-modal modal
    and complete, unconditionally (no skip — matches the Decisions doc:
    Filer stays owned in coexist mode on every Unfold version); an ordinary
    FK (`category`) on the *same* `MediaAsset` page goes native when a
    native modal is available, skipping otherwise (behavioural detection via
    `Locator.or_()`, no version string).
  - Helper reuse: `assert_owns_modal`, `assert_no_native_modal`,
    `click_related` from `tests/ui_helpers.py`, consistent with
    `test_ui_native_modal_ownership.py`.
- Removed from `tests/test_ui_native_modal_ownership.py`:
  `TestCoexistSetting.test_coexist_simulated_filer_markup_stays_owned` (the
  `span.filerFile`-wrapped raw_id link simulation), now superseded by the
  real Filer tests above. No helper was unique to that test; `publisher` and
  other fixtures remain in use by the rest of the file.

### Results (final verification, one environment at a time)

| Environment | django-unfold | `pytest --ignore-glob='tests/test_ui_*.py'` | `pytest tests/test_ui_*.py --browser chromium` |
|---|---|---|---|
| venv-312 (Python 3.12.9) | 0.107.0 | 66 passed | 91 passed, 1 skipped |
| venv-311 (Python 3.11.1) | 0.91.0 | 66 passed | 90 passed, 2 skipped |
| venv-310 (Python 3.10.17) | 0.81.0 | 66 passed | 90 passed, 2 skipped |

- venv-312's one skip is the pre-existing coexist-without-native
  complementary skip in `test_ui_native_modal_ownership.py` (native modal
  present here, so that branch runs instead). The new
  `test_coexist_ordinary_related_add_on_same_page_goes_native` in
  `test_ui_filer.py` ran (not skipped) on venv-312 and passed, confirming the
  native path actually exercised.
- venv-311/-310's two skips: the pre-existing complementary skip plus this
  worker's new `test_coexist_ordinary_related_add_on_same_page_goes_native`,
  both skipping for the same reason ("Native related modal is not available
  on this Unfold version") — expected, since neither Unfold version has
  native related modals.
- No xfail; no unresolved package bug (the one incompatibility found is
  Unfold × Filer, not `unfold_modal`, and is worked around at the test-app
  level as described above, not papered over in any test assertion).

### `ruff` / lock / cleanliness

- `ruff check --no-fix tests/`: 9 findings, all in files this worker did not
  touch (`test_csrf.py`, `test_permissions.py`, `test_popup.py`,
  `test_smoke.py`, `test_ui_cms_modal.py`, `test_ui_dark_mode.py`,
  `test_ui_modal.py`, `test_ui_nested_modal.py`) — zero new findings. The
  count dropped from the stated baseline of 11 because fixing this worker's
  own import-order issues in `tests/server/testapp/admin.py` and
  `tests/server/testapp/settings.py` (introduced by adding the `filer`/
  `FilerFolderField` imports and `tempfile`) incidentally cleaned up isort
  ordering in those two files; no finding was suppressed or ignored.
  `tests/test_ui_filer.py` and `tests/ui_helpers.py` are both clean.
  `ruff format` was run only on `tests/test_ui_filer.py` (the only file this
  worker created).
- `uv lock --check` passes.
- `git status --short`: no media files, `__pycache__`, DB files, or other
  binary artefacts added; only the expected source/text files are modified
  or untracked.

### Deliberately not covered

- Filer's own edit button (`#<id>_change`), "New Folder", and cancel links —
  explicitly out of scope per the task (django-unfold-extra's concern; they
  finish through `window.opener`, which doesn't resolve inside the
  unfold-modal iframe, and django-unfold-extra is capped below Unfold 0.105
  so it isn't installable here anyway).
- Upload/dropzone flows (ajax upload) — not part of the related-popup
  ownership surface this package touches; not exercised.
- Filer permissions (`FILER_ENABLE_PERMISSIONS`), multi-site/owner filtering
  — the test app runs with Filer's defaults (permissions off), matching how
  the rest of the test app's admin is configured (single superuser).

### Could not verify / unverified

- Filer behaviour under any Unfold version between 0.92 and 0.106 (not in
  the lock, consistent with the rest of T24).
- Real file *content* rendering (thumbnails/previews) for image files —
  the probe/tests use a plain text file; no image-specific (easy-thumbnails
  rendering, EXIF, etc.) path was exercised, since the task only requires
  the lookup/selection flow, not Filer's image-processing pipeline.

## Worker 4 (CI, docs) — notes

**Status: DONE.** Dependabot, README, CHANGELOG and the Status block above. No package
code (`unfold_modal/`), tests, `tasks/`, or `pyproject.toml` touched, per scope. Everything
left uncommitted. Legend as above: **[run]** / **[read]**.

### Files changed

- `.github/dependabot.yml` (new) — `uv` ecosystem, weekly, modelled on
  `django-unfold-extra/.github/dependabot.yml` (`versioning-strategy: lockfile-only`,
  `open-pull-requests-limit: 5`, `chore(deps)` prefix, `dependencies` label). `allow` list:
  `django-unfold`, `django`, `django-filer`, `playwright`, `pytest-playwright` — all present
  as distinct entries in `uv.lock` **[run: grepped `uv.lock`]**. CI already runs on every
  pull request (`.github/workflows/ci.yml`), so each Dependabot PR gets the full unit +
  Playwright run across the three Python legs; no workflow change was needed for this.
- `README.md`:
  - Requirements: range `django-unfold>=0.52.0,<0.108` plus the three tested
    combinations (0.81.0/3.10, 0.91.0/3.11, 0.107.0/3.12) and a note that newer Unfold
    needs Python 3.12+ and Django 5.2+ because Unfold itself requires them.
  - Configuration: added `UNFOLD_MODAL_OVERRIDE_NATIVE = True` with a one-line comment,
    same style as the other settings.
  - New "Relationship with Unfold's Native Related Modals" section (placed before "Django
    CMS Integration"): own-all default and why, what `False` does and keeps owning, "no
    effect" on Unfold without native modals, and one sentence on coexist's native-nesting
    limitation being Unfold's own behaviour (Worker 2b "Limitations" #1, verified **[run]**
    there against stock Unfold with `unfold_modal` removed).
  - Supported Widgets: added the view-related link.
  - Added two sentences after Supported Widgets on Filer: picker support is in this
    package; edit / "New Folder" / cancel need django-unfold-extra's Filer integration
    (Filer worker's "Deliberately not covered" section). Did **not** mention the
    `FilerFolderField` + Unfold `ModelAdmin` `empty_label` incompatibility in the README,
    per the task's instruction — it stays in this review only (see Filer worker's "Real
    incompatibility found and worked around" section above).
  - Testing: switched the two commands to `uv run pytest …`.
  - Package tagline/description (`README.md` H1 subtitle and `pyproject.toml`
    `description`) left unchanged, as the task said to "consider" rather than require it.
- `CHANGELOG.rst`, `Unreleased` section: replaced the `<0.86` Compatibility entry with the
  `<0.108` range; added Features (`UNFOLD_MODAL_OVERRIDE_NATIVE`), Changed (view-link
  behaviour change), Bug Fixes (real-popup-window fix, lookup console error — stated only
  for the two Unfold versions the review verified, 0.107.0 and 0.91.0), and extended Tests
  (helper + UI migration, native-modal ownership suite, real Filer picker tests) and CI
  (Dependabot) entries; kept the existing CI (`uv`, `--ignore-glob`) and Packaging (uv
  migration) entries unchanged. Corrected the released `0.2.0b0` entry's
  `UNFOLD_MODAL_SHOW_ADD_IN_POPUP` bullet: removed the inaccurate claim that the check
  "lives in django-unfold's `add_link.html`" and replaced it with "has no effect with
  upstream django-unfold" (matches Worker 1's "Header suppression" finding: no template or
  tag in this package reads the setting, and upstream has no such check). No other
  released entry changed.
- `reviews/feat-unfold-modal-overwrite__T24.md`: added the `## Status` block directly under
  the title (summary of scope, final per-environment test counts, open/unverified items
  collected from every worker section, "Codex review: pending") and this section.

### Final verification (run in this order, one environment at a time, never two Playwright
runs in parallel, never the repo's own `.venv`)

| Environment | django-unfold | `pytest --ignore-glob='tests/test_ui_*.py' -q -rs -p no:cacheprovider` | `pytest tests/test_ui_*.py --browser chromium -q -rs -p no:cacheprovider` |
|---|---|---|---|
| venv-312 (Python 3.12.9) | 0.107.0 | 66 passed | 91 passed, 1 skipped |
| venv-311 (Python 3.11.1) | 0.91.0 | 66 passed | 90 passed, 2 skipped |
| venv-310 (Python 3.10.17) | 0.81.0 | 66 passed | 90 passed, 2 skipped |

All six runs match the previous worker's reported expectation exactly (66 / 91+1 / 90+2 /
90+2); no regression, no new failure, no new skip to triage. **[run]**

- `uv lock --check`: `Resolved 37 packages`, no changes. **[run]**
- `uv build --out-dir <scratchpad>/dist-check`: built `django_unfold_modal-0.2.2.tar.gz`
  and `django_unfold_modal-0.2.2-py3-none-any.whl`. The wheel contains
  `unfold_modal/static/unfold_modal/js/unfold_related_adapter.js` and no `tests/` path.
  **[run]**
- `CHANGELOG.rst` RST validation via `uv run --no-project --with docutils python …`
  (docutils `Parser` + `new_document`, not plain `uv run` in the repo, so the repo's
  `.venv` was not touched): at `report_level=1` (INFO and above) docutils reports ten
  "Duplicate implicit target name" notices for repeated section titles (`Features:`,
  `Tests:`, `Bug Fixes:`, `CI:`, `Other:`) across different released version sections —
  this is inherent to a changelog that reuses the same subsection headings release after
  release and is unrelated to this change (the same notices fire for titles this worker
  did not touch, e.g. line 168 `Other:` under `0.1.0`). At `report_level=2` (WARNING and
  above, docutils' own definition of "parses without warnings"), there are zero messages.
  **[run]**
- `git status --short`: only the pre-existing modified/untracked files from Workers 1–3
  plus this worker's `README.md`, `CHANGELOG.rst` and `.github/dependabot.yml`; no build
  artefacts, `dist/`, `__pycache__`, media, or venv directories. **[run]**

### Acceptance Criteria not met or not fully verified by this worker

- All Acceptance Criteria listed in the task file that depend on code/tests (ownership,
  nested chain, raw_id/autocomplete/CMS host, no new config required, script-order
  independence, coexist behaviour, view link, real-popup window, `uv lock --check`) were
  verified by Workers 1–3/Filer worker and reconfirmed here by rerunning the full suite on
  all three environments; this worker introduced no code or test changes that could affect
  them.
- Not independently re-verified by this worker (relies on earlier workers' **[run]**
  claims, not rerun): "the view-related link opens in the unfold-modal stack … on every
  Unfold version in the lock" and "a related popup opened as a real window completes on
  every Unfold version in the lock" — covered by the full suite re-run above (same tests,
  same pass counts) but not probed manually again.
- Codex review (`$unfold-codex-reviewer`) has not been run on this branch; per the task's
  Review Workflow it is still required before merge.
