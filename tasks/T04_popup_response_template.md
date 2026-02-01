# Task T04 - popup_response Template Override

Goal
- Override Django's popup_response to postMessage the result to the parent modal while preserving fallback for window.opener.

Scope
- Add `django_unfold_modal/templates/admin/popup_response.html`.
- If `window.opener` exists, keep Django default behavior.
- Otherwise, use `window.parent.postMessage` with a structured payload containing:
  - action
  - value / new_value
  - obj / new_obj
  - to_field (if present)

Non-goals
- Do not modify Django's backend logic for PopupResponse.

Deliverables
- Template override with script that posts message and closes modal.

Acceptance Criteria
- Add/change/delete in iframe returns a postMessage payload and modal closes in parent.
- Existing popup window flow still works.

Tests to run
- `pytest -q`

