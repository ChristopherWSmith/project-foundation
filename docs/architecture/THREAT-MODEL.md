---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# Threat model — __PROJECT_NAME__

Update when a trust boundary, an integration or a kind of data changes. The security checklist and the AI red-team brief test against this.

## Assets

| Asset | Why someone wants it | Impact if lost / leaked / altered |
|---|---|---|
| | | |

## Trust boundaries and entry points

| Boundary | Entry points | Who's on the other side |
|---|---|---|
| Browser ↔ API | | anonymous / authenticated users |
| API ↔ database | | |
| API ↔ third parties | webhooks, callbacks | vendors |
| App ↔ LLM | prompts, tool calls, retrieved content | model + any content it reads |

## Threats (STRIDE as a prompt, not a ritual)

| ID | Threat | Boundary | Likelihood | Impact | Mitigation | Verified by |
|---|---|---|---|---|---|---|
| T1 | Tenant A reads tenant B's data | API ↔ DB | | high | RLS + tenant-scoped queries | cross-tenant test |
| T2 | | | | | | |

## Accepted risks

| Risk | Why accepted | Revisit |
|---|---|---|
| | | |
