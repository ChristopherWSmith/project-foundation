# Brand — __PROJECT_NAME__

Everything visual about the brand comes from this folder. Code never hard-codes a color, font or spacing value; CI fails on raw hex in UI files.

## Name

- Written **__PROJECT_NAME__**: same capitalization everywhere, never abbreviated.
- Wrong spellings to catch are listed in `copy-lint.json`.

## Tokens

`tokens.json` is the only source of colors, type, radius and spacing.

```bash
python3 scripts/brand/build_tokens.py             # → brand/dist/tokens.css  (:root custom properties)
python3 scripts/brand/build_tokens.py --tailwind  # → @theme block for Tailwind v4
```

Commit the generated CSS; CI checks it matches `tokens.json`. Import `brand/dist/tokens.css` once, in the app's global stylesheet.

## Files to provide (`logo/`, `og/`)

| File | Size | Use |
|---|---|---|
| `logo/logo.svg` | vector | Master logo |
| `logo/mark.svg` | vector | Icon-only mark |
| `logo/logo-dark.svg` | vector | On dark backgrounds |
| `logo/favicon.ico` | 32×32 | Browser tab |
| `logo/icon-192.png`, `logo/icon-512.png` | 192, 512 | PWA / Android |
| `logo/apple-touch-icon.png` | 180×180 | iOS |
| `og/default.png` | 1200×630 | Default social preview |

## Usage rules

- Minimum clear space around the logo: the height of the mark's smallest element.
- Never recolor, stretch, or add effects to the logo.
- Text contrast meets WCAG AA (4.5:1 body, 3:1 large text). Check each new token pairing.
