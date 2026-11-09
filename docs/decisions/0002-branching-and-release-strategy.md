---
status: accepted
date: __DATE__
deciders: __OWNER__
---

# 0002. Two long-lived branches: staging (default, integration) and main (production)

## Context

Agents open most PRs and merge without a human in the loop. Production must only change on a human decision. The portfolio's coding agent already targets `staging`.

## Options considered

### A. Trunk-based: `main` integration, production = release tags
- Pros: one long-lived branch, no back-merges.
- Cons: agents' default target is the production line. A release tag is easy to cut from the wrong commit. Production approval becomes "who may push tags", which is weaker on personal accounts.

### B. `staging` (default) + `main` (production), promotion by PR
- Pros: every default (PRs, agents, Renovate) lands on integration. Production changes only by an admin-merged PR, enforceable with rulesets. Matches the existing agent setup.
- Cons: hotfixes need a back-merge. Squash on promotion would break ancestry.

## Decision

We use B. Feature PRs squash into `staging`. Promotions and back-merges use merge commits. `promotion_gate` blocks a release while staging lacks main's commits. Only admins merge to `main`. Details: `docs/engineering/BRANCHING-AND-RELEASES.md`.

## Consequences

- Good: an agent can't reach production through any default or any permission it holds.
- Bad / costs: back-merges after hotfixes; two branches to keep protected.
- Revisit if: a second human joins (production approval can then be a required reviewer), or releases become frequent enough for a merge queue.
