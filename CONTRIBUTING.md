# Contributing to Memnex

Memnex is early and deliberately small. Contributions should make personal AI memory easier to inspect, preserve, retrieve, and reuse.

## Good Contributions

- Adapter examples for Claude, Cursor, Continue, Windsurf, Cline, Roo, MCP servers, or other agent tools.
- Cross-platform sync support for macOS and Linux.
- Safer redaction rules and tests.
- Clear documentation for real AI-agent workflows.
- Small improvements to the PowerShell sync scripts.
- Better examples of memory, rule, skill, and preference governance.

## Scope

Please keep Memnex focused:

- local-first memory vaults;
- file-backed memories, rules, skills, preferences, and templates;
- reviewable and portable agent memory;
- conservative safety defaults.

Avoid turning Memnex into a large hosted agent platform, a general vector database, or an enterprise observability product.

## Before Opening a Pull Request

1. Keep changes small and focused.
2. Do not include real secrets, private memories, customer data, or personal exports.
3. If you add examples, prefer sanitized fake data.
4. If you touch sync behavior, explain what gets copied, excluded, or redacted.
5. Update README or docs if the user-facing workflow changes.

## Documentation Style

- Prefer short, practical examples.
- Explain when a workflow is native, adapted, or experimental.
- Show the expected directory layout.
- Call out privacy and redaction concerns clearly.
- Do not assume users want to run a server.

## Pull Request Checklist

- [ ] The change is focused.
- [ ] No private memory data or credentials are included.
- [ ] Documentation links are valid.
- [ ] New sync behavior is explained.
- [ ] Safety implications are mentioned when relevant.
