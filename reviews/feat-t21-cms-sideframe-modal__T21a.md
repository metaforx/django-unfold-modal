# Review: feat/t21-cms-sideframe-modal — T21a

**Status: DONE**

## Scope
When Django admin runs inside a Django CMS modal iframe, render unfold modals in the CMS parent document instead of inside the admin iframe.

## Approach
Three-tier iframe context detection:
1. Unfold modal iframe (`unfold-modal-iframe` class) → forward to parent modal host
2. CMS modal iframe (`.cms-modal` ancestor) → forward to CMS parent if host loaded, else local
3. Non-CMS iframe / top-level → open modal locally

New standalone `cms_host.js` module runs in CMS parent page, manages its own modal stack, and routes dismiss messages back to the originating admin iframe.

## Key Changes
- `modal_core.js`: Added `isInCmsModal` detection via `window.frameElement.closest('.cms-modal')`
- `related_modal.js`: Capability detection (`window.parent.UnfoldModal.cmsHost`) before delegating to parent
- `cms_host.js` (new): CMS parent host module with modal stack, postMessage routing, origin validation
- `templatetags/unfold_modal_tags.py` (new): `{% unfold_modal_cms_head %}` template tag
- `utils.py`: Added `get_cms_modal_head_html()` utility
- `apps.py`: Added CMS settings (UNFOLD_CMS_MODAL_SIZE, UNFOLD_CMS_MODAL_RESIZE, UNFOLD_CMS_MODAL_DISABLE_HEADER)
- `views.py`: Config endpoint now includes `cms` sub-config
- `README.md`: Added Django CMS Integration section

## Codex CLI Review Findings (Round 1)
- P1: No postMessage origin validation in `cms_host.js` → Fixed: added `event.origin` check + `getChildIframeWindows()` sender verification
- P2: No fallback when CMS host runtime missing → Fixed: capability detection before delegating to parent

## Codex CLI Result (Round 2)
No issues found.

## Test Result
104 passed, 7 warnings (pytest -q + playwright chromium)
5 new tests: TestCmsModalHost (3) + TestCmsModalRegression (2)
