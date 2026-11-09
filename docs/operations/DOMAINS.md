---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# Domains and DNS — __PROJECT_NAME__

Every domain this product uses, and every DNS record on it.

## Domains

| Domain | Purpose | Registrar | Renews | Auto-renew | Monitored in UptimeWatchr |
|---|---|---|---|---|---|
| | primary | | | yes | SSL + expiry |

## Subdomain plan

| Host | Points to | Purpose |
|---|---|---|
| `@` / `www` | | Marketing site |
| `app` | | Product |
| `api` | | API |
| `status` | | Status page |

## DNS records (every record, with a reason)

| Type | Name | Value | Why | Added |
|---|---|---|---|---|
| | | | | |

**Remove a record when its service is gone.** A CNAME pointing at a deleted service lets someone else claim your subdomain.

## Email authentication (before the first email is sent)

- [ ] SPF: one record, includes only the providers you use
- [ ] DKIM: a record per sending provider
- [ ] DMARC: start with `p=none` plus a reporting address, move to `quarantine` once reports are clean
- [ ] Sender addresses: `hello@` (human), `no-reply@` or `notifications@` (transactional)
