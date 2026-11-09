# Plans

A plan is written, reviewed and approved before code. It's the contract between the planner, the executor and the reviewer (`docs/engineering/AGENT-WORKFLOW.md`).

**Lifecycle:** `draft` → `approved` → `in-progress` → `done` → moved to `docs/archive/plans/`

**Naming:** `YYYY-MM-DD-<slug>.md`, e.g. `2026-11-07-stripe-billing.md`

**Rules**
- Each phase is one PR, with its own acceptance criteria and the docs it will touch.
- The executor follows the approved plan. If reality disagrees with the plan, stop and update the plan instead of improvising.
- Reviewer feedback goes in the plan's review log, so the reasoning stays with the plan.

Create one with `/plan <what to build>`, or copy `_template.md`.
