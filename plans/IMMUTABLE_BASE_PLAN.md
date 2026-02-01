# Immutable Base Plan - django-unfold-modal

Goal
- Provide a reusable Django app package named django-unfold-modal that replaces all admin related-object popups with an Unfold-styled modal (iframe-based for v1), while preserving Django's existing permissions and widget behaviors.

Audience
- This plan is a strict guide for coding agents. It must be followed as written unless the human reviewer approves a change.

Must-follow Instructions (agent workflow)
- Implement only what is explicitly allowed in this plan and task tickets.
- No monkeypatching, no runtime patching, no edits to Django or Unfold internals.
- Minimal template overrides only (see Integration Surface).
- Create test infrastructure first. Tests are the contract.
- Run local tests for each task and commit only after tests pass.
- Use feature branches named feat/<short-name> and Conventional Commits.
- Keep changes small, reviewable, and in scope; raise a plan issue if a new requirement appears.

Do
- Use Django best practices and Unfold patterns for static assets and templates.
- Use iframe strategy for v1 and design a clean seam for future fetch-inject and drawer variants.
- Reuse existing Django/Unfold functions where possible (dismissAddRelatedObjectPopup, dismissChangeRelatedObjectPopup, dismissRelatedLookupPopup).
- Prefer event-based integration (django:show-related, django:lookup-related).
- Ensure permissions, CSRF, and existing admin behaviors remain unchanged.

Don't
- Do not override or patch Unfold's admin JS files.
- Do not override more templates than listed in Integration Surface.
- Do not add third-party JS libraries beyond what Unfold already ships.
- Do not change unrelated admin UI/UX or styles.

Decisions (with challenge)
- Modal content loading: iframe for v1. Rationale: lowest risk, preserves admin forms/media/validation, minimal CSRF issues, least template disruption. Fetch-inject is deferred to v2 because it requires robust script/media execution and is more fragile with admin inline JS.
- Architecture seam: implement a ModalAdapter interface (or similar) so iframe is the default, and a future fetch-inject adapter can be added without changing event hooks.
- Drawer UI: not implemented in v1. Add a configuration hook (setting or data-attribute) that allows a drawer variant later without changing core logic.

Integration Surface (allowed)
- Templates (only these overrides):
  - admin/base_site.html (extend Unfold base_site; add JS include in extrahead)
  - admin/popup_response.html (replace opener calls with postMessage + fallback)
- Static assets:
  - django_unfold_modal/static/django_unfold_modal/js/related_modal.js (new)
  - Optional minimal CSS in django_unfold_modal/static/django_unfold_modal/css/related_modal.css (only if needed)
- Settings:
  - UNFOLD_MODAL_ENABLED (default True)
  - UNFOLD_MODAL_VARIANT = "iframe" (reserved for future "fetch")
  - UNFOLD_MODAL_PRESENTATION = "modal" (reserved for future "drawer")

Compatibility Matrix
- Django 5.x
- Unfold 0.52.0
- Widgets:
  - ForeignKey select
  - ManyToMany select
  - OneToOne select
  - raw_id_fields lookup
  - autocomplete_fields (Select2)
- Contexts:
  - inline form related fields (not inline add forms themselves)

Non-goals
- No inline formset add/remove UI changes.
- No admin redesign beyond the modal itself.
- No custom frontend frameworks or libraries.
- No changes to Django core templates beyond Integration Surface.

Architecture Summary
- Provide a Django app package with:
  - AppConfig that registers static assets and exposes settings defaults.
  - A minimal admin/base_site.html override to load JS globally.
  - A popup_response.html override to postMessage payload to parent.
  - JS module that intercepts related-object events and renders a modal iframe.
- Data flow:
  1) User clicks related widget action.
  2) JS intercepts django:show-related or django:lookup-related, prevents default, and opens modal iframe.
  3) iframe loads add/change/delete/view or lookup page with _popup=1.
  4) On success, popup_response.html posts payload to parent.
  5) Parent receives message and calls dismissAdd/Change/Delete/Lookup to update the widget.

UX Requirements
- Modal overlay with Unfold styling.
- ESC closes modal.
- Modal body scrolls; background does not scroll.
- Prevent page jump when locking body scroll (compensate for scrollbar width).

Acceptance Criteria (testable)
- Clicking add/change/view/delete/lookup for related objects opens modal, not a popup window.
- Successful save in modal closes it and updates the correct parent widget value.
- Validation errors remain inside modal and do not close it.
- Permission behavior matches stock Django admin (no regressions).
- raw_id_fields lookup returns selection to parent field correctly.
- autocomplete_fields update correctly with new or changed object labels.
- All pytest and Playwright tests pass locally.

Test Matrix
- Pytest (Django):
  - Permissions: add/change/view/delete visibility and access.
  - Popup behavior: add form served with is_popup=1 when requested.
  - popup_response payload includes correct ids/labels for add/change/delete.
  - CSRF enforced for form POST.
- Playwright (UI):
  - Add related from normal select updates parent field.
  - Change related updates label in select2 autocomplete.
  - raw_id lookup selection updates field.
  - Validation errors remain in modal.
  - Inline form related field add works inside inline form.

Definition of Done
- All tasks complete and reviewed.
- Tests green (pytest, Playwright).
- Conventional Commit created on feature branch after successful tests.
- Documentation for installation and usage added.

