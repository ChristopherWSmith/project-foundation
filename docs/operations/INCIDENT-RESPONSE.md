---
status: draft
lifecycle: reference
last_reviewed: __DATE__
---

# Incident response — __PROJECT_NAME__

## Severity

| Sev | Means | Respond within |
|---|---|---|
| 1 | Production down, data loss or leak, money wrong | immediately |
| 2 | Major feature broken for many users | same day |
| 3 | Degraded, workaround exists | next work session |

## Steps

1. **Contain** with the least destructive reversible action: roll back to the previous `prod-*` tag, turn off a flag, revoke a key.
2. **Stop agents** touching the affected repo (pause the orchestrator) until it's understood.
3. **Assess** who's affected and whether data was exposed. A leak of personal data may have notification deadlines (`docs/legal/`).
4. **Fix** via a `hotfix/*` PR; back-merge into staging.
5. **Write it up** within a few days: timeline, cause, what stopped it, what changes. The fix for "how did this get through" usually belongs in a check, an AGENTS.md rule, or the template.

## Contacts and access

| Need | Where |
|---|---|
| Hosting status / rollback | |
| Database backups | `docs/operations/restore.md` |
| Revoke credentials | Infisical + the vendor dashboard |

## Incident log

| Date | Sev | Summary | Write-up |
|---|---|---|---|
| | | | |
