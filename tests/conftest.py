import pytest
from django.contrib.auth import get_user_model


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


@pytest.fixture(scope="function")
def admin_user(db):
    """Create an admin user for Playwright tests."""
    User = get_user_model()
    return User.objects.create_superuser(
        username="playwrightadmin",
        email="playwright@example.com",
        password="playwrightpass",
    )


@pytest.fixture(scope="function")
def authenticated_page(browser, live_server, admin_user):
    """A Playwright page logged into the admin site.

    Uses browser fixture directly to avoid async context issues.
    """
    # Create a new context and page
    context = browser.new_context()
    page = context.new_page()

    # Navigate to admin login with next parameter
    page.goto(f"{live_server.url}/admin/login/?next=/admin/")

    # Fill in login form
    page.fill('input[name="username"]', "playwrightadmin")
    page.fill('input[name="password"]', "playwrightpass")
    page.click('button[type="submit"], input[type="submit"]')

    # Wait for navigation to complete
    page.wait_for_load_state("networkidle")

    yield page

    # Cleanup
    context.close()
