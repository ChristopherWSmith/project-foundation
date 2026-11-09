# Definition of Done

Part of the project foundation. Applies to every change, whoever makes it. `/done` walks through it.

## Always

- [ ] The acceptance criteria in the ticket or plan phase are met.
- [ ] The quality gates (`python3 scripts/checks/quality_gates.py`) and `./scripts/check-all.sh` were **run** and pass. Anything not run is `not_run` in the handoff, with the reason.
- [ ] New behaviour has a test; a bug fix has a regression test.
- [ ] Docs updated per AGENTS.md → "Keep the docs true".
- [ ] No secrets, real customer data or production logs committed.
- [ ] No new dependency without a stated reason.
- [ ] Follows a golden path, or the PR says why not.
- [ ] The PR description has a valid `foundation-handoff` block.
- [ ] An independent review of the final commit has no open P0/P1 findings (`review-gate`). High-risk changes also get Chris's eyes.

## When it applies

- [ ] **Schema:** migration is new (never an edited one); types regenerated; RLS on new tables; SCHEMA.md updated.
- [ ] **Auth, permissions, money, or personal data:** security checklist (`docs/reviews/security-checklist.md`) done; human approval.
- [ ] **UI:** uses brand tokens (no raw hex); copy follows VOICE.md; loading, empty and error states exist; keyboard and screen-reader basics work.
- [ ] **New or changed analytics event:** added to `docs/growth/TRACKING.md`; name follows the portfolio convention.
- [ ] **New vendor receiving user data:** `docs/legal/SUBPROCESSORS.md` and SECURITY.md updated.
- [ ] **Pricing or limits:** `config/entitlements.json` + PRICING.md + CHANGELOG.
- [ ] **Prompt or model change:** prompt `version` bumped; evals run and results noted in the PR.
- [ ] **New env var:** in `.env.example` and the env schema; set in Infisical for staging and production.
- [ ] **New feature flag:** in the flag register with an owner and a removal date.
- [ ] **User-visible change:** CHANGELOG entry; help docs updated if they describe it.
- [ ] **Deploy impact:** migration order, flags and rollback written in the PR.

Merged to `staging` is done for an agent. Promotion to production is Chris's decision, and only Chris can merge to `main`.
