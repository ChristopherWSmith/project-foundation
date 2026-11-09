---
status: draft
lifecycle: reference
last_reviewed: __DATE__
---

# Compatibility and deprecation — __PROJECT_NAME__

## Supported clients

| Client | Supported | Not supported |
|---|---|---|
| Browsers | Last 2 versions of Chrome, Edge, Firefox, Safari | IE, anything older |
| Mobile | iOS Safari / Android Chrome, last 2 major versions | |
| Screen sizes | ≥ 360px wide | |

## Public interfaces

| Interface | Versioning | Current | Deprecated |
|---|---|---|---|
| REST / API | | | |
| Webhooks | payload `version` field | | |
| Exports / imports | | | |

## Deprecation policy

- A breaking change to a public interface needs an ADR and a new version; the old one keeps working for at least [90] days.
- Deprecations are announced in the CHANGELOG and to affected users, with the removal date.
- Data migrations are backwards-compatible for one release (expand, then contract).
