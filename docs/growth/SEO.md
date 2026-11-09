---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# SEO and answer-engine visibility — __PROJECT_NAME__

Audited by AEOFuse on a schedule. Fix what it flags here, in the page templates, not page by page.

## Page patterns

| Page type | Title pattern | Description | Structured data | Indexed |
|---|---|---|---|---|
| Home | `__PROJECT_NAME__ — <value prop>` | ≤155 chars, what it does + for whom | Organization, WebSite | yes |
| Feature page | `<Feature> — __PROJECT_NAME__` | | SoftwareApplication | yes |
| Blog post | `<Post title> — __PROJECT_NAME__` | | Article | yes |
| Pricing | `Pricing — __PROJECT_NAME__` | | Product / Offer | yes |
| App pages | | | | **no** (noindex) |

## Rules

- Every indexed page has a unique title, a description, a canonical URL and a social preview image (default: `brand/og/default.png`, 1200×630).
- One `h1` per page, matching the page's intent.
- `sitemap.xml` is generated from the routes, never hand-edited.
- `robots.txt` blocks app routes, not marketing ones.
- `llms.txt` summarises the product and links the key pages, for AI answer engines.
- Pages answer the actual question in the first paragraph, which is what answer engines quote.

## Audit log

| Date | Tool | Score / issues | Fixed in |
|---|---|---|---|
| | AEOFuse | | |
