# Tests Overview

This project uses a Django test app plus pytest and Playwright to verify modal behavior.

## What’s Covered

- Pytest (unit/integration): settings, config endpoint, popup responses, permissions, CSRF.
- Playwright (UI): modal DOM, widget integration, nested modal behavior, resize/maximize UX.

## How to Run

```bash
pytest -q
pytest --browser chromium
```

## Test App

The test app models are designed to exercise:
- FK/M2M related widgets
- Autocomplete/select2 widgets
- `raw_id_fields` lookup
- Inline related fields
- Nested modal flows (Venue → City → Country)
