# Review Notes - feat/t15-unused-code-cleanup (T15)

## Summary of T15 Changes

Removed unused code and settings that were never wired in or referenced:

### Removed Files
- **`django_unfold_modal/static/django_unfold_modal/css/related_modal.css`**
  - Contained loading spinner for iframe
  - Never referenced in templates, settings, or utils
  - All necessary styles are already injected via `modal_core.js`

- **`django_unfold_modal/templatetags/unfold_modal.py`**
  - Provided `unfold_modal_enabled` template tag
  - Never used in any template
  - Entire `templatetags/` directory removed

### Removed Settings
- **`UNFOLD_MODAL_ENABLED`**
  - Removed from `apps.py` default_settings
  - Removed from `README.md` documentation
  - Removed from test settings and assertions
  - This setting never controlled any functionality - modal is enabled by adding scripts to `UNFOLD["SCRIPTS"]`

## Verification

```bash
$ rg -n "related_modal\.css" django_unfold_modal/
# No matches (file removed)

$ ls django_unfold_modal/templatetags
# No such directory

$ rg "UNFOLD_MODAL_ENABLED" django_unfold_modal/
# No matches

$ pytest -q
# 91 passed
```

## Rationale

1. **CSS file**: The JS already injects all modal styles via `injectStyles()`. Having a separate CSS file that's never loaded adds confusion.

2. **Template tag**: The `unfold_modal_enabled` tag was never called from any template. Modal enablement is handled via UNFOLD's SCRIPTS setting.

3. **ENABLED setting**: Doesn't actually enable/disable anything. The modal works when scripts are loaded, period.

## Status: Done
