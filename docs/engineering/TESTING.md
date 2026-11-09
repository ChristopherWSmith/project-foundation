---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# Testing — __PROJECT_NAME__

## Layers

| Layer | Covers | Command | Required in CI |
|---|---|---|---|
| Unit | Pure logic, edge cases | | yes |
| Integration | DB, API and service boundaries | | yes |
| End-to-end | The critical journeys below | | before production |
| Security | Authz, tenant isolation, input abuse | | yes, for auth changes |
| AI evals | Prompt quality and regressions | `evals/` | when prompts or models change |

## Critical journeys

Each one must have an end-to-end or integration test. If it isn't tested, it's not on this list yet; it's a gap.

| Journey | Test | Status |
|---|---|---|
| Sign up → first value | | gap |
| | | |

## Test data

- Fixtures and factories live in:
- Never real personal or financial data. Generate it.
- Tests clean up after themselves, or run in a transaction.

## Rules

- A bug fix gets a regression test that fails before the fix.
- Flaky tests get fixed or skipped **with a ticket** (CI enforces the ticket).
- No `.only` committed (CI enforces).
