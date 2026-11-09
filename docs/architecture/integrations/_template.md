---
status: draft
lifecycle: living
last_reviewed: YYYY-MM-DD
---

# Integration: <service>

**Used for:** · **Owner:** · **Docs:** <vendor API docs URL> · **API version pinned:**

## Data flow

| Direction | What | When | Contains personal data? |
|---|---|---|---|
| Out | | | |
| In (webhook) | | | |

## Auth and secrets

- Credential: (Infisical path, never the value) · Scope: · Rotation:

## Failure behaviour

| Failure | What the user sees | What we do (retry, queue, alert) |
|---|---|---|
| Timeout / 5xx | | |
| Rate limited | | |
| Webhook missed or duplicated | | idempotent handler keyed on event id |

## Limits and costs

- Rate limits: · Pricing that scales with usage:

## Testing

- Sandbox / test mode: · Fixtures: · Contract test:
