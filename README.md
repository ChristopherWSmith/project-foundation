<!-- foundation:template-note -->
> **This is the project foundation.** To start a product from it, see [.foundation/README.md](.foundation/README.md). `scripts/init.py` removes this note.
<!-- /foundation:template-note -->
# __PROJECT_NAME__

__DESCRIPTION__

## Quickstart

```bash
mise install            # pinned runtimes (see mise.toml)
pnpm install
cp .env.example .env    # values come from Infisical
# start the app — see docs/engineering/local-setup.md
```

## Where things are

- **What and why:** [docs/product/VISION.md](docs/product/VISION.md)
- **Where it stands:** [docs/STATUS.md](docs/STATUS.md)
- **How it's built:** [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)
- **All docs:** [docs/README.md](docs/README.md)
- **Working with agents:** [AGENTS.md](AGENTS.md)

## Branches

`feat/*`, `fix/*` → `staging` → `main` (production)

Built on the project foundation (`.foundation/README.md`).
