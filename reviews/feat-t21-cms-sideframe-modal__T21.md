# Review: feat/t21-cms-sideframe-modal — T21

**Status: DONE**

## Scope
Fix modal opening when admin runs inside a non-modal iframe (e.g. Django CMS sideframe).

## Root Cause
`isInIframe` used broad `window.parent !== window` check, treating all iframes as modal-iframes. In CMS sideframe, parent is CMS frontend (not modal host), so postMessage was silently dropped and modal never opened.

## Fix
Replace broad iframe check with `window.frameElement.classList.contains('unfold-modal-iframe')` in both `modal_core.js` and `popup_iframe.js`. Wrapped in try/catch for cross-origin safety.

## Codex CLI Result
No issues found.

## Test Result
99 passed, 7 warnings (pytest -q + playwright chromium)
2 new tests: TestIframeHostModal (sideframe modal open + nested modal flow)
