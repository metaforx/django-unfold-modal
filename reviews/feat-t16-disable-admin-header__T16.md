# Review Notes - feat/t16-disable-admin-header (T16)

## Summary of T16 Changes

Added `UNFOLD_MODAL_DISABLE_HEADER` setting to optionally hide the Unfold admin header inside modal iframes, providing a cleaner UX.

### New Setting

```python
# Hide admin header inside modal iframes (default: True)
UNFOLD_MODAL_DISABLE_HEADER = True
```

### Implementation Details

1. **Setting in apps.py**: Added to `default_settings` dict with default `True`

2. **Config endpoint**: Exposed as `disableHeader` in the JSON config served at `/unfold-modal/config.js`

3. **JavaScript logic**: On iframe load, if `disableHeader` is true:
   - Find `#header-inner` element in iframe
   - Hide its parent `.border-b` container (the header)
   - Add `1rem` top padding to `#main` to compensate

4. **Selector used**: `#header-inner.closest('.border-b')` - targets the Unfold header reliably

### Files Changed

| File | Change |
|------|--------|
| `apps.py` | Add default setting |
| `views.py` | Expose in config endpoint |
| `modal_core.js` | Parse and expose `disableHeader` |
| `related_modal.js` | Hide header on iframe load |
| `README.md` | Document new setting |
| `test_modal_config.py` | Config API tests |
| `test_ui_header_suppression.py` | Playwright UI tests |

### Playwright Tests Added

- `test_admin_header_hidden_in_modal_iframe` - Verifies header is hidden
- `test_main_content_has_top_padding_when_header_hidden` - Verifies spacing
- `test_header_visible_on_parent_page` - Parent page unaffected
- `test_nested_modal_also_hides_header` - Nested modals also work

## Verification

```bash
$ pytest -q
# 96 passed (90 existing + 6 new)
```

## Status: Done
