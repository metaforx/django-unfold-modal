# Task T22b - CMS Head Material Icons and Z-Index Fix

Context
- In CMS templates outside Django admin, using:
  - `{% load unfold_modal_tags %}`
  - `{% unfold_modal_cms_head %}`
  does not load Material Symbols, so modal controls render icon names (`open_in_full`, `close`) as plain text.
- In CMS parent-host mode, modal stacking also needs a higher z-index so Unfold modal UI is above Django CMS layers.

Goal
- Ensure `unfold_modal_cms_head` includes Material Symbols assets required by Unfold icons.
- Ensure modal z-index is high enough for CMS parent-host rendering.

Preferred Approach
- Keep changes minimal and centralized.
- Fix at the shared CMS head generator (`get_cms_modal_head_html`) and modal CSS variable default.

Implementation Notes
- Add Material Symbols stylesheet to CMS head output:
  - `unfold/fonts/material-symbols/styles.css` (same font source Unfold uses in admin skeleton).
- Keep output order deterministic: icon/font CSS + modal CSS before JS.
- Set/keep modal z-index default high enough for CMS layering:
  - Use `--unfold-modal-z-index: 9999999`.
- Verify stack-order safety against Django CMS layers:
  - Django CMS commonly uses 6-digit/7-digit layers (e.g., `999999`, `9999999`; debug can be `99999999`).
  - Confirm modal overlay/container renders above the active CMS modal/sideframe layer in the supported integration path.
- Add/extend tests:
  - Unit assertion that `get_cms_modal_head_html()` includes Material Symbols stylesheet.
  - Optional Playwright assertion in CMS host flow for computed z-index dominance if stable in CI.

Scope
- CMS integration output (`unfold_modal_cms_head` / `get_cms_modal_head_html`).
- Modal CSS z-index default used by overlay/container.
- Docs update for CMS template integration behavior.

Non-goals
- No redesign of modal UI.
- No changes to modal protocol/events.
- No unrelated admin theme changes.

Deliverables
- Material Symbols stylesheet included in CMS head helper output.
- Modal z-index default suitable for CMS parent-host stacking.
- Regression test coverage for CMS head output.
- Docs note that CMS integration includes icon assets and high z-index modal layering.

Acceptance Criteria
- In CMS templates using `{% unfold_modal_cms_head %}`, modal controls show actual icons (not icon text).
- In CMS parent-host mode, Unfold modal overlay/container appears above CMS stack layers in supported scenarios.
- Existing modal behavior (open/close/nested flow) remains unchanged.

Verification
- Manual: open a CMS-hosted admin iframe, trigger related modal, confirm icon glyphs render and modal is visually above CMS UI.
- Automated:
  - `pytest -q`
  - `pytest --browser chromium`

Tests to run
- `pytest -q`
- `pytest --browser chromium`
