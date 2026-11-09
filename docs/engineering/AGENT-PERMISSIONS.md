# Agent permissions

Part of the project foundation. Instructions ask agents to behave; this doc defines what they **can't** do even if they misbehave. The identities are recorded in `.foundation/agents.json`, and `scripts/github/verify-protection.py` checks the live settings against it.

## Identities: one per role, never Chris's

| Role | Identity | Why its own |
|---|---|---|
| Implementer (Claude Code, Codex tasks) | GitHub App "implementer" (installation token) | Not an admin, so it can't bypass rulesets; can't approve its own work |
| Reviewer (Codex / "Astra") | A different GitHub App or bot account | The review gate rejects reviews from the PR author and from anyone who pushed to the PR |
| Orchestrator (n8n / Inngest) | Its own app, or the implementer's | Moves tickets, opens PRs; same limits as the implementer |
| Chris | Personal account (admin) | The only identity that merges to `main` or changes settings |

**Never give an agent your personal token**, a classic PAT, or a fine-grained PAT on your account. Rulesets judge the *user*: anything acting as you inherits your admin bypass.

## GitHub permissions per identity

| Permission | Implementer | Reviewer | Why |
|---|---|---|---|
| Contents | write | read (write only if it must run `@codex fix`, and then it can't review that PR) | Push branches |
| Pull requests | write | write | Open PRs / post reviews |
| Workflows | **none** | **none** | Can't change CI, so it can't change what judges it |
| Administration | **none** | **none** | Can't change rulesets, settings or environments |
| Secrets, Environments | **none** | **none** | Can't read or retarget deploy credentials |
| Commit statuses / Checks | none | none | Can't post a fake `review-gate`; required checks are pinned to GitHub Actions |

## Credential boundaries (Infisical)

| Identity | Can read | Can't read |
|---|---|---|
| Implementer | `/agents/implementer/*`, `/products/<slug>/dev` | `/products/<slug>/staging`, `/products/<slug>/prod` |
| Reviewer | nothing it doesn't need to review | any product secrets |
| CI (staging deploy) | `/products/<slug>/staging` via the `staging` environment | prod |
| CI (production deploy) | `/products/<slug>/prod` via the `production` environment (only `main` can use it) | — |

Each agent gets its own Infisical machine identity, scoped to the paths above. Production credentials exist in exactly two places: Infisical `prod` and the GitHub `production` environment.

## Isolated workspaces

- One task = one git worktree (or container) on its own branch: `git worktree add ../<repo>-<ticket> -b feat/<ticket>-<slug> origin/staging`.
- Agents work only inside that worktree. Never in your home directory, never in another repo's checkout.
- Worktrees are deleted when the PR merges or closes.
- Agents running on the M5 or the Acer run as a non-admin OS user without access to your SSH keys or browser profiles.

## What a misbehaving agent still can't do

| Attempt | Blocked by |
|---|---|
| Merge its own unreviewed PR | `review-gate` required status; reviewer must be a different identity |
| Approve itself, or have the reviewer push the fix | Review gate independence rules |
| Edit the gate script, review config or CI to pass | Code-owner approval on those paths; no `workflows` permission; gate runs from the base commit |
| Post a fake success status | Required checks pinned to the GitHub Actions app (integration 15368) |
| Merge or push to `main` / deploy production | Ruleset "restrict updates" (admin-only); `production` environment branch policy |
| Read production secrets | Infisical scopes; environment secrets |
