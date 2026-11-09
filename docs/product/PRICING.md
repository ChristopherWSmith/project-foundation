---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# Pricing — __PROJECT_NAME__

**Source of truth: `config/entitlements.json`.** The code enforces limits from it, the pricing page renders from it, and Stripe products map to it by lookup key. This doc explains the reasoning; it never restates the numbers, so it can't drift from them.

## Model

<!-- Free / trial / paid tiers, per seat or flat, annual discount. And why. -->

## Plans

| Plan id | Who it's for | Upgrade trigger |
|---|---|---|
| free | | |
| pro | | |

## Stripe mapping

| Plan id | Stripe lookup key (monthly) | Stripe lookup key (annual) |
|---|---|---|
| | | |

## Rules

- Changing a limit or a price is a `config/entitlements.json` change plus a CHANGELOG entry. CI requires this doc to change too, so the reasoning gets updated.
- Existing customers: grandfathered or migrated? Decide per change and record it in an ADR.
