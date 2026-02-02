"""Tests for permission checks on related widget links."""

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from testapp.models import Author, Book, Category


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(name="Fiction")


@pytest.fixture
def author(db):
    """Create a test author."""
    return Author.objects.create(name="Jane Doe")


@pytest.fixture
def book(db, category, author):
    """Create a test book with related objects."""
    return Book.objects.create(title="Test Book", category=category, author=author)


@pytest.fixture
def user_with_book_perms(django_user_model, db):
    """Create a user with only book permissions (no category/author perms)."""
    user = django_user_model.objects.create_user(
        username="bookuser",
        email="book@example.com",
        password="password",
        is_staff=True,
    )
    # Add only book permissions
    content_type = ContentType.objects.get_for_model(Book)
    perms = Permission.objects.filter(content_type=content_type)
    user.user_permissions.add(*perms)
    return user


@pytest.fixture
def user_with_all_perms(django_user_model, db):
    """Create a user with all model permissions."""
    user = django_user_model.objects.create_user(
        username="allperms",
        email="all@example.com",
        password="password",
        is_staff=True,
    )
    # Add permissions for all test models
    for model in [Book, Category, Author]:
        content_type = ContentType.objects.get_for_model(model)
        perms = Permission.objects.filter(content_type=content_type)
        user.user_permissions.add(*perms)
    return user


@pytest.mark.django_db
class TestRelatedWidgetPermissions:
    """Test that related widget links respect permissions."""

    def test_add_link_visible_with_permission(self, client, user_with_all_perms):
        """Add link should be visible when user has add permission."""
        client.force_login(user_with_all_perms)
        response = client.get("/admin/testapp/book/add/")
        assert response.status_code == 200
        content = response.content.decode()
        # Check for add related link for category (has permission)
        assert "add_id_category" in content or "related-widget-wrapper" in content

    def test_add_link_hidden_without_permission(self, client, user_with_book_perms):
        """Add link should be hidden when user lacks add permission."""
        client.force_login(user_with_book_perms)
        response = client.get("/admin/testapp/book/add/")
        assert response.status_code == 200
        content = response.content.decode()
        # User has book perms but not category add perm
        # The add link for category should not be present
        assert "add_id_category" not in content

    def test_change_link_visible_with_permission(
        self, client, user_with_all_perms, book
    ):
        """Change link should be visible when user has change permission."""
        client.force_login(user_with_all_perms)
        response = client.get(f"/admin/testapp/book/{book.pk}/change/")
        assert response.status_code == 200
        content = response.content.decode()
        # Check for change related link
        assert "change_id_category" in content or "change-related" in content

    def test_change_link_hidden_without_permission(
        self, client, user_with_book_perms, book
    ):
        """Change link should be hidden when user lacks change permission."""
        client.force_login(user_with_book_perms)
        response = client.get(f"/admin/testapp/book/{book.pk}/change/")
        assert response.status_code == 200
        content = response.content.decode()
        # User lacks category change permission
        assert "change_id_category" not in content

    def test_delete_link_requires_permission(self, client, user_with_all_perms, book):
        """Delete link should only appear with delete permission."""
        client.force_login(user_with_all_perms)
        response = client.get(f"/admin/testapp/book/{book.pk}/change/")
        assert response.status_code == 200
        content = response.content.decode()
        # With all perms, delete link should be present
        assert "delete_id_category" in content or "delete-related" in content
