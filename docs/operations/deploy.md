---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# Runbook: Deploy and roll back

**Use when:** promoting `staging` to production, or undoing a bad release.
**Access needed:** GitHub (merge to `main`), the hosting dashboard, Infisical.

## Flow

`feat/*`, `fix/*` → PR → `staging` (deploys to staging) → PR `staging` → `main` (deploys to production)

## Before you start

- [ ] `.foundation/project.json` stage is `development` (otherwise `promotion_gate` blocks the release)
- [ ] CI is green on `staging`: `checks`, `security_staging`, `drift`, `supabase_drift`
- [ ] This release's migrations were applied to staging and tested
- [ ] New env vars exist in Infisical for production, and are synced to hosting
- [ ] Feature flags for unfinished work are off in production
- [ ] CHANGELOG.md `[Unreleased]` is accurate

## Steps

1. Open a PR from `staging` to `main`, titled with the release version or date.
2. Chris merges it with a **merge commit** (only admins can merge to `main`; see `docs/engineering/BRANCHING-AND-RELEASES.md`).
3. Watch the production deploy:
4. Apply production migrations, if the host doesn't do it automatically:

## Verify it worked

- Health check:
- Smoke test the core flow:
- Watch error tracking for 15 minutes.

## Roll back

1. Redeploy the previous `prod-*` tag from the hosting dashboard (fastest).
2. Revert the release merge on `main` through a `hotfix/revert-…` PR, then back-merge `main` into `staging`.
3. If a migration shipped, apply its down migration only if it's safe for the data; otherwise roll forward with a fix.
4. Note it in `docs/STATUS.md` → Known issues.
