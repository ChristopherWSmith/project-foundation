---
status: draft
lifecycle: living
last_reviewed: __DATE__
---

# Product acceptance tests — __PROJECT_NAME__

What a person checks before a release, from the user's side, beyond the automated tests. Automate a row when you can (end-to-end test) and link it, but keep it listed here.

| ID | Scenario (as the user) | Expected | Automated by | Last checked |
|---|---|---|---|---|
| A1 | Sign up, verify email, land on the first-value screen | Under 2 minutes, no dead ends | | |
| A2 | Core action on a phone-sized screen | Usable one-handed, nothing cut off | | |
| A3 | Hit an error (offline, bad input) | Message follows VOICE.md; nothing lost | | |
| A4 | Upgrade, then downgrade, a plan | Limits change per `config/entitlements.json` | | |
| A5 | Delete account | Data goes per `docs/legal/DATA-RETENTION.md` | | |

## Release sign-off

| Release | Rows checked | Problems | By |
|---|---|---|---|
| | | | |
