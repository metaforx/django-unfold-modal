# Review Notes - feat/t10-modal-stack (T10)

## Codex CLI Review

Reviewer: codex (gpt-5.2-codex)

### Run 1: One issue found

> [P2] Preserve popup pathname in forwarded dismiss — related_modal.js:480-485
> When a nested modal completes, `handleForwardedDismiss` builds `fakeWin` with
> an empty `location`. Django's `dismissAdd/ChangeRelatedObjectPopup` calls
> `updateRelatedSelectsOptions`, which relies on `win.location.pathname` to derive
> the model name; with an empty pathname, `modelName` becomes `undefined` and
> related select widgets won't be updated in the parent iframe.

**Fix applied:** Capture nested popup URL before closing and forward it in the
`django:modal:dismiss` message. `handleForwardedDismiss` now populates
`fakeWin.location` with the forwarded URL, matching `createFakeWindow` behavior.

### Run 2: No new issues (timed out during deep analysis)

Reviewer confirmed fix addresses the pathname issue. Additional analysis noted
only design-level observations (same-origin assumption, popup index reuse
matching Django's behavior) — no actionable bugs.

## Status: Done
