---
description: Check the branch against the Definition of Done and write the PR description with a valid handoff block
---

Check this branch against `docs/engineering/DEFINITION-OF-DONE.md` before a PR is opened.

1. Run `./scripts/check-all.sh` and `python3 scripts/checks/quality_gates.py`. Record each command and its **real** result: `pass`, `fail`, or `not_run` with a reason. Never write `pass` for something you didn't run.
2. Diff against `staging`. For every changed area, check AGENTS.md → "Keep the docs true", and confirm the matching doc changed meaningfully (a date bump doesn't count).
3. Go through the Definition of Done line by line: met, not met, or n/a, each with a one-line reason.
4. Write the PR description from `.github/pull_request_template.md`. The `foundation-handoff` block must validate against `.foundation/schemas/handoff.schema.json`. Check it with:
   `PR_AUTHOR=<your-login>[bot] python3 scripts/checks/check_handoff.py --body-file <description.md>`
5. If any command failed or anything is not met, list what's left and stop. Don't open the PR.
6. Otherwise open the PR into `staging` and turn on auto-merge: `gh pr merge --auto --squash`.
