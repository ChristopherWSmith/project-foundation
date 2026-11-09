# Agent workflow

Part of the project foundation. Who does what, how work moves between agents, and what is enforced by the platform versus only asked for. Models per role: `MODELS.md`. Identities and permissions: `AGENT-PERMISSIONS.md`.

## The loop

```
ClickUp task → plan (planner) → plan review (reviewer) → Chris approves the plan
  → implementer: branch, code, /done → PR into staging with foundation-handoff block, auto-merge on
  → CI: checks, security_staging, drift (incl. handoff + doc triggers)
  → reviewer reviews the head commit → foundation-review block
      ├─ open P0/P1 → review-gate fails → implementer fixes → new push → gate resets → re-review
      └─ approve, nothing blocking → review-gate passes → GitHub auto-merges into staging
  → staging → main: Chris merges the promotion PR (only admins can) → production
```

## What enforces each step

| Rule | Enforced by | Where |
|---|---|---|
| Quality gates are real and pass | `checks` required check | `quality_gates.py`, `.foundation/project.json` |
| Handoff present, valid, honest | `drift` required check | `check_handoff.py`, handoff schema |
| Docs change meaningfully with the code | `drift` required check | `doc_triggers.py` |
| Independent review of the current commit, no open P0/P1 | `review-gate` required status (staging) | `review_gate.py`, review schema |
| Reviewer ≠ implementer; reviewer didn't push code | `review-gate` | `review_gate.py` |
| Gates and agent rules can't be changed by an agent alone | Code-owner review (staging) + agents lack the `workflows` permission | `CODEOWNERS`, ruleset |
| Only staging / hotfix reach main; never in bootstrap | `promotion_gate` required check (main) | `promotion_gate.py` |
| Only Chris merges to main | Ruleset "restrict updates" with admin-only bypass | `.github/rulesets/` |
| Production secrets only usable from main | `production` environment, branch policy `main` | `scripts/github/apply-protection.py` |

Everything else in this doc is convention. The reviewer checks it, and nothing blocks on it by machine.

## Contracts

| From → to | Carrier | Schema |
|---|---|---|
| Implementer → reviewer | PR description, `foundation-handoff` block | `.foundation/schemas/handoff.schema.json` |
| Reviewer → gate and implementer | PR review body, `foundation-review` block | `.foundation/schemas/review.schema.json` |
| Planner ↔ reviewer | `docs/plans/<plan>.md` review log | (prose) |
| Session → next session | `docs/STATUS.md` (`/handoff`) | (prose) |

Severities: **P0** critical, **P1** high (both block), **P2** should fix, **P3** nit. A reviewer can mark a P2/P3 `accepted_risk`. A P0/P1 can only be resolved, or overridden by Chris with an approving review containing `foundation-override: <reason>`.

## Escalate to Chris (stop, don't guess) when

- Requirements conflict, or the plan doesn't match what the code shows.
- A secret, a permission, a paid service or a production action is needed.
- The change is irreversible (data deletion, destructive migration, public API break).
- The same finding survives two fix-and-review rounds; the loop isn't converging.
- A check fails and you can't tell why after one honest attempt.

Escalate through the approval channel (Telegram), not by leaving a note somewhere.
