# The project foundation

One folder with every file a product repo needs: agent rules, docs, CI, quality and review gates, and branch protection. Copy it, run `scripts/init.py`, and the repo is set up. After that, each repo owns all of its files. There's no template engine and no update mechanism.

## Start a new repo

```bash
cp -r project-foundation my-app && cd my-app
python3 scripts/init.py "My App" --github-owner <your-github-username> --reviewer "<reviewer-bot-login>"
#   optional: --description "One sentence" --owner Chris
git remote add origin git@github.com:<you>/my-app.git
git push -u origin main staging
python3 scripts/github/apply-protection.py <you>/my-app --with supabase_drift
python3 scripts/github/verify-protection.py <you>/my-app --with supabase_drift
```

`init.py` fills in the `__PLACEHOLDER__` tokens, builds the brand CSS, and creates git with `main` (production) and `staging` (integration, checked out). It runs once; `.foundation/IS_TEMPLATE` marks a folder that hasn't been initialised. Without `--reviewer`, every PR into staging stays blocked until you set the reviewer login in `.foundation/review.json`.

## Add it to an existing repo

```bash
cp -rn project-foundation/. existing-repo/     # -n: never overwrite a file that's already there
cd existing-repo && python3 scripts/init.py "Existing" --github-owner <you> --reviewer "<bot>"
```

`init.py` leaves an existing git repo alone. Then move your old docs into the new structure in small PRs. Expect the checks to flag drift at first: that's useful.

## Every repo gets every file

Delete what a product will never need, e.g. `brand/`, `docs/growth/` and `docs/legal/` for an internal tool, or `supabase` bits without a database. Deleting a doc can make a rule in `.foundation/doc-triggers.txt` point at nothing, so remove that rule in the same PR.

## Changing a standard

Each repo owns its copy, so a standard changes per repo:

1. Create a ClickUp task: "Apply <change> to <repo>" (one per repo, or one listing several).
2. The coding agent opens the PR. Changes under `.github/`, `.foundation/`, `scripts/checks/`, `scripts/github/` and the agent rules need your approval as code owner, so an agent can't loosen its own gates.
3. If the change should apply to future repos too, make it here, in the foundation, as well.

When a check script changes, CI runs the foundation's own tests (`scripts/checks/tests/`) in that repo, so a broken check is caught before it judges anything.

## Stages

`.foundation/project.json` starts in **bootstrap**: unset quality gates are reported, not enforced, and nothing can be promoted to `main`. Once real code exists, set the gate commands and switch to **development**. From then on, every required gate must be a real command that passes, and test files must exist.

## What's here

| Path | What |
|---|---|
| `project.json` | Stage and quality-gate commands |
| `review.json` | Reviewer logins, human approvers, blocking severities (read from the base branch by the review gate) |
| `agents.json` | Agent GitHub Apps and permissions they must not have (checked by `verify-protection.py`) |
| `schemas/` | `foundation-review` and `foundation-handoff` contracts |
| `doc-triggers.txt` | Which code changes require which doc updates |
| `hygiene.json` | Ticket-ID format, scanned paths, limits |
| `LIVE-TESTS.md` | What only GitHub can prove; run once on the first repo |
| `VERSION` | Which foundation version this repo started from |

## Testing the foundation

```bash
python3 -m unittest discover -s scripts/checks/tests -v
```

About 30 seconds. Covers init, every gate's pass and fail paths, the implement → review → fix → re-review → release loop, and apply/verify protection against a mock GitHub. The tests work on a copy, so they run the same in the foundation folder and in any product repo.

The foundation repo itself skips the product workflows (its name is `project-foundation`). Keep that name, or change the `github.event.repository.name` guard in `.github/workflows/`.
