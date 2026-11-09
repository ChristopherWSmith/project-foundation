---
status: accepted
date: __DATE__
deciders: __OWNER__
---

# 0001. Record architecture decisions as ADRs

## Context

Several agents and sessions work on this repo, and none of them remember earlier conversations. Without a written record, settled choices get reopened, and agents "fix" deliberate decisions they don't understand.

## Options considered

### A. A single DECISIONS.md
- Pros: one file to read.
- Cons: merge conflicts, grows without limit, history gets edited in place.

### B. One numbered file per decision
- Pros: append-only, easy to link, supersession is explicit.
- Cons: more files.

## Decision

We will record significant decisions as numbered ADRs in `docs/decisions/`, indexed in its README.

## Consequences

- Good: agents can check why something is the way it is before changing it.
- Bad / costs: a few minutes per decision.
- Revisit if: never; this is the meta-decision.
