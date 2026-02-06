# Review Notes - feat/t14d-dark-mode-tokens (T14d)

## Summary of T14d Changes

- **Replaced fake `--unfold-*` CSS variables** with hardcoded colors matching Unfold's actual token values
- **Moved modal backgrounds/colors to CSS** (not inline) so dark mode can properly override
- **Updated injectStyles()** to define both light and dark mode rules for all modal elements
- **Removed obsolete variable definitions** from related_modal.css
- **Added Playwright dark mode test suite** with 5 tests validating styling

## Color Token Mapping

| Element | Light Mode | Dark Mode (Unfold Token) |
|---------|------------|--------------------------|
| Container bg | #fff | rgb(24,24,27) base-900 |
| Header border | rgb(229,231,235) | rgb(63,63,70) base-700 |
| Title color | rgb(55,65,81) | rgb(244,244,245) base-100 |
| Button color | rgb(107,114,128) base-500 | rgb(161,161,170) base-400 |
| Button hover | rgb(243,244,246) base-100 | rgb(39,39,42) base-800 |
| Iframe bg | #fff | rgb(24,24,27) base-900 |

## Playwright Tests Added

- `test_dark_mode_container_background` - Verifies dark background in dark mode
- `test_dark_mode_header_border` - Verifies dark border color in dark mode
- `test_dark_mode_title_color` - Verifies light text color in dark mode
- `test_dark_mode_button_hover` - Verifies button colors in dark mode
- `test_light_mode_baseline` - Sanity check for light mode styling

## Key Technical Decisions

1. **Hardcoded colors over CSS variable fallbacks**: The `rgb(var(--color-base-900, 24 24 27))` syntax doesn't work correctly - when the variable is undefined, `rgb(24 24 27)` is invalid CSS. Using hardcoded values ensures consistent behavior with or without Unfold.

2. **Inline styles removed for themeable properties**: Background, color, and border-color are now set via CSS so dark mode selectors can override them without needing `!important`.

3. **Loading spinner retained in CSS file**: The related_modal.css file now only contains the iframe loading spinner with its animated SVG, plus dark mode background color override.

## Verification

```bash
$ rg "\-\-unfold-" django_unfold_modal/
# No matches - all fake variables removed

$ rg "!important" django_unfold_modal/
# Only comment mentions it, no actual usage

$ pytest -q
# 91 passed
```

## Status: Done
