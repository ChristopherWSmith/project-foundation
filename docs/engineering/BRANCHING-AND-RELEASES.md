# Branching and releases

Part of the project foundation. The why is in ADR 0002. Branch rules are applied by `scripts/github/apply-protection.py` and checked by `scripts/github/verify-protection.py`.

## Branches

| Branch | Role | Who merges | Merge method | Deploys to |
|---|---|---|---|---|
| `feat/*`, `fix/*`, `chore/*` | Work | — | — | preview, if any |
| `staging` | Integration; the **default branch** | GitHub auto-merge once every required check passes (agents enable it) | squash (features), merge commit (back-merges) | staging |
| `main` | Production | **Chris only** (admin; ruleset "restrict updates") | merge commit | production |
| `hotfix/*` | Urgent production fix, branched from `main` | — | — | — |

`staging` is the default branch because every PR, every agent and every Renovate update should land on integration, never on production, by default.

## Required checks

| Check | staging | main |
|---|---|---|
| `checks` (quality gates) | ✓ | ✓ |
| `security_staging` (secrets, audit) | ✓ | ✓ |
| `drift` (docs, env, hygiene, doc triggers, handoff) | ✓ | ✓ |
| `review-gate` (independent review of the head commit) | ✓ | — (already reviewed on the way into staging) |
| Code-owner approval for gates and agent rules | ✓ | — |
| `promotion_gate` (only staging/hotfix; not in bootstrap; contains main) | — | ✓ |
| `supabase_drift` (if present) | ✓ | ✓ |

## Release (staging → main)

1. Open a PR from `staging` to `main`. CI runs the full set plus `promotion_gate`.
2. Chris reviews what's in it and merges with a **merge commit**. That merge is the production approval.
3. Production deploys from `main`. The deploy job uses the `production` environment, whose secrets only `main` can read.
4. `tag_release` tags the commit `prod-YYYY-MM-DD-<sha>`. These tags are the rollback targets.

A project in the `bootstrap` stage can't be released: `promotion_gate` fails until `.foundation/project.json` is `development`.

## Hotfix

1. Branch `hotfix/<slug>` from `main`, fix it, open a PR into `main`. CI runs; Chris merges.
2. **Back-merge**: open a PR from `main` into `staging` and merge it with a merge commit (not squash). The review gate passes back-merges automatically.
3. Skip step 2 and the next release is blocked: `promotion_gate` requires staging to contain all of main.

## Rollback

1. Redeploy the previous `prod-*` tag from the hosting dashboard (fastest), or re-run its deploy.
2. Fix forward with a hotfix (above), or revert the release merge on `main` via a `hotfix/revert-…` PR.
3. Back-merge into staging. Note it in `docs/STATUS.md`.

## Merge permissions

| Actor | staging | main | Rules and settings |
|---|---|---|---|
| Implementer agent (GitHub App) | via auto-merge, when every check passes | ✗ blocked by ruleset | ✗ no admin |
| Reviewer agent | ✗ (reviews only) | ✗ | ✗ |
| Chris (admin) | ✓ (code-owner bypass for his own PRs) | ✓ the only one | ✓ |
| Renovate | via PR + checks + review | ✗ | ✗ |
