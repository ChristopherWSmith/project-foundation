# Docs map — __PROJECT_NAME__

Every doc has one job. Delete the ones this product will never need (and their rules in `.foundation/doc-triggers.txt`).

| Path | Job | Lifecycle |
|---|---|---|
| `STATUS.md` | Where things stand right now | living (14 days) |
| `product/VISION.md` | Problem, users, non-goals, success | reference |
| `product/FEATURES.md` | Every capability and its state | living |
| `product/GLOSSARY.md` | One name per concept | reference |
| `product/VOICE.md` | How the product sounds | reference |
| `product/PRICING.md` | Plans and limits, explained (source: `config/entitlements.json`) | living |
| `product/ACCEPTANCE.md` | Release acceptance scenarios | living |
| `architecture/ARCHITECTURE.md` | Components, flows, integrations, invariants | living |
| `architecture/SCHEMA.md` | Data model, RLS, migration rules | living |
| `architecture/SECURITY.md` | Auth, isolation, secrets inventory, AI risks | living |
| `architecture/CONVENTIONS.md` | Data, errors, logging, flags, API shape | living |
| `architecture/THREAT-MODEL.md` | Assets, boundaries, threats, mitigations | living |
| `architecture/COMPATIBILITY.md` | Supported clients, versioning, deprecation | reference |
| `architecture/PERFORMANCE.md` | Performance budgets | living |
| `architecture/integrations/` | One spec per external service | living |
| `engineering/DEFINITION-OF-DONE.md` | What "done" means | foundation doc |
| `engineering/AGENT-WORKFLOW.md` | The loop, contracts, what's enforced | foundation doc |
| `engineering/AGENT-PERMISSIONS.md` | Identities, permissions, credential boundaries | foundation doc |
| `engineering/BRANCHING-AND-RELEASES.md` | Branches, releases, hotfix, rollback, merge rights | foundation doc |
| `engineering/TESTING.md` | Test layers and critical journeys | living |
| `engineering/local-setup.md` | Fresh clone → running app | living |
| `decisions/` | ADRs: why X over Y | record |
| `plans/` | Plans approved before code | record |
| `operations/` | Deploy, restore, domains, accounts, incidents, recovery objectives | living / reference |
| `growth/` | SEO, tracking plan and metrics, support | living |
| `legal/` | Policies, subprocessors, data retention | living |
| `reviews/` | Review briefs and the security checklist | foundation doc |
| `archive/` | Superseded docs and finished plans | — |

## Outside docs/

- `AGENTS.md`: agent rules and the reviewer's guidelines
- `MODELS.md`: which model does which job
- `.foundation/`: stage and quality gates, review config, contracts, check config (see its README)
- `brand/`: logo files and `tokens.json`, the only source of colors, type and spacing
- `config/entitlements.json`: plans and limits, read by both the code and the pricing page
- `prompts/` and `evals/`: versioned prompts and the evals that guard them

## Conventions

- **Frontmatter on every doc:** `status`, `lifecycle` and `last_reviewed` (or `date` for records).
  - `living` docs describe the system now. CI warns after 90 days without review (`review_every_days` overrides).
  - `reference` docs change rarely: warned after 365 days.
  - `record` docs (ADRs, plans, logs) never go stale.
  - Foundation docs ("Part of the project foundation"), READMEs and `_templates` carry no frontmatter.
- **Changing a doc means changing its content.** Bumping `last_reviewed` doesn't satisfy a doc trigger.
- **File names:** canonical docs `UPPERCASE.md`; dated or numbered docs `kebab-case`.
- **Generate, don't hand-copy:** types, env lists and token CSS are generated. Hand-write only the *why*.
- **Never delete history:** move superseded docs to `archive/` and mark them `superseded`.
- **Tasks live in ClickUp**, not here. Code is the truth: when a doc and the code disagree, fix the doc in the same PR.
