---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# Runbook: Restore from backup

A backup you've never restored is a guess. Run this as a drill quarterly, against a scratch project, never against production.

**Access needed:** Supabase dashboard (project owner), Infisical.

## Where backups are

- Automatic:
- Retention:
- Point-in-time recovery: yes / no

## Drill steps

1. Create a scratch database or project.
2. Restore the latest backup into it.
3. Point a local app at it (`DATABASE_URL` from the scratch project).
4. Verify: row counts on the key tables, sign in as a test user, open a recent record.
5. Time the whole thing. That's your real recovery time.
6. Delete the scratch project.

## Drill log

| Date | Backup used | Time to restore | Problems | By |
|---|---|---|---|---|
| | | | | |
