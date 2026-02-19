# Review Instructions - feat/t03-modal-js (T03)

Branch: feat/t03-modal-js  
Task: tasks/T03_modal_js.md

Scope
- JS module that intercepts related-object events and opens a modal iframe.
- Minimal CSS only if required for modal behavior.
- No template/HTML changes and no drawer/fetch implementations.

Scope Guard (must flag)
- Any Python/AppConfig/README changes are out of scope for this task.
- Any non-modal UI work (drawer, fetch-inject, other admin UI changes) is out of scope.

Checklist
- `django_unfold_modal/static/django_unfold_modal/js/related_modal.js` exists and handles related-object popups via modal.
- Uses Unfold’s integration pattern: listen for `django:show-related` and `django:lookup-related` and `preventDefault()` so the default popup does not open.
- Ensures iframe URLs include `_popup=1`.
- Sets iframe `name` to match Django’s expected popup naming scheme.
- ESC closes modal; background scroll is locked; modal body scrolls.
- No jQuery dependency beyond using `django.jQuery` for the event hook (modal implementation can remain vanilla).

Commands
- poetry run pytest -q
