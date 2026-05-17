"""Tests for unfold_modal package."""

import re


class TestPackageImport:
    """Verify package can be imported and has expected attributes."""

    def test_import_package(self):
        import unfold_modal

        assert isinstance(unfold_modal.__version__, str)
        assert re.match(r"^\d+\.\d+\.\d+", unfold_modal.__version__)

    def test_import_app_config(self):
        from unfold_modal.apps import UnfoldModalConfig

        assert UnfoldModalConfig.name == "unfold_modal"

    def test_default_settings(self):
        from unfold_modal.apps import UnfoldModalConfig

        defaults = UnfoldModalConfig.default_settings
        assert defaults["UNFOLD_MODAL_VARIANT"] == "iframe"
        assert defaults["UNFOLD_MODAL_PRESENTATION"] == "modal"
