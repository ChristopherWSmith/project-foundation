# MODELS.md — model routing for __PROJECT_NAME__

Roles stay stable; swap the model names as new ones ship.

## Building this repo

| Role | Does | Model(s) |
|---|---|---|
| Planner / architect | Plans in `docs/plans/`, architecture reviews, ADRs | Claude Opus / Fable |
| Executor | Implements approved plan phases | Claude Sonnet / Codex |
| Reviewer | Reviews plans and every PR before merge | Codex ("Astra") |
| Boilerplate | Scaffolding, renames, fixtures, doc formatting | Claude Haiku |

The escalation and handoff rules are in `docs/engineering/AGENT-WORKFLOW.md`.

## Inside the product

| Feature | Prompt id | Model | Why this model | Fallback | Cost ceiling |
|---|---|---|---|---|---|
| | | | | | |

- Model IDs live in config, never in code. Changing one means bumping the prompt version and running the evals.
- Each call is traced (Langfuse) with `feature`, `prompt_id`, `prompt_version` and `model` metadata.
- Check the provider deprecation pages quarterly; record any retirement date in the table above.
