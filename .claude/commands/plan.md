---
description: Write an implementation plan in docs/plans/ for review before any code is written
argument-hint: <what to build, or a ClickUp task ID>
---

Write an implementation plan for: $ARGUMENTS

1. Read `docs/STATUS.md`, `docs/architecture/ARCHITECTURE.md`, `docs/architecture/CONVENTIONS.md`, `docs/architecture/SCHEMA.md` (if it exists), and any related ADRs or plans.
2. Copy `docs/plans/_template.md` to `docs/plans/YYYY-MM-DD-<slug>.md` using today's date.
3. Fill in every section. Each phase is one reviewable PR with its own acceptance criteria and the docs it will update.
4. Name the golden path each phase follows (from AGENTS.md). If there isn't one, say so and propose it.
5. List open questions honestly instead of guessing at answers.
6. Set `status: draft`. Write no application code.
7. Reply with the plan's path, a few-line summary, and the open questions.
