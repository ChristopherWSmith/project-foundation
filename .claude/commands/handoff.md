---
description: Update docs/STATUS.md so the next session (human or agent) can pick up cold
---

Update `docs/STATUS.md` to reflect this session's work.

1. Check `git log` and `git status` since the date in STATUS.md's `last_reviewed`.
2. Update every section: current phase, in flight (with branch and PR), recently done (keep only the last 5), next up, blockers and open questions, known issues.
3. Set `last_reviewed` to today.
4. Keep it to about one screen. History belongs in git and CHANGELOG.md.
5. If this session changed something in AGENTS.md's "Keep the docs true" table and the doc wasn't updated, say so.
6. If something tripped you up that the next agent should know, add it to Gotchas in AGENTS.md.
