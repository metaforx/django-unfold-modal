# Review Notes - feat/t14-related-modal-refactor (T14)

## Codex CLI Review

Reviewer: codex (gpt-5.2-codex)

### Run 1: One issue found

> [P2] Preserve responsiveness after window resizes — modal_core.js:254-270
> When `UNFOLD_MODAL_RESIZE=True`, `createModalContainer` converts the `%`/`vh`
> preset dimensions into fixed pixel values once at open time. If the user later
> resizes the browser window or rotates a device, the modal never recalculates
> and can end up larger than the viewport.

**Fix applied:** Added window resize event listener in `setupResizeTracking()` that:
- Clamps modal to viewport bounds when window shrinks
- Updates maximized modal dimensions to new bounds
- Properly cleans up the listener when modal closes

### Run 2: No issues found

> No functional regressions or correctness issues were identified in the
> reviewed changes.

## Summary of T14 Changes

- **Created `modal_core.js`** (~445 lines): Extracted state, config, utilities, and DOM creation
- **Reduced `related_modal.js`** (~600 lines, down from ~940): Now focused on modal operations and event handling
- **Fixed initial size bug**: Modal now respects preset max dimensions when resize is enabled
- **Added window resize handling**: Modal clamps to viewport when window shrinks

## Status: Done
