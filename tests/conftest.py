import pytest


@pytest.fixture
def admin_client(client, django_user_model):
    """A Django test client logged in as an admin user."""
    user = django_user_model.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="password",
    )
    client.force_login(user)
    return client
