---
status: draft
lifecycle: reference
last_reviewed: __DATE__
---

# Recovery objectives — __PROJECT_NAME__

**RTO**: how long it may be down. **RPO**: how much recent data it may lose. Each number must be backed by a mechanism, and that mechanism must be tested (restore drill).

| Component | RTO | RPO | Mechanism | Last tested |
|---|---|---|---|---|
| Application | [1 h] | n/a | redeploy previous `prod-*` tag | |
| Database | [4 h] | [24 h → PITR: minutes] | provider backups / point-in-time recovery | |
| File storage | | | | |
| Secrets (Infisical) | | | Infisical backup / export | |

If a drill misses a target, either fix the mechanism or change the target here. Then tell users the honest number (status page, terms).
