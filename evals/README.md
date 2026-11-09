# Evals

Part of the project foundation. A small, honest test set for each prompt: the cases that matter, the ones that broke before, and the attacks from the AI red-team review.

- One config per prompt, named after its `id`. The example uses [promptfoo](https://www.promptfoo.dev); any runner is fine as long as it's committed and repeatable.
- Run: `npx promptfoo eval -c evals/<id>.yaml`
- Start with 10–20 cases. Every production bug or red-team finding becomes a new case.
- Results go in the PR (pass rate before and after). Output files are gitignored.
