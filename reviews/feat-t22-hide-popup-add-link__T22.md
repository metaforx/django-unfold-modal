# Review: feat/t22-hide-popup-add-link — T22 (Hide Add Link In Popups)

**Status: DONE**
**Codex Result: No issues found.**

## Summary

Adds `UNFOLD_MODAL_SHOW_ADD_IN_POPUP` setting (default: `True`) to suppress the header "Add" button in popup/modal-iframe contexts. Template-only change; no JS.

## Changes

| File | Change |
|---|---|
| `unfold_modal/apps.py` | Added `UNFOLD_MODAL_SHOW_ADD_IN_POPUP = True` to `default_settings` |
| `unfold_modal/templatetags/unfold_modal_tags.py` | Added `unfold_modal_show_add_in_popup` simple tag |
| `unfold_modal/templates/unfold/helpers/add_link.html` | New override: wraps add link in `{% if not is_popup or show_add_in_popup %}` |

## Behaviour

- Default (`True`): no change from previous behaviour — add link shows in all contexts.
- Set to `False`: add link is hidden when `is_popup` is truthy (popup or modal iframe). Outside popups, link always shows.
- Related-widget "+" buttons are unaffected (they come from widget templates, not `add_link.html`).

## Codex Review

**Round 1**: No issues found.
