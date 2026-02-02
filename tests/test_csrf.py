"""Tests for CSRF enforcement in popup forms."""

import pytest
from django.test import Client

from testapp.models import Category


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(name="Fiction")


@pytest.mark.django_db
class TestCSRFEnforcement:
    """Test that CSRF protection is enforced for popup forms."""

    def test_post_without_csrf_token_fails(self, admin_client):
        """POST without CSRF token should fail."""
        # Create a client that doesn't enforce CSRF for setup
        # but then test with CSRF enforcement
        client = Client(enforce_csrf_checks=True)

        # Login the admin user
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_superuser(
            username="csrfadmin", email="csrf@example.com", password="password"
        )
        client.login(username="csrfadmin", password="password")

        # Try to POST without CSRF token
        response = client.post(
            "/admin/testapp/category/add/?_popup=1",
            {"name": "No CSRF Category", "_popup": "1"},
        )
        # Should get 403 Forbidden
        assert response.status_code == 403

    def test_post_with_csrf_token_succeeds(self, admin_client):
        """POST with valid CSRF token should succeed."""
        # Get the form first to obtain CSRF token
        response = admin_client.get("/admin/testapp/category/add/?_popup=1")
        assert response.status_code == 200

        # POST with the form (admin_client handles CSRF automatically)
        response = admin_client.post(
            "/admin/testapp/category/add/?_popup=1",
            {"name": "With CSRF Category", "_popup": "1"},
            follow=True,
        )
        # Should succeed
        assert response.status_code == 200
        assert Category.objects.filter(name="With CSRF Category").exists()

    def test_popup_form_contains_csrf_token(self, admin_client):
        """Popup form should include CSRF token."""
        response = admin_client.get("/admin/testapp/category/add/?_popup=1")
        assert response.status_code == 200
        content = response.content.decode()
        # Check for csrfmiddlewaretoken input
        assert "csrfmiddlewaretoken" in content

    def test_change_form_csrf_enforcement(self, admin_client, category):
        """Change form should also enforce CSRF."""
        # Verify the form has CSRF token
        response = admin_client.get(
            f"/admin/testapp/category/{category.pk}/change/?_popup=1"
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "csrfmiddlewaretoken" in content

        # POST should work with proper CSRF
        response = admin_client.post(
            f"/admin/testapp/category/{category.pk}/change/?_popup=1",
            {"name": "CSRF Updated", "_popup": "1"},
            follow=True,
        )
        assert response.status_code == 200

    def test_delete_form_csrf_enforcement(self, admin_client, category):
        """Delete form should also enforce CSRF."""
        response = admin_client.get(
            f"/admin/testapp/category/{category.pk}/delete/?_popup=1"
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "csrfmiddlewaretoken" in content
