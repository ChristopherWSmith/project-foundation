---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# Conventions — __PROJECT_NAME__

The small rules that, when they drift, cause real bugs. Enforce with types and lint wherever possible; prose is the fallback.

## Data

| Thing | Rule |
|---|---|
| Money | Integer minor units (cents) + ISO 4217 currency code. Never floats. One `Money` type. |
| Time | Store UTC (`timestamptz`). ISO 8601 at API boundaries. Convert to the user's time zone only for display. |
| Dates without time | `date` type / `YYYY-MM-DD` string. Never a midnight timestamp. |
| IDs | UUID (v7 preferred). Never expose sequential IDs publicly. |
| Percentages | Store as basis points or a decimal fraction. Say which. |
| Names in code | `camelCase` in TS, `snake_case` in DB and JSON APIs (or say otherwise here). |

## Errors

| Kind | HTTP | User sees | Logged as |
|---|---|---|---|
| validation | 400 | What to fix | info |
| unauthenticated | 401 | Sign in again | info |
| forbidden | 403 | You don't have access | warn |
| not_found | 404 | Couldn't find it | info |
| conflict | 409 | Someone changed this; reload | info |
| rate_limited | 429 | Slow down; try again shortly | warn |
| internal | 500 | Our fault, your data is safe (VOICE.md) | error + alert |

Error responses use one shape: `{ "error": { "code": "...", "message": "...", "request_id": "..." } }`.

## Logging and tracing

- One logger, structured JSON. No `console.log` in committed code paths.
- Every log line carries `request_id`, plus `tenant_id` and `user_id` where known.
- **Never log:** secrets, tokens, passwords, full card or account numbers, raw request bodies with personal data. Redact at the logger.
- AI calls are traced with `feature`, `prompt_id`, `prompt_version`, `model`, tokens and cost.

## Feature flags

Every flag has an owner and an expiry. Expired flags are removed, not left on.

| Flag | Purpose | Owner | Created | Remove by | State |
|---|---|---|---|---|---|
| | | | | | |

## TODOs and shortcuts

`TODO(<ticket-id>): …` only; CI rejects a TODO without a ticket. Skipped tests need a ticket on the same or previous line.

## API shape

- Pagination: cursor-based, `?cursor=&limit=` (max 100)
- Idempotency: write endpoints that can be retried accept `Idempotency-Key`
- Versioning:
