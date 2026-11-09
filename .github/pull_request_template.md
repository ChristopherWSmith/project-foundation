<!-- The block below is the machine-checked handoff (schema: .foundation/schemas/handoff.schema.json). CI rejects agent
PRs without it, with a "fail" result in it, or with an unexplained "not_run". Record only what you actually ran. -->

## What and why

<!-- Two or three sentences for a human. -->

```foundation-handoff
{
  "schema": "foundation-handoff/v1",
  "task": "CU-xxxx",
  "plan": null,
  "implementer": "",
  "summary": "",
  "commands": [
    { "cmd": "./scripts/check-all.sh", "result": "not_run", "note": "replace with the real result" },
    { "cmd": "python3 scripts/checks/quality_gates.py", "result": "not_run", "note": "replace with the real result" }
  ],
  "docs_updated": [],
  "risks": [],
  "open_questions": [],
  "next_action": "independent review"
}
```

## Risk and rollback

- Risk: low / medium / high
- Migration or flag needed:
- Rollback:

<!-- Docs exception? Label the PR docs-not-needed and add a line:  Docs-Not-Needed: <why, 20+ chars>
     The reviewer must accept it (docs_exception: "accepted") or the review gate stays closed. -->
