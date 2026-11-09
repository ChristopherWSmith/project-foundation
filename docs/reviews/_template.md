---
status: draft
lifecycle: reference
last_reviewed: YYYY-MM-DD
type: holistic   # holistic | appsec | invariants | tenant-isolation | ai-red-team | ux
---

# Review brief: <name>

A reusable brief to hand a reviewer (human or agent). Copy it per review type, e.g. `appsec.md`, `tenant-isolation.md`.

## Scope

<!-- What's being reviewed: the whole repo, a PR, a feature, a flow. -->

## Read first

- `docs/architecture/ARCHITECTURE.md` → Constraints and invariants
- `docs/architecture/SECURITY.md`
-

## Invariants that must hold

-

## Check

-

## Adversarial probes

<!-- Specific attacks to try, e.g. "a user in tenant A requests tenant B's record by ID". -->

-

## Output

Findings in the format from `docs/engineering/AGENT-WORKFLOW.md`, most severe first. Report only; don't change code.
