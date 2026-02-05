# Review Notes - feat/t13-modal-ux (T13)

## Codex CLI Review

Reviewer: codex (gpt-5.2-codex)

### Run 1: Two issues found

> [P2] Preserve user-resized dimensions when restoring — related_modal.js:446-455
> When resize is enabled, a user can manually resize the modal before clicking maximize.
> `originalDimensions` is captured only once at open, so after a maximize/restore cycle
> the modal snaps back to the initial config size instead of the user's last resized size.

**Fix applied:** Capture current dimensions right before maximizing (`preMaximizeDimensions`)
instead of using `originalDimensions` captured at modal open time.

> [P2] Clean up resize tracking listeners on close — related_modal.js:504-512
> `setupResizeTracking` registers a document-level `mouseup` listener and a `ResizeObserver`
> per modal, but there is no cleanup in `closeModal`. Repeatedly opening and closing modals
> will accumulate observers and mouseup handlers.

**Fix applied:** Return cleanup function from `setupResizeTracking` that disconnects
ResizeObserver and removes mouseup listener. Store on modal object and call in `closeModal`.

### Run 2: No issues found

> Reviewed the updated modal logic and associated tests; the changes are internally
> consistent and do not introduce clear functional regressions.

## Status: Done
