# django-unfold-modal

Modal-based related-object popups for [django-unfold](https://github.com/unfoldadmin/django-unfold).

Replaces Django admin's popup windows for related objects (ForeignKey, ManyToMany, etc.) with Unfold-styled modals.

## Requirements

- Python 3.10+
- Django 5.0+
- django-unfold 0.52.0+

## Installation

```bash
pip install django-unfold-modal
```

Add to your `INSTALLED_APPS` after `unfold`:

```python
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "django_unfold_modal",  # Add after unfold, before django.contrib.admin
    "django.contrib.admin",
    # ...
]
```

Add the required scripts to your Unfold configuration in `settings.py`:

```python
from django_unfold_modal.utils import get_modal_scripts

UNFOLD = {
    # ... other unfold settings ...
    "SCRIPTS": [
        *get_modal_scripts(),
    ],
}
```

## Configuration

The following settings are available (all optional):

```python
# Enable/disable modal functionality (default: True)
UNFOLD_MODAL_ENABLED = True

# Content loading strategy: "iframe" (default, v1 only)
UNFOLD_MODAL_VARIANT = "iframe"

# Presentation style: "modal" (default, v1 only)
UNFOLD_MODAL_PRESENTATION = "modal"

# Modal size preset: "default", "large", or "full"
UNFOLD_MODAL_SIZE = "default"

# Enable manual resize handle on modal (default: False)
UNFOLD_MODAL_RESIZE = False
```

### Size Presets

To use custom size presets (`UNFOLD_MODAL_SIZE`) or enable resize (`UNFOLD_MODAL_RESIZE`),
include the app's URLs in your `urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("unfold-modal/", include("django_unfold_modal.urls")),
]
```

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

## License

MIT
