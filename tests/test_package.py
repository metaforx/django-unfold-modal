"""Tests for django_unfold_modal package."""


class TestPackageImport:
    """Verify package can be imported and has expected attributes."""

    def test_import_package(self):
        import django_unfold_modal

        assert django_unfold_modal.__version__ == "0.1.0"

    def test_import_app_config(self):
        from django_unfold_modal.apps import DjangoUnfoldModalConfig

        assert DjangoUnfoldModalConfig.name == "django_unfold_modal"

    def test_default_settings(self):
        from django_unfold_modal.apps import DjangoUnfoldModalConfig

        defaults = DjangoUnfoldModalConfig.default_settings
        assert defaults["UNFOLD_MODAL_VARIANT"] == "iframe"
        assert defaults["UNFOLD_MODAL_PRESENTATION"] == "modal"
