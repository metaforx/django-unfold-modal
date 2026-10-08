=========
Changelog
=========

All notable changes to django-unfold-modal are documented here.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

Unreleased
==========

Compatibility:
--------------

* Raise the ``django-unfold`` cap to 0.109 (``django-unfold>=0.52.0,<0.109``), covering the
  related widget's dropdown menu (0.86) and Unfold's own native related modals (0.107).
  unfold-modal keeps working alongside the native modals; see the ``Features`` entry below.

Features:
---------

* Add the ``UNFOLD_MODAL_OVERRIDE_NATIVE`` setting (default ``True``). ``True`` keeps
  unfold-modal handling every related popup, including on Unfold 0.107+, where Unfold would
  otherwise open its own native modal; existing projects need no change on upgrade. Set it
  to ``False`` to let Unfold's native modal handle related popups on normal admin pages,
  while unfold-modal keeps modals opened from a CMS-hosted admin, chains it started itself,
  and Django Filer widgets. The setting has no effect on Unfold versions without native
  related modals.

Changed:
--------

* The view-related link now opens in the modal instead of navigating away. On Unfold
  versions before 0.107, it previously left the form and navigated to the related object's
  change page.

Bug Fixes:
----------

* A related popup opened as a real browser window (``window.opener``) completes again on
  Unfold 0.107+. The popup response now calls ``opener.dismiss*`` directly instead of
  loading Unfold's own ``popup_response.js``, which assumes ``window.parent`` and left the
  window stuck on "Popup closing…".
* Lookup row selection inside the modal no longer logs an uncaught error; the selected
  value is still written back exactly once.

Other:
------

* ``admin/popup_response.html`` no longer contains inline JavaScript. The logic moved to
  ``unfold_modal/js/popup_response.js``, loaded with data attributes like Django's own
  template.
* Use ``const`` / ``let`` instead of ``var`` in all JavaScript files.

Tests:
------

* Add a shared related-widget click helper (``tests/ui_helpers.py``) and migrate the
  Playwright suite to Unfold's related-widget dropdown (0.86+), so tests no longer click
  ``#add_id_*`` / ``#change_id_*`` / ``#view_id_*`` / ``#delete_id_*`` directly.
* Add a native-modal ownership regression suite
  (``tests/test_ui_native_modal_ownership.py``).
* Add real Django Filer picker tests (``tests/test_ui_filer.py``); ``django-filer`` is now a
  test-only dependency.

CI:
---

* Add ``.github/dependabot.yml`` (``uv`` ecosystem) for ``django-unfold``, ``django``,
  ``django-filer`` and the Playwright test dependencies. Each update within the declared
  ranges gets its own PR and the full Playwright run; the ``django-unfold`` cap is raised
  by hand.
* Run the workflow on uv (``astral-sh/setup-uv``, ``uv sync --frozen``) with the
  Python 3.10 / 3.11 / 3.12 matrix.
* Exclude the Playwright tests from the unit test step with ``--ignore-glob``. The previous
  ``--ignore=tests/test_ui_*.py`` did not expand the pattern, so they ran in both steps.

Packaging:
----------

* Migrate dependency management from Poetry to uv. The ``test`` and ``dev`` dependencies
  move to ``[dependency-groups]``, and ``uv.lock`` replaces ``poetry.lock`` with the same
  pinned versions. Hatch remains the build backend.

0.2.2 (2026-08-26)
==================

Features:
---------

* Add Django Filer support: the folder and file selection widgets open in the modal and
  write the selection back to the field. (#15)

0.2.1 (2026-05-17)
==================

Tests:
------

* Sanitize and escape the admin URL parameters in the test app's iframe and modal host
  views to prevent HTML injection.
* Validate the format of ``__version__`` with a regex in the package tests.

0.2.0b1 (2026-03-10)
====================

Features:
---------

* ``{% unfold_modal_cms_head %}`` now loads the Material Symbols icon font, so the close
  and maximize controls show as glyphs in a CMS-hosted modal (T22b).

Bug Fixes:
----------

* Raise the modal z-index to ``9999999`` so it renders above the Django CMS layers (T22b).
* ``raw_id_fields`` lookups in CMS-hosted modals now reliably write the selected value back
  to the field (T23).

0.2.0b0 (2026-03-09)
====================

Features:
---------

* Add Django CMS integration: when the admin runs inside a CMS modal iframe
  (``.cms-modal``), modals open in the CMS parent document. Load the assets with
  ``{% unfold_modal_cms_head %}`` (T21a, T21b).
* Add ``UNFOLD_CMS_MODAL_SIZE``, ``UNFOLD_CMS_MODAL_RESIZE`` and
  ``UNFOLD_CMS_MODAL_DISABLE_HEADER``, independent of the ``UNFOLD_MODAL_*`` settings and
  defaulting to a fullscreen modal.
* Add the ``UNFOLD_MODAL_SHOW_ADD_IN_POPUP`` setting (default ``True``) for hiding the
  header "Add" link in popups. It currently has no effect with upstream django-unfold: no
  template or tag in this package reads it, and upstream's ``add_link.html`` has no check
  for it either (T22, T22a).

Bug Fixes:
----------

* Detect the modal iframe by its ``unfold-modal-iframe`` class instead of treating any
  iframe as one. Admin embedded in another iframe, such as the Django CMS sideframe, now
  opens its own modals instead of forwarding to the parent (T21).

Other:
------

* Modernize ``cms_host.js`` from ``var`` to ``const`` / ``let`` (T21c).
* Document the Django CMS modal support in the README.

0.1.0 (2026-02-19)
==================

Features:
---------

* Initial release: replace Django admin related-object popups with Unfold-styled modals
  that load the popup in an iframe, without patching Django or Unfold (T03).
* Support ForeignKey, ManyToMany and OneToOne selects, ``autocomplete_fields`` (Select2)
  and related fields inside inline forms.
* Support ``raw_id_fields`` lookups in the modal (T04b).
* Return the popup result to the parent window via ``postMessage`` and update the widget
  with Django's own dismiss functions (T04).
* Load the scripts through Unfold's ``SCRIPTS`` setting with ``get_modal_scripts``, so no
  admin template override is needed (T05, T08).
* Nested modals: opening a related object from within a modal replaces it on a stack and
  restores the previous modal on close (T10).
* Add size presets (``UNFOLD_MODAL_SIZE``: ``default``, ``large``, ``full``) and an
  optional resize handle (``UNFOLD_MODAL_RESIZE``), served through
  ``get_modal_scripts_with_config`` (T12).
* Add a title bar with a maximize button; the maximized state and a user-resized size
  persist across nested modals (T13, T13b, T13c).
* Hide the admin header inside modal iframes (``UNFOLD_MODAL_DISABLE_HEADER``, default
  ``True``) (T16, T16a).
* Dark mode support using Unfold's CSS token variables (T14d, T14e).
* ESC closes the modal; the background scroll is locked without a page jump.

Other:
------

* Split ``related_modal.js`` into separate modules (T14, T14a).
* Move all styling to external CSS: no ``!important``, no inline styles and no style
  injection from JS; icons use Material Symbols (T14c, T17, T17a).
* Rename the Python package from ``django_unfold_modal`` to ``unfold_modal``; the
  distribution name stays ``django-unfold-modal`` (T20, T20a).
* Remove unused code and settings (T15).

Tests:
------

* Add the test project and demo app, with pytest cases for permissions, popup responses
  and CSRF (T01, T06).
* Add Playwright UI tests for modals, nested modals, iframe scrolling, sizes and dark mode
  (T07, T11, T14d).

CI:
---

* Add a GitHub Actions workflow running pytest and the Playwright tests (T19).
