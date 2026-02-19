# Review Notes - feat/t17-tailwind-css-refactor (T17)

## Status

Planned (not implemented yet).

## Expected Scope (for future review)

- Move modal inline `style.cssText` rules into Tailwind 4 CSS.
- Keep JS purely class-based.
- Maintain dark-mode parity with Unfold tokens.
- Ensure no visual regressions in modal layout or interactions.

## Tests to Run

```bash
pytest -q
pytest --browser chromium
```
