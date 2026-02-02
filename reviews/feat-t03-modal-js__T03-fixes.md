# Review Instructions - feat/t03-modal-js Fixes (T03)

Branch: feat/t03-modal-js  
Task: tasks/T03_modal_js.md (follow-up fixes)

Scope
- Modal lifecycle race fix (avoid clearing state for a newly opened modal).
- postMessage validation (source and/or origin checks).
- Preserve and restore existing body scroll styles when locking/unlocking.

Scope Guard (must flag)
- Any changes outside `django_unfold_modal/static/django_unfold_modal/js/related_modal.js`.
- Any new UI behavior or layout changes beyond the fixes listed above.

Checklist
- `closeModal()` only clears state if it is still the active modal instance.
- `handlePopupMessage()` validates message `event.source` (and origin if used) against the active iframe.
- `lockScroll()`/`unlockScroll()` restore prior `body` styles.
- Existing behavior (modal open/close, ESC, iframe `_popup=1`, Django events) remains unchanged.

Commands
- poetry run pytest -q
