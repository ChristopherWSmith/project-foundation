---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# Tracking plan — __PROJECT_NAME__

Convention, the same in every product: `object_action` in snake_case, past tense (`account_created`, `budget_shared`). Object first, so related events sort together. Variants go in properties (`export_format: "csv"`), not new event names. The core events below keep the same names in every product, so funnels compare across the portfolio. Every event also carries `product`, `app_version`, `tenant_id` (pseudonymous), `plan` and `platform`.

Events are sent only through the typed `track()` helper, which accepts only the names in this table. Never call the analytics SDK directly.

- Tool:
- Consent: events wait for consent where the law requires it

## Events

| Event | Fires when | Properties | Core? | Added |
|---|---|---|---|---|
| `account_created` | Sign-up completes | `method` | yes | |
| `activated` | User reaches the activation moment (defined in METRICS.md) | | yes | |
| `subscription_started` | First successful payment | `plan`, `interval` | yes | |
| `subscription_cancelled` | Cancellation confirmed | `plan`, `reason` | yes | |
| | | | | |

## Activation for this product

<!-- The specific action that means "got value", e.g. first account connected and categorized. -->

## Metric definitions (same in every product)

| Metric | Definition |
|---|---|
| Activation rate | Share of new accounts that fire `activated` within 7 days of `account_created` |
| Active user | Did a core action in the period; always say daily, weekly or monthly |
| Retention (week N) | Share of a sign-up week's cohort active in week N |
| Trial conversion | Share of `trial_started` reaching `subscription_started` within the trial |
| MRR | Active subscriptions normalized to monthly (annual ÷ 12), no one-off charges |
| Logo churn | Subscriptions cancelled in the month ÷ subscriptions at the start of the month |

Count tenants, not seats, unless the metric says "users". Exclude internal and test accounts.

## Never send

Names, emails, free text the user typed, amounts tied to identity, anything from the "never log" list in CONVENTIONS.md.
