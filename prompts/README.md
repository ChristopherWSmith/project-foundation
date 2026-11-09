# Prompts

Part of the project foundation. Every prompt the product sends lives here, one file each, versioned. Never inline a prompt in code; load it by `id`.

## File format

```markdown
---
id: transaction-categorize
version: 3
role: executor            # model role from MODELS.md, not a model ID
owner: Chris
evals: evals/transaction-categorize.yaml
---

<the prompt; use {{variable}} placeholders>
```

## Rules

- **Any edit bumps `version`.** CI fails a changed prompt whose version didn't change.
- Re-run the prompt's evals on every version bump and on every model change; note the result in the PR.
- Traces carry `prompt_id` and `prompt_version`, so a regression points at the exact version.
- Untrusted content (user input, documents, emails) goes in clearly delimited variables, never concatenated into the instructions.
