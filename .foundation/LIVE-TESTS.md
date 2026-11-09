# Live tests — run once on the first repo (Workbench), then after any change to rulesets or the review gate

Locally the scripts are verified by `scripts/checks/tests` against fixtures and a mock `gh`. These tests check what only GitHub can tell us. Record the result and date in the last column. Anything that fails gets fixed in the template or the rulesets before the next repo adopts v3.

**Setup:** repo started from the foundation (`scripts/init.py` with `--github-owner` and `--reviewer`), pushed, `scripts/github/apply-protection.py` run, and two GitHub Apps installed (implementer, reviewer) as in `.foundation/agents.json`. Use the implementer app's installation token for the agent steps (`GH_TOKEN=<installation token>`).

| # | Test | How | Expected | Result |
|---|---|---|---|---|
| 1 | Protection matches the standard | `scripts/github/verify-protection.py owner/repo` | All PASS | |
| 2 | Agent can't push to main | As implementer: `git push origin HEAD:main` | Rejected by ruleset | |
| 3 | Agent can't merge to main | As implementer: open PR staging→main, `gh pr merge --merge` | Refused ("restrict updates"); Chris can merge | |
| 4 | Agent can't change CI | As implementer: push a branch changing `.github/workflows/ci.yml` | Push rejected (no `workflows` permission) | |
| 5 | Agent can't loosen the gate | As implementer: PR changing `scripts/checks/review_gate.py` | Blocked: "Review required from code owners" | |
| 6 | Unreviewed PR waits | As implementer: open PR into staging, `gh pr merge --auto --squash` | `review-gate` failure; auto-merge waits | |
| 7 | Codex emits the contract | Let Codex review the PR | Review body ends with a valid `foundation-review` block. **If not:** have the orchestrator post the block from Codex's findings | |
| 8 | Open P1 blocks | Reviewer posts a review with an open P1 | `review-gate` red, "1 open blocking finding" | |
| 9 | New push resets the gate | Implementer pushes a fix | `review-gate` red: "earlier commits were reviewed; this one hasn't been" | |
| 10 | Re-review approves → auto-merge | Reviewer re-reviews the new head, P1 `resolved`, verdict approve | `review-gate` green; GitHub merges into staging by itself | |
| 11 | Forged status doesn't count | With your PAT: `gh api -X POST repos/o/r/statuses/<sha> -f state=success -f context=review-gate` on an unreviewed PR | Still blocked: the required check is pinned to GitHub Actions (15368) | |
| 12 | Reviewer independence | Reviewer app pushes a commit to the PR, then approves | `review-gate` red: "reviewer must not change the code it reviews" | |
| 13 | Bootstrap can't ship | PR staging→main while `stage` is bootstrap | `promotion_gate` red | |
| 14 | Feature branch can't ship | PR `feat/x`→main | `promotion_gate` red | |
| 15 | Missing tests fail CI | Set `stage: development`, gates set, no test files | `checks` red: "Mandatory tests are missing" | |
| 16 | Hotfix must be back-merged | Hotfix to main; then PR staging→main without back-merge | `promotion_gate` red until main is merged into staging | |
| 17 | Production secrets stay on main | Job with `environment: production` on a feature branch | Job refuses to run (branch policy) | |
| 18 | Release tag | Merge to main | `prod-YYYY-MM-DD-<sha>` tag pushed | |
| 19 | Supabase drift job | Repo with Supabase: change a migration without regenerating types | `supabase_drift` red | |
| 20 | Installations permissions | `verify-protection.py` agent section | Lists real permissions; no admin, workflows or statuses:write | |

If test 7 fails (Codex doesn't reliably emit the block), the gate stays closed: it fails safe. Use your orchestrator (Astra pipeline) to post the contract review. Don't loosen the gate.
