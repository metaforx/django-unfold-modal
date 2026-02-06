# Review Notes - feat/t14e-unfold-token-alignment (T14e)

## Summary of T14e Changes

- **Replaced all hardcoded `rgb()` values** with `var(--color-base-*)` Unfold tokens
- **Added hex fallbacks** for standalone use without Unfold (e.g., `var(--color-base-900, #18181b)`)
- **Aligned all colors to Tailwind Zinc scale** (Unfold's default palette)
- **Updated dark mode tests** to handle both `rgb()` and `oklch()` color formats

## Token Mapping

| Element | Token | Hex Fallback |
|---------|-------|--------------|
| Light container bg | `--color-base-50` | `#fafafa` |
| Light header border | `--color-base-200` | `#e4e4e7` |
| Light title color | `--color-base-700` | `#3f3f46` |
| Light button color | `--color-base-500` | `#71717a` |
| Light hover bg | `--color-base-100` | `#f4f4f5` |
| Dark container bg | `--color-base-900` | `#18181b` |
| Dark header border | `--color-base-700` | `#3f3f46` |
| Dark title color | `--color-base-100` | `#f4f4f5` |
| Dark button color | `--color-base-400` | `#a1a1aa` |
| Dark hover bg | `--color-base-800` | `#27272a` |
| Dark iframe bg | `--color-base-900` | `#18181b` |

## Test Updates

Updated `test_ui_dark_mode.py` to handle both color formats:
- `rgb(r, g, b)` - standard CSS format
- `oklch(L C H)` - modern Tailwind/Unfold format

Tests now use lightness-based assertions:
- Dark colors: lightness < 0.3
- Light colors: lightness > 0.9
- Medium colors: 0.4 < lightness < 0.8

## Verification

```bash
$ rg "rgb\(" django_unfold_modal/
# No matches - all hardcoded values replaced

$ pytest -q
# 91 passed
```

## Benefits

1. **Theme compatibility**: Modal inherits Unfold's theme customizations automatically
2. **Graceful fallback**: Works standalone with sensible defaults when Unfold isn't loaded
3. **Future-proof**: Aligned with Unfold's modern OKLCH color system

## Status: Done
