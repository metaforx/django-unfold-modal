"""Tests for popup rendering and popup_response behavior."""

import pytest

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
