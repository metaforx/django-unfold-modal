# Review Notes - feat/t12-modal-resize (T12)

## Codex CLI Review

Reviewer: codex (gpt-5.2-codex)

### Run 1: One issue found

> [P1] Guard reverse() when app URLs aren't included — utils.py:31-34
> `get_modal_scripts()` now unconditionally calls `reverse(...)`. If a project
> upgrades and keeps the previous setup without including `django_unfold_modal.urls`,
> Django will raise `NoReverseMatch` while rendering admin pages.

**Fix applied:** Added try/except with fallback to None... but this creates another issue.

### Run 2: One issue found

> [P2] Filter out missing config script URL — utils.py:49-52
> When `_get_config_url` returns `None`, Unfold's template renders `<script src="">`
> which makes the browser request the current admin page as JavaScript.

**Fix applied:** Split into two functions:
- `get_modal_scripts()` - returns only static scripts (safe without URL config)
- `get_modal_scripts_with_config()` - includes config.js (requires URL include)

### Run 3: No issues found

> The changes add configurable modal sizing and resize behavior with a dedicated
> config endpoint and script ordering; the implementation is consistent with
> existing patterns and does not introduce functional regressions.

## Status: Done
