# Tests Overview

This project uses a Django test app plus pytest and Playwright to verify modal behavior.

## Test Structure

```
tests/
├── server/testapp/       # Django test application
│   ├── models.py         # Test models (Book, Author, Category, etc.)
│   ├── admin.py          # Admin configuration with various widget types
│   └── settings.py       # Test settings with modal configuration
├── conftest.py           # Pytest fixtures (live_server, authenticated_page)
├── test_*.py             # Unit/integration tests
└── test_ui_*.py          # Playwright UI tests
```

## What's Covered

**Pytest (unit/integration):**
- `test_package.py` - Package metadata and imports
- `test_modal_config.py` - Config endpoint responses
- `test_popup.py` - Popup response template behavior
- `test_permissions.py` - Admin permission checks
- `test_csrf.py` - CSRF token handling
- `test_smoke.py` - Basic admin page loading

**Playwright (UI):**
- `test_ui_modal.py` - Modal DOM, widget integration (FK, M2M, raw_id, autocomplete)
- `test_ui_nested_modal.py` - Nested modal flows, stack behavior
- `test_ui_modal_ux.py` - Resize, maximize, overlay transitions
- `test_ui_modal_size.py` - Size presets verification
- `test_ui_dark_mode.py` - Dark mode styling
- `test_ui_header_suppression.py` - Admin header hiding in iframes

## How to Run

```bash
# All tests (unit + UI)
pytest -q

# UI tests only with specific browser
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit

# Specific test file
pytest tests/test_ui_modal.py -v

# Run with visible browser (debugging)
pytest --browser chromium --headed
```

## Test App Models

The test app models exercise various relationship patterns:

| Model | Purpose |
|-------|---------|
| `Book` | FK (Category, Publisher), M2M (Authors, Tags), autocomplete |
| `Author` | Simple model for autocomplete testing |
| `Category` | Simple FK target |
| `Tag` | M2M target for multiple relationship testing |
| `Publisher` | raw_id_fields target |
| `Venue` | Nested FK chain (Venue → City → Country) |
| `City` | Mid-level FK for nested modal testing |
| `Country` | Leaf FK for nested modal testing |
| `Event` | Inline related fields, scrollable content |

## Fixtures

Key fixtures in `conftest.py`:

- `authenticated_page` - Playwright page with admin login
- `admin_user` - Django admin user for authentication
- `admin_client` - Django test client with admin login

Note: `live_server` is a pytest-django built-in fixture.
