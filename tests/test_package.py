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

    def test_override_native_defaults_to_true(self):
        from unfold_modal.apps import UnfoldModalConfig, get_setting

        assert UnfoldModalConfig.default_settings["UNFOLD_MODAL_OVERRIDE_NATIVE"] is True
        assert get_setting("UNFOLD_MODAL_OVERRIDE_NATIVE") is True


class TestModalScriptLists:
    """The related-click adapter is part of both admin script helpers."""

    def test_get_modal_scripts_includes_adapter(self):
        from unfold_modal.utils import get_modal_scripts

        urls = [script(None) for script in get_modal_scripts()]
        assert any("unfold_modal/js/unfold_related_adapter.js" in url for url in urls)

    def test_get_modal_scripts_with_config_includes_adapter(self):
        from unfold_modal.utils import get_modal_scripts_with_config

        urls = [script(None) for script in get_modal_scripts_with_config()]
        assert any("unfold_modal/js/unfold_related_adapter.js" in url for url in urls)


class TestOverrideNativeFlag:
    """UNFOLD_MODAL_OVERRIDE_NATIVE reaches the adapter through its script URL."""

    ADAPTER = "unfold_modal/js/unfold_related_adapter.js"

    def _adapter_url(self, helper):
        urls = [script(None) for script in helper()]
        matches = [url for url in urls if self.ADAPTER in url]
        assert len(matches) == 1
        return matches[0]

    def test_own_all_by_default(self):
        from unfold_modal.utils import get_modal_scripts, get_modal_scripts_with_config

        for helper in (get_modal_scripts, get_modal_scripts_with_config):
            assert self._adapter_url(helper).endswith(self.ADAPTER)

    def test_coexist_adds_fragment(self, settings):
        from unfold_modal.utils import get_modal_scripts, get_modal_scripts_with_config

        settings.UNFOLD_MODAL_OVERRIDE_NATIVE = False
        for helper in (get_modal_scripts, get_modal_scripts_with_config):
            assert self._adapter_url(helper).endswith(self.ADAPTER + "#coexist")

    def test_setting_is_read_per_request(self, settings):
        """The flag follows the setting after the script list was built."""
        from unfold_modal.utils import get_modal_scripts

        scripts = get_modal_scripts()
        settings.UNFOLD_MODAL_OVERRIDE_NATIVE = False
        assert any(script(None).endswith("#coexist") for script in scripts)
        settings.UNFOLD_MODAL_OVERRIDE_NATIVE = True
        assert not any("#coexist" in script(None) for script in scripts)

    def test_other_scripts_unchanged(self, settings):
        from unfold_modal.utils import get_modal_scripts

        settings.UNFOLD_MODAL_OVERRIDE_NATIVE = False
        urls = [script(None) for script in get_modal_scripts()]
        assert [url for url in urls if "#" in url] == [
            url for url in urls if self.ADAPTER in url
        ]
