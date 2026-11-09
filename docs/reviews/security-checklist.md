# Security review checklist

Part of the project foundation. Required for any change touching auth, permissions, money, personal data, or a new integration. Mark each item ✓, ✗ (with a finding) or n/a.

## Access

- [ ] Authentication and authorization are enforced server-side, never only in the UI
- [ ] Every query on tenant data is tenant-scoped (RLS or explicit filter), with a test proving tenant A can't read tenant B
- [ ] New roles and tokens get least privilege

## Input and output

- [ ] Inputs are validated at the boundary (schema), and queries are parameterised
- [ ] Output is encoded for its context (HTML, URLs, headers)
- [ ] File uploads are checked for type and size and stored outside the web root
- [ ] Rate limits on auth, expensive and AI endpoints

## Secrets and data

- [ ] No secrets in code, logs, errors or client bundles
- [ ] Personal and financial data is redacted from logs and traces
- [ ] Sensitive data is encrypted in transit; at rest where required
- [ ] A new vendor receiving data is in SUBPROCESSORS.md and SECURITY.md

## AI

- [ ] Untrusted content reaching a model can't change its instructions or trigger tools on its own
- [ ] The model's tools are limited to what the feature needs; risky actions need human approval
- [ ] Model output is treated as untrusted input before it's stored, rendered or executed

## Dependencies and failure

- [ ] New dependencies are maintained, licensed compatibly, and pass the audit
- [ ] Errors fail closed (deny), with a user-safe message and no stack traces
- [ ] Webhooks verify signatures and are idempotent
