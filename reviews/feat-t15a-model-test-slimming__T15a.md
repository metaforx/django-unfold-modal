# Review Notes - feat/t15a-model-test-slimming (T15a)

## Summary of T15a Changes

Removed the `Profile` model as it provided no unique widget coverage.

### Analysis

| Model | Widget Type | UI Test Coverage | Decision |
|-------|-------------|------------------|----------|
| Category | FK select | ✓ test_ui_modal.py | Keep |
| Tag | ManyToMany filter_horizontal | - | Keep (widget coverage) |
| Author | Autocomplete/Select2 | ✓ test_ui_modal.py | Keep |
| Publisher | raw_id_fields | ✓ test_ui_modal.py | Keep |
| Book | Multi-widget main model | ✓ test_ui_modal.py | Keep |
| Chapter | Inline related field | ✓ test_ui_modal.py | Keep |
| Country | Nested modal level 2 | ✓ test_ui_nested_modal.py | Keep |
| City | Nested modal level 1 | ✓ test_ui_nested_modal.py | Keep |
| Venue | Nested modal parent | ✓ test_ui_nested_modal.py | Keep |
| Event | Long form scrolling | ✓ test_ui_nested_modal.py | Keep |
| **Profile** | OneToOne (same as FK) | - | **Removed** |

### Rationale for Removing Profile

1. **No UI tests** - Profile was only tested in smoke tests
2. **Redundant widget type** - OneToOne behaves identically to FK for modal purposes
3. **Autocomplete already covered** - Author's autocomplete is tested via Book.author

### Files Changed

- `tests/server/testapp/models.py` - Removed Profile class
- `tests/server/testapp/admin.py` - Removed ProfileAdmin
- `tests/test_smoke.py` - Removed Profile test and import
- `tests/server/testapp/migrations/0003_delete_profile.py` - New migration

## Verification

```bash
$ pytest -q
# 90 passed (was 91 - one smoke test removed)

$ pytest --collect-only | grep -c "<Function"
# 90 tests collected
```

All widget types remain covered by existing tests.

## Status: Done
