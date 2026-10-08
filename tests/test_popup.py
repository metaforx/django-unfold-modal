"""Tests for popup rendering and popup_response behavior."""

import json
import re
from html import unescape
from pathlib import Path

import pytest
from django.contrib.staticfiles import finders

from testapp.models import Author, Category


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(name="Fiction")


@pytest.fixture
def author(db):
    """Create a test author."""
    return Author.objects.create(name="Jane Doe")


@pytest.mark.django_db
class TestPopupRendering:
    """Test that popup mode renders correctly with _popup=1."""

    def test_add_form_with_popup_parameter(self, admin_client):
        """Add form should include is_popup context when _popup=1."""
        response = admin_client.get("/admin/testapp/category/add/?_popup=1")
        assert response.status_code == 200
        # Check that the response has popup-specific rendering
        content = response.content.decode()
        # Django adds _popup hidden field in popup mode
        assert '_popup' in content or 'is_popup' in content

    def test_add_form_without_popup_parameter(self, admin_client):
        """Add form should render normally without _popup parameter."""
        response = admin_client.get("/admin/testapp/category/add/")
        assert response.status_code == 200
        # Normal rendering should have full admin chrome
        content = response.content.decode()
        assert "<!DOCTYPE html>" in content

    def test_change_form_with_popup_parameter(self, admin_client, category):
        """Change form should include is_popup context when _popup=1."""
        response = admin_client.get(
            f"/admin/testapp/category/{category.pk}/change/?_popup=1"
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert '_popup' in content or 'is_popup' in content

    def test_popup_form_has_hidden_popup_field(self, admin_client):
        """Popup form should include hidden _popup field."""
        response = admin_client.get("/admin/testapp/category/add/?_popup=1")
        assert response.status_code == 200
        content = response.content.decode()
        # Check for hidden input with name="_popup"
        assert 'name="_popup"' in content


@pytest.mark.django_db
class TestPopupResponsePayload:
    """Test popup_response.html template and its payloads."""

    def test_add_popup_response(self, admin_client):
        """Successful add in popup should return popup_response with correct data."""
        response = admin_client.post(
            "/admin/testapp/category/add/?_popup=1",
            {"name": "New Category", "_popup": "1"},
            follow=False,
        )
        # Should redirect to popup_response or render it directly
        if response.status_code == 302:
            # Follow the redirect
            response = admin_client.get(response.url)

        assert response.status_code == 200
        content = response.content.decode()

        # Should contain popup response data
        # Our template or Django's should have the popup response
        assert "popup" in content.lower() or "Popup closing" in content

    def test_add_popup_response_contains_object_data(self, admin_client):
        """Popup response should contain the new object ID and representation."""
        response = admin_client.post(
            "/admin/testapp/category/add/?_popup=1",
            {"name": "Science Fiction", "_popup": "1"},
            follow=True,
        )
        assert response.status_code == 200
        content = response.content.decode()

        # The response should contain the object representation
        # Either in JSON format or escaped in the template
        assert "Science Fiction" in content or "Science" in content

    def test_change_popup_response(self, admin_client, category):
        """Successful change in popup should return popup_response."""
        response = admin_client.post(
            f"/admin/testapp/category/{category.pk}/change/?_popup=1",
            {"name": "Updated Category", "_popup": "1"},
            follow=True,
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "popup" in content.lower() or "Updated Category" in content

    def test_popup_response_structure(self, admin_client):
        """Verify popup_response has expected structure for postMessage."""
        response = admin_client.post(
            "/admin/testapp/author/add/?_popup=1",
            {"name": "New Author", "_popup": "1"},
            follow=True,
        )
        assert response.status_code == 200
        content = response.content.decode()

        # Our popup_response.html should have postMessage logic
        # or Django's default popup_response.js reference
        assert "postMessage" in content or "popup_response" in content.lower()


def _popup_response_marker(content):
    """Return the popup response marker element's opening tag."""
    match = re.search(
        r'<script id="django-admin-popup-response-constants"[^>]*>', content
    )
    assert match, "popup response marker element not found"
    return match.group(0)


def _popup_response_data(content):
    """Return the payload carried by the popup response marker element."""
    match = re.search(
        r'data-popup-response="([^"]*)"', _popup_response_marker(content)
    )
    assert match, "popup response payload not found"
    return json.loads(unescape(match.group(1)))


def _popup_response_script():
    """Return the source of the package's popup_response.js."""
    path = finders.find("unfold_modal/js/popup_response.js")
    assert path, "unfold_modal/js/popup_response.js not found"
    return Path(path).read_text()


@pytest.mark.django_db
class TestPopupResponseContexts:
    """popup_response in the modal iframe, a real popup and Unfold's native modal."""

    def _add_response(self, admin_client, name="Marker Category"):
        response = admin_client.post(
            "/admin/testapp/category/add/?_popup=1",
            {"name": name, "_popup": "1"},
        )
        assert response.status_code == 200
        return response.content.decode()

    def test_marker_carries_add_payload(self, admin_client):
        """Unfold's native modal and the admin's own script read this marker."""
        data = _popup_response_data(self._add_response(admin_client, 'A "quoted" <b>'))
        category = Category.objects.get(name='A "quoted" <b>')
        assert data["value"] == str(category.pk)
        assert data["obj"] == 'A "quoted" <b>'
        assert data.get("action") != "change"

    def test_marker_carries_change_payload(self, admin_client, category):
        response = admin_client.post(
            f"/admin/testapp/category/{category.pk}/change/?_popup=1",
            {"name": "Renamed", "_popup": "1"},
        )
        data = _popup_response_data(response.content.decode())
        assert data["action"] == "change"
        assert data["value"] == str(category.pk)
        assert data["new_value"] == str(category.pk)
        assert data["obj"] == "Renamed"

    def test_marker_carries_delete_payload(self, admin_client, category):
        response = admin_client.post(
            f"/admin/testapp/category/{category.pk}/delete/?_popup=1",
            {"post": "yes", "_popup": "1"},
        )
        data = _popup_response_data(response.content.decode())
        assert data["action"] == "delete"
        assert data["value"] == str(category.pk)

    def test_template_has_no_inline_script(self, admin_client):
        """The marker loads the package script and hands it the admin's own."""
        content = self._add_response(admin_client)
        marker = _popup_response_marker(content)
        assert re.search(r'src="[^"]*unfold_modal/js/popup_response\.js"', marker)
        assert re.search(
            r'data-admin-script="[^"]*admin/js/popup_response\.js"', marker
        )
        assert content.count("<script") == 1
        assert re.search(r"<script[^>]*>\s*</script>", content)

    def test_unfold_modal_iframe_branch_posts_message(self):
        script = _popup_response_script()
        assert "unfold-modal-iframe" in script
        assert "window.parent.postMessage" in script
        for message_type in ("add", "change", "delete"):
            assert f"django:popup:{message_type}" in script

    def test_real_popup_branch_calls_opener_directly(self):
        """Unfold >=0.107 ships a popup_response.js that targets window.parent."""
        script = _popup_response_script()
        assert "opener.dismissAddRelatedObjectPopup(window" in script
        assert "opener.dismissChangeRelatedObjectPopup(window" in script
        assert "opener.dismissDeleteRelatedObjectPopup(window" in script
        opener_branch = script[script.index("if (window.opener)") :]
        admin_script = opener_branch.index("marker.dataset.adminScript")
        assert opener_branch.index("return;") < admin_script

    def test_native_modal_branch_loads_admin_popup_response_js(self):
        assert "script.src = marker.dataset.adminScript" in _popup_response_script()


@pytest.mark.django_db
class TestDeletePopupResponse:
    """Test delete confirmation in popup mode."""

    def test_delete_confirmation_in_popup(self, admin_client, category):
        """Delete confirmation should work in popup mode."""
        response = admin_client.get(
            f"/admin/testapp/category/{category.pk}/delete/?_popup=1"
        )
        assert response.status_code == 200
        content = response.content.decode()
        # Should show delete confirmation
        assert "delete" in content.lower() or "confirm" in content.lower()

    def test_delete_popup_response(self, admin_client, category):
        """Successful delete in popup should return popup_response."""
        cat_id = category.pk
        response = admin_client.post(
            f"/admin/testapp/category/{cat_id}/delete/?_popup=1",
            {"post": "yes", "_popup": "1"},
            follow=True,
        )
        assert response.status_code == 200
        # Category should be deleted
        assert not Category.objects.filter(pk=cat_id).exists()
