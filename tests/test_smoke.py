"""Smoke tests to verify test infrastructure is working."""

import pytest
from django.contrib.admin.sites import site as admin_site

from testapp.models import Author, Book, Category, Chapter, Publisher, Tag


@pytest.mark.django_db
class TestModelsExist:
    """Verify all models are properly defined and can be instantiated."""

    def test_category_model(self):
        category = Category.objects.create(name="Fiction")
        assert str(category) == "Fiction"

    def test_tag_model(self):
        tag = Tag.objects.create(name="Bestseller")
        assert str(tag) == "Bestseller"

    def test_author_model(self):
        author = Author.objects.create(name="Jane Doe")
        assert str(author) == "Jane Doe"

    def test_publisher_model(self):
        publisher = Publisher.objects.create(name="Acme Publishing")
        assert str(publisher) == "Acme Publishing"

    def test_book_model(self):
        book = Book.objects.create(title="Test Book")
        assert str(book) == "Test Book"

    def test_chapter_model(self):
        book = Book.objects.create(title="Test Book")
        chapter = Chapter.objects.create(book=book, title="Introduction", number=1)
        assert "Chapter 1" in str(chapter)


@pytest.mark.django_db
class TestAdminRegistered:
    """Verify all models are registered with the admin site."""

    def test_models_registered(self):
        registered_models = [model.__name__ for model in admin_site._registry.keys()]
        expected = ["Category", "Tag", "Author", "Publisher", "Book", "Chapter"]
        for model_name in expected:
            assert model_name in registered_models, f"{model_name} not registered"


@pytest.mark.django_db
class TestAdminAccess:
    """Verify admin pages are accessible."""

    def test_admin_index(self, admin_client):
        response = admin_client.get("/admin/")
        assert response.status_code == 200

    def test_book_changelist(self, admin_client):
        response = admin_client.get("/admin/testapp/book/")
        assert response.status_code == 200

    def test_book_add(self, admin_client):
        response = admin_client.get("/admin/testapp/book/add/")
        assert response.status_code == 200
