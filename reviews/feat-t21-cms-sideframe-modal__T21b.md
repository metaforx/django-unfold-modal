# Review: feat/t21-cms-sideframe-modal — T21b (CMS Host Simplification)

**Status: DONE**
**Codex Result: No issues found.**

## Summary

T21b lean refactor of the CMS parent-host implementation. All T21/T21a behavior preserved; no tests altered; 104 tests pass.

## Net Change

| File | Before | After | Delta |
|---|---|---|---|
| `cms_host.js` | ~419 lines | 118 lines | -301 |
| `related_modal.js` | ~616 lines | ~625 lines | +9 |
| `utils.py` | 154 lines | 157 lines | +3 |
| `views.py` | 47 lines | 37 lines | -10 |
| `templatetags/unfold_modal_tags.py` | 55 lines | 22 lines | -33 |
| `modal_core.js` | 384 lines | 384 lines | 0 |

**Total: ~-342 lines (-20%)**

## Key Changes

- `cms_host.js` reduced to thin bridge: origin tracking + message routing only. All modal lifecycle delegated to `Modal.open`/`Modal.close` from `related_modal.js`.
- `utils.py`: added `_build_cms_config()` single source of truth for CMS config; updated `get_cms_modal_head_html()` to include `related_modal.js` in script list.
- `views.py`: uses `_build_cms_config()` instead of duplicating CMS config logic.
- `templatetags/unfold_modal_tags.py`: delegates entirely to `utils.get_cms_modal_head_html()`.
- `related_modal.js` (minimal hooks only):
  1. `!Modal.cmsHost` guard around `handleParentMessage` registration — prevents double-handler conflict on CMS parent pages.
  2. `initWhenReady` capped at 600 attempts (~30s) as safety net for non-admin pages.

## Codex Review Rounds

**Round 1**: P2 infinite polling loop in `initWhenReady`. Fixed with attempt cap.
**Round 2**: P2 double-handler if `django.jQuery` present on CMS page; P3 100-attempt cap too low for slow pages. Fixed with `!Modal.cmsHost` guard + raised cap to 600.
**Round 3**: No issues found.
