# Review brief: AI red team

Part of the project foundation. Run it before launching an AI feature and after major prompt, model or tool changes.

## Probes

- [ ] **Direct injection:** the user tells the model to ignore its instructions, reveal the system prompt, or act as another user.
- [ ] **Indirect injection:** instructions hidden in content the model reads (emails, documents, web pages, transaction memos) try to trigger tools or leak data.
- [ ] **Cross-tenant leakage:** can a prompt get the model to retrieve or mention another tenant's data?
- [ ] **Tool abuse:** can the model be led to call a tool with arguments the user couldn't use directly?
- [ ] **Output handling:** model output containing HTML, markdown links, SQL or code is rendered or stored safely.
- [ ] **Cost abuse:** very long inputs or loops can't run up unbounded token spend (limits, timeouts).
- [ ] **Confidently wrong:** for answers that matter (money, health, legal), does the UI label AI output and invite review?

## Output

Findings in the format from `docs/engineering/AGENT-WORKFLOW.md`. Each successful probe also becomes a case in `evals/`.
