# Review Notes - feat/t14c-remove-important-css (T14c)

## Codex CLI Review

Reviewer: codex (gpt-5.2-codex)

### Run 1: One issue found

> [P2] Preserve theme CSS variables for modal colors — modal_core.js:242-255
> Hardcoding the button and hover colors means themed deployments will see
> fixed gray shades regardless of configured variables.

**Fix applied:** Restored CSS variables (e.g., `var(--unfold-hover-bg, #f3f4f6)`)
in all injected CSS rules while keeping backgrounds out of inline styles.

### Run 2: No issues found

> The changes only adjust icon markup and move button styling from inline styles
> to injected CSS without altering modal behavior. No regressions or functional
> issues were found in the modified code.

## Summary of T14c Changes

- **Removed `!important`** from all CSS hover rules
- **Moved button backgrounds to CSS** (not inline) so hover naturally overrides
- **Preserved CSS variables** for theme customization (`--unfold-*` variables)
- **Replaced SVG icons with Material Symbols** matching Unfold's pattern:
  - `open_in_full` for maximize
  - `close_fullscreen` for restore
  - `close` for close button
- **Removed inline styles from buttons** (only class assignment needed)

## Verification

```bash
$ rg "!important" django_unfold_modal/
# Only comment mentions it, no actual usage
```

## Status: Done
