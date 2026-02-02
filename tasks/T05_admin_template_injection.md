# Task T05 - Admin Template Injection

Goal
- Ensure related_modal.js loads on all admin pages (including popups) via minimal template override.

Scope
- Add `django_unfold_modal/templates/admin/base_site.html` that extends Unfold's admin/base_site and injects a script include in extrahead.
- Gate loading by UNFOLD_MODAL_ENABLED setting.

Note
- This task is superseded by T06 using Unfold `SCRIPTS` injection (no base_site override needed).

Non-goals
- Do not modify Unfold templates or static files directly.

Deliverables
- Template override that adds `<script src=".../related_modal.js" defer>`.

Acceptance Criteria
- Admin pages load related_modal.js when app is installed.
- Popups (iframe content) also load the JS.

Tests to run
- `pytest -q`
