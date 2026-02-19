# Review Notes - feat/t14a-modal-refactor-followup (T14a)

## Codex CLI Review

Reviewer: codex (gpt-5.2-codex)

### Run 1: One issue found

> [P2] Add fallback cleanup when transitionend doesn't fire — related_modal.js:278-286
> The close path now relies solely on a `transitionend` event to call
> `cleanupAfterClose()`. If transitions are disabled (e.g., `prefers-reduced-motion`
> styles), this handler never fires.

**Fix applied:** Added fallback timeout (200ms) with `cleanupDone` guard to ensure
cleanup runs even if transitionend doesn't fire.

### Run 2: One issue found

> [P3] Re-enable hover backgrounds for modal buttons — modal_core.js:234-238
> The new CSS hover rules won't take effect because the buttons have inline
> `background: none`, which overrides stylesheet rules.

**Fix applied:** Added `!important` to light mode hover CSS rule.

### Run 3: One issue found

> [P3] Restore dark-mode hover override for inline styles — modal_core.js:259-263
> The dark-mode hover rule also needs `!important` to override inline styles.

**Fix applied:** Added `!important` to dark mode hover CSS rule.

### Run 4: No issues found

> I did not identify any discrete issues introduced by this change set that would
> break existing behavior or tests within this repository.

## Summary of T14a Changes

- **Added MSG constants** for postMessage types (`django:modal:open`, etc.)
- **Added ICONS constants** for SVG icons (maximize, restore, close)
- **Added URL/popup helpers** (`ensurePopupParam`, `getPopupName`)
- **Replaced JS hover handlers with CSS** (`:hover` rules with `!important`)
- **Replaced setTimeout with transitionend** for close cleanup (with fallback)
- **Simplified initialization** to single `initWhenReady()` function
- **Removed `window.unfoldModal` legacy export** (tests updated to use `UnfoldModal`)
- **Updated `popup_iframe.js`** to use MSG constant with fallback

## Status: Done
