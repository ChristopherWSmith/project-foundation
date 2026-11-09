---
description: Record an architecture decision as a new ADR in docs/decisions/
argument-hint: <the decision, e.g. "use Inngest for background jobs">
---

Record this decision as an ADR: $ARGUMENTS

1. List `docs/decisions/` and take the next number (4 digits, zero-padded).
2. Copy `docs/decisions/0000-template.md` to `docs/decisions/NNNN-<slug>.md`.
3. Fill in the context, the options actually considered (at least two, with real trade-offs), the decision, and its consequences, good and bad.
4. If it replaces an earlier ADR, set the old one to `status: superseded by NNNN` and link both ways. Never rewrite an accepted ADR's decision.
5. Add a row to the index in `docs/decisions/README.md`.
6. Leave `status: proposed` unless I said it's already decided.
