# Task T19 - GitHub Actions CI for Pytest + Playwright

Goal
- Add CI pipeline that runs pytest and Playwright and blocks merges on failure.

Suggested Skill
- Use `$unfold-dev-structured` (Sonnet).
- Review with `$unfold-codex-reviewer`.

Scope
- Add GitHub Actions workflow:
  - Python setup (3.10+).
  - Install deps (Poetry).
  - Run `pytest -q`.
  - Run `pytest --browser chromium`.
- Configure branch protection expectations (documented in README or repo settings).
- Ensure Playwright dependencies are installed in CI.

Non-goals
- No changes to application code.
- No new test frameworks.

Deliverables
- `.github/workflows/ci.yml` (or similar).
- README note about CI and required checks.

Acceptance Criteria
- CI runs on PRs and pushes.
- Failures block merge (via required checks in GitHub settings).

Tests to run
- CI only.
