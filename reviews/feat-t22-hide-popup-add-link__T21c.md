# Review: feat/t22-hide-popup-add-link — T21c (JS Syntax Modernization)

**Status: DONE**
**Codex Result: No issues found.**

## Summary

Replaced all `var` declarations in `cms_host.js` with `const`/`let` to match `modal_core.js` style. Syntax-only; zero behavior change.

## Changes

| Declaration | Count | Rationale |
|---|---|---|
| `var` -> `const` | 8 | Never reassigned |
| `var` -> `let` | 3 | `originIframeWindow`, `popupUrl`, `topPopupUrl` (reassigned) |

No `var` remaining in `cms_host.js`. 104 tests pass.

## Codex Review

**Round 1**: No issues found.
