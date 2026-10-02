=========
Changelog
=========

All notable changes to django-unfold-modal are documented here.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

Unreleased
==========

Packaging:
----------

* Migrate dependency management from Poetry to uv. The ``test`` and ``dev`` dependencies
  move to ``[dependency-groups]``, and ``uv.lock`` replaces ``poetry.lock`` with the same
  pinned versions. Hatch remains the build backend.

CI:
---

* Run the workflow on uv (``astral-sh/setup-uv``, ``uv sync --frozen``) with the
  Python 3.10 / 3.11 / 3.12 matrix.
* Exclude the Playwright tests from the unit test step with ``--ignore-glob``. The previous
  ``--ignore=tests/test_ui_*.py`` did not expand the pattern, so they ran in both steps.

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
  header "Add" link in popups. The check itself lives in django-unfold's ``add_link.html``,
  because a template override in this package loses to ``unfold`` in ``INSTALLED_APPS``
  order (T22, T22a).

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
