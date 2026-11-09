---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# Local setup — __PROJECT_NAME__

Goal: from a fresh clone to a running app in under 15 minutes. If it takes longer, fix this guide.

## Prerequisites

- [mise](https://mise.jdx.dev): installs the pinned toolchain from `mise.toml`
- Infisical CLI, signed in
- Docker (for local Supabase)

## Steps

```bash
git clone <repo-url> && cd __PROJECT_SLUG__
mise install
pnpm install
infisical export --env=dev --path=/products/__PROJECT_SLUG__ > .env
pnpm supabase start
# start the dev server (see AGENTS.md → Commands)
./scripts/check-all.sh
```

## Verify

- Open:
- Expect:

## Common problems

| Symptom | Fix |
|---|---|
| | |
