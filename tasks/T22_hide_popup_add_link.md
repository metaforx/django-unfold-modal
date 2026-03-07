# Task T22 - Hide Add Link In Popups

Goal
- Add a setting to suppress the "Add" action in popup contexts (classic admin popup or modal iframe) so users cannot create a new object of the same type from within a popup.
- Prefer minimal code changes, likely a template-only tweak.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Implementation Notes
- Keep changes minimal and avoid JS; aim for a template condition if possible.
- Add a new setting in `unfold_modal.apps.UnfoldModalConfig.default_settings`, defaulting to preserving current behavior (show the add link).
  - Proposed name: `UNFOLD_MODAL_SHOW_ADD_IN_POPUP = True`.
- Update the Unfold change form header add link to respect the setting when `is_popup` is true.
  - The button currently comes from `django-unfold/src/unfold/templates/unfold/helpers/add_link.html` via `change_form.html` `nav-global-side`.
  - Only suppress the classic header add link when `is_popup` is true; do not touch related-widget add buttons.
- Plumb the setting into templates (context processor, template tag, or direct setting access) so templates can check the flag.
- Document the setting in README or docs.

Scope
- Only affects the header "Add" button in popup contexts.
- Preserve behavior outside of popups.

Non-goals
- Do not disable related-widget add buttons (the "+" next to FK/M2M fields).
- Do not change permissions logic for add/change/delete.

Deliverables
- New setting with default + documentation.
- Template change to hide the add link when `is_popup` and the setting is `False`.

Acceptance Criteria
- With `UNFOLD_MODAL_SHOW_ADD_IN_POPUP = False`, popups (including modal iframes) do not show the header add button.
- With the setting `True` or unset, behavior matches today.
- Related-widget add buttons remain unchanged.

Tests to run
- `pytest -q`
- `pytest --browser chromium`
