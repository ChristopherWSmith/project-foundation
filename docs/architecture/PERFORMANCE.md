---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# Performance budgets — __PROJECT_NAME__

Budgets are numbers that fail a check, not aspirations. Add each to CI as it becomes measurable (Lighthouse CI, bundle-size checks, load tests).

| Budget | Target | Measured by | Enforced in CI |
|---|---|---|---|
| Largest Contentful Paint (key pages, mobile) | ≤ 2.5 s | Lighthouse | |
| Interaction to Next Paint | ≤ 200 ms | Lighthouse / RUM | |
| JS shipped on first load | ≤ [200] KB gzipped | bundle analyzer | |
| API p95 latency (core endpoints) | ≤ [300] ms | logs / APM | |
| DB queries per request (core endpoints) | ≤ [10] | query log in tests | |
| AI response time (p95) | ≤ [8] s | Langfuse | |
| AI cost per active user / month | ≤ $[x] | Langfuse | |

## When a budget is blown

Fix it or raise it in this file, with a reason, in the same PR. Never silently.
