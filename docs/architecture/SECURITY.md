---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# Security — __PROJECT_NAME__

## What we protect

| Data | Sensitivity | Where it lives |
|---|---|---|
| | | |

## Authentication

<!-- Provider, session handling, MFA, service-to-service auth. -->

## Authorization and tenant isolation

<!-- How access is decided, where it's enforced (RLS, middleware), and how cross-tenant access is tested. -->

## Secrets inventory (names only, never values)

Infisical paths: `/products/__PROJECT_SLUG__/<env>`, `/agents/`, `/mcp/`.

| Secret | Scope / permissions | Used by | Rotation | Last rotated |
|---|---|---|---|---|
| | | | | |

Rotating a secret means updating it in Infisical **and** every place it's synced (hosting, CI). Record the date here.

## Agent and automation access

| Agent / token | Can read | Can write | Can't |
|---|---|---|---|
| Coding agent | repo | branches, PRs to `staging` | `main`, production, secrets |
| | | | |

## AI-specific risks

- **Prompt injection:** untrusted content that reaches a model is treated as data, never as instructions.
- **Tool permissions:** each AI feature gets only the tools it needs.
- **Approval gates:** actions that need a human yes before they run.
- **Data sent to providers:** (also in `docs/legal/SUBPROCESSORS.md`)

## External integrations (security view)

<!-- Mirrors ARCHITECTURE.md → External integrations. CI requires this file to change when that section does. -->

| Service | Credential | Least-privilege scope | Data exposure |
|---|---|---|---|
| | | | |

## Dependencies

Audits run in CI (`security_staging`). High or critical findings block merges into `staging`. Renovate opens weekly update PRs.

## Accepted risks

-
