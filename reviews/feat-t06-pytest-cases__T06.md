# Review Notes - feat/t06-pytest-cases (T06)

Findings
- Medium: `test_add_link_visible_with_permission` can pass even if the add link is missing because it accepts `related-widget-wrapper` (wrapper exists regardless of permission). Prefer asserting the specific add link (`add_id_category` or `.related-widget-wrapper-link[data-popup="yes"]`) to make the test diagnostic.
- Low: Unused import `json`. Remove to reduce noise.

Notes
- Tests not re-run here; relying on reported `pytest -q` (34 tests).

Guardrails
- Scope is tests and test settings only. Do not change runtime app code or modal JS behavior in this task.
- No changes outside `tests/` and `tests/server/testapp/settings.py` for T06.

Implementation Guide (for a smaller model)
1) Fix add-link assertion:
   - In `tests/test_permissions.py`, update `test_add_link_visible_with_permission` to assert a concrete add link marker only (e.g., `add_id_category` or `.related-widget-wrapper-link[data-popup="yes"]`), and remove the fallback `related-widget-wrapper` check.
2) Remove unused import:
   - In `tests/test_popup.py`, delete the unused `import json`.
3) Run tests:
   - `pytest -q`
