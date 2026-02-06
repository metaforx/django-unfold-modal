# Task T16 - Optional Admin Header Suppression in Modal

Goal
- Make the Django/Unfold admin header inside modal iframes optional, defaulting to hidden for cleaner UX.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Approach (lean)
- Add setting: `UNFOLD_MODAL_DISABLE_HEADER = True` (default).
- Expose the setting through the existing config endpoint (`UNFOLD_MODAL_CONFIG`).
- On iframe load, if disabled:
  - Hide the admin header element inside the iframe.
  - Add top spacing to the iframe content container: `calc(var(--spacing) * 4)`.
- If the setting is `False`, keep current behavior (header visible).

Scope
- Determine a stable selector for the Unfold admin header in the iframe.
- Apply the suppression only inside modal iframes (not global admin pages).
- Add/adjust CSS to provide the spacing when header is hidden.

Non-goals
- No redesign of admin header.
- No changes to parent page header.

Deliverables
- Config setting wired and documented.
- Modal iframe header suppression implemented.
- Spacing applied when header is hidden.
- Playwright tests covering both enabled/disabled states.

Acceptance Criteria
- With `UNFOLD_MODAL_DISABLE_HEADER=True`, the iframe header is not visible and content has extra top spacing.
- With `UNFOLD_MODAL_DISABLE_HEADER=False`, the iframe header remains visible.
- `pytest -q` and `pytest --browser chromium` pass.

Tests to run
- `pytest -q`
- `pytest --browser chromium`
