# Review Notes - feat/t13c-modal-ux-final (T13c)

## Codex CLI Review

Reviewer: codex (gpt-5.2-codex)

### Run 1: One issue found

> [P2] Preserve max bounds when ResizeObserver is unavailable — related_modal.js:203-206
> When `resizeEnabled` is true you always set `max-width`/`max-height` to `none`, but
> `setupResizeTracking` only enforces viewport bounds if `ResizeObserver` exists.
> In browsers without `ResizeObserver`, this removes the only size cap.

**Fix applied:** Only set max-width/max-height to 'none' when BOTH resize is enabled
AND ResizeObserver is available. Fall back to preset limits in older browsers.

### Run 2: No issues found

> The changes consistently implement the new resize behavior and header layout
> without introducing functional regressions in the modal logic. No discrete
> correctness issues were identified in the modified code.

## Status: Done
