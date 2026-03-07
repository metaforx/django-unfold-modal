# Review: feat/t22-hide-popup-add-link — T22a (Fix Popup Add Link Override)

**Status: DONE**
**Codex Result: No issues found.**

## Problem

T22's template override in `unfold_modal/templates/unfold/helpers/add_link.html` was ignored because `unfold` comes before `unfold_modal` in `INSTALLED_APPS`. Django resolves templates by app order.

## Fix

Moved the conditional into `django-unfold` directly:

| File | Change |
|---|---|
| `django-unfold/.../unfold.py` | Added `show_add_in_popup` simple tag reading `UNFOLD_MODAL_SHOW_ADD_IN_POPUP` from `django.conf.settings` (default `True`) |
| `django-unfold/.../add_link.html` | Wraps add link in `{% if not is_popup or _show_add_in_popup %}` |
| `unfold_modal/templates/unfold/helpers/add_link.html` | Deleted (shadowed override no longer needed) |
| `unfold_modal/templatetags/unfold_modal_tags.py` | Removed unused `unfold_modal_show_add_in_popup` tag |

Works regardless of `INSTALLED_APPS` order. 104 tests pass.

## Codex Review

**Round 1**: No issues found.
