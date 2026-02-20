![Unfold modal preview](docs/images/unfold-modal.png)
# django-unfold-modal
[![PyPI - Version](https://img.shields.io/pypi/v/django-unfold-modal.svg?style=for-the-badge)](https://pypi.org/project/django-unfold-modal/) [![CI](https://github.com/metaforx/django-unfold-modal/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/metaforx/django-unfold-modal/actions/workflows/ci.yml)

Modal-based related-object popups for [django-unfold](https://github.com/unfoldadmin/django-unfold).

Replaces Django admin's popup windows for related objects (ForeignKey, ManyToMany, etc.) with Unfold-styled modals.

## Features
- Modal replacement for admin related-object popups
- Supports nested modals (replace/restore behavior)
- Raw ID lookup + autocomplete + inline related fields
- Optional modal resize + size presets
- Optional admin header suppression inside iframe
- Stylable using Unfold theme configuration & custom CSS

## Motivation
As much as I love the Django admin, I’ve always found its related-object pop-ups clunky and outdated. 
They open in separate browser windows, which breaks the flow and doesn’t fit modern UI patterns. 
It’s fine for straightforward admin use, but when exposed to users, it often causes confusion.

[Django Unfold](https://github.com/unfoldadmin/django-unfold) greatly improves the admin’s UX for regular users.
This package modernizes related-object interactions while following Unfold’s design principles.

> **AI Disclaimer:** Beyond the practical use of the package, the project was also driven by the incentive to explore AI-assisted research and development. All code was intentionally written by AI using structured, automated agent orchestration, including development and review by different models (Claude CLI Sonnet/Opus & Codex CLI), result verification, and regression testing.
> 
> Design and implementation decisions were made by me and reviewed/tested.
>
> If interested in the process, see plans, tasks and reviews folder to get an idea of how the package was developed.


## Requirements

- Python 3.10+
- Django 5.0+
- django-unfold 0.52.0+ (tested with latest)

## Installation

```bash
pip install django-unfold-modal
```

Add to your `INSTALLED_APPS` after `unfold`:

```python
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold_modal",  # Add after unfold, before django.contrib.admin
    "django.contrib.admin",
    # ...
]
```

Add the required styles and scripts to your Unfold configuration in `settings.py`:

**Minimal setup:**

```python
from unfold_modal.utils import get_modal_styles, get_modal_scripts

UNFOLD = {
    # ... other unfold settings ...
    "STYLES": [
        *get_modal_styles(),
    ],
    "SCRIPTS": [
        *get_modal_scripts(),
    ],
}
```

This setup loads only the core modal scripts. If you do not use the configuration options below, this is enough.

**Config-enabled setup** (for custom sizes and resize handle):

```python
from unfold_modal.utils import get_modal_styles, get_modal_scripts_with_config

UNFOLD = {
    # ... other unfold settings ...
    "STYLES": [
        *get_modal_styles(),
    ],
    "SCRIPTS": [
        *get_modal_scripts_with_config(),
    ],
}
```

This setup adds a config script (served from `unfold_modal.urls`) before the core JS so the frontend can read size presets and `UNFOLD_MODAL_RESIZE`. See **Configuration** below for the options that require it.

## Configuration

The following settings are available (all optional):

```python
# Content loading strategy: "iframe" (default, v1 only)
UNFOLD_MODAL_VARIANT = "iframe"

# Presentation style: "modal" (default, v1 only)
UNFOLD_MODAL_PRESENTATION = "modal"

# Modal size preset: "default", "large", or "full"
UNFOLD_MODAL_SIZE = "default"

# Enable manual resize handle on modal (default: False)
UNFOLD_MODAL_RESIZE = False

# Hide admin header inside modal iframes (default: True)
UNFOLD_MODAL_DISABLE_HEADER = True
```

### Size Presets

To use custom size presets (`UNFOLD_MODAL_SIZE`) or enable resize (`UNFOLD_MODAL_RESIZE`):

1. Include the app's URLs in your `urls.py`:

    ```python
    from django.urls import include, path

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("unfold-modal/", include("unfold_modal.urls")),
    ]
    ```

2. Use `get_modal_scripts_with_config` instead of `get_modal_scripts` in your UNFOLD configuration (see Installation section above).

| Preset    | Width | Max Width | Height | Max Height |
|-----------|-------|-----------|--------|------------|
| `default` | 90%   | 900px     | 85vh   | 700px      |
| `large`   | 95%   | 1200px    | 90vh   | 900px      |
| `full`    | 98%   | none      | 95vh   | none       |

## Supported Widgets

- ForeignKey select
- ManyToMany select
- OneToOne select
- `raw_id_fields` lookup
- `autocomplete_fields` (Select2)
- Related fields within inline forms

## Testing

```bash
pytest -q
pytest --browser chromium
```

See `tests/README.md` for the test app overview and Playwright scope.

## CI

GitHub Actions runs on all PRs and pushes to `main`/`development`:

- Unit tests across Python 3.10, 3.11, 3.12
- Playwright UI tests with Chromium

Configure branch protection to require the CI check to pass before merging.

## License

MIT
