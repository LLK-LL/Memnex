# Agent Namespace Onboarding

This document is the standard setup guide for connecting a new agent to Total Agent Memory.

Use this when adding a new agent such as `claude`, `cursor`, `jarvis`, or any custom namespace.

## Core Rule

Every agent must write to its own `agent_namespace`.

Default namespace:

- `codex` for Codex-originated writes

Non-default examples:

- `claude` for Claude-based agents
- `cursor` for Cursor-based agents
- `jarvis` for Jarvis
- `custom:<name>` for any other agent family

## What Actually Controls Writes

The server resolves namespace in this order:

1. Explicit `agent_namespace` tool argument
2. Environment variable `TAM_AGENT_NAMESPACE`
3. Environment variable `MEMORY_AGENT_NAMESPACE`
4. Fallback `codex`

For that reason, the safest setup is:

- set `TAM_AGENT_NAMESPACE` for the agent process
- also pass `agent_namespace` explicitly when the client supports it

Do not use an MCP header as the standard namespace configuration. Use an environment variable or explicit tool argument unless the server is explicitly extended to read a namespace header.

## Required Setup For A New Agent

### 1. Pick A Namespace

Choose one stable lowercase namespace string.

Examples:

- `claude`
- `cursor`
- `jarvis`

Do not reuse `codex` for a different agent.

### 2. Configure The Agent Process

Set the environment variable before the agent starts:

```powershell
$env:TAM_AGENT_NAMESPACE = "<agent-namespace>"
```

Equivalent shell examples:

```bash
export TAM_AGENT_NAMESPACE=<agent-namespace>
```

If the client or launcher supports a per-tool namespace field, also pass:

```json
{
  "agent_namespace": "<agent-namespace>"
}
```

### 3. Keep MCP Connection Targeting The Shared Server

All agents connect to the same Total Agent Memory server.

Current local MCP config example:

```json
{
  "mcpServers": {
    "total-agent-memory": {
      "type": "http",
      "url": "http://127.0.0.1:3747/mcp/"
    }
  }
}
```

Do not add `X-TAM-Agent-Namespace` as part of the standard setup. It can mislead agents into thinking the server reads the header. Only use a namespace header after the server has been explicitly verified to support it.

### 4. Verify The Agent Writes To Its Own Namespace

Save one probe memory:

```text
content: "namespace probe for <agent-namespace>"
type: "fact"
agent_namespace: "<agent-namespace>"
```

Then confirm the record is stored with the expected namespace and does not appear in the default Codex-only recall.

### 5. Verify Recall Isolation

Expected default behavior:

- Codex recalls only `codex`
- each non-Codex agent recalls only its own namespace
- Cross-agent search happens only when explicitly requested

## Recommended Onboarding Workflow

When adding a new agent, follow this order:

1. Add the namespace to the agent launcher or environment
2. Set `TAM_AGENT_NAMESPACE`
3. Confirm the client passes `agent_namespace` when available
4. Save a probe record
5. Verify the saved record appears in the correct namespace
6. Verify default recall does not leak across namespaces
7. If needed, backfill old records for that agent

## New Agent Example

For a new agent, replace `<agent-namespace>` with that agent's own namespace:

```powershell
$env:TAM_AGENT_NAMESPACE = "<agent-namespace>"
```

And, when the client can set it, every write should include:

```json
{
  "agent_namespace": "<agent-namespace>"
}
```

Do not rely on `X-TAM-Agent-Namespace` unless the server has been verified to read that header.

## Codex Example

Codex can usually rely on the default:

```powershell
$env:TAM_AGENT_NAMESPACE = "codex"
```

Or leave it unset and let the fallback resolve to `codex`.

## New Agent Checklist

- Choose a unique namespace
- Set `TAM_AGENT_NAMESPACE`
- Pass `agent_namespace` explicitly when possible
- Keep all writes on the shared MCP server
- Confirm namespace-isolated recall
- Confirm cross-agent search requires explicit scope

## Related Files

- [.mcp.json](C:/Users/Administrator/total-agent-memory/.mcp.json)
- [src/server.py](C:/Users/Administrator/total-agent-memory/src/server.py)
- [docs/superpowers/specs/2026-06-29-agent-namespaced-memory-galaxies-design.md](C:/Users/Administrator/total-agent-memory/docs/superpowers/specs/2026-06-29-agent-namespaced-memory-galaxies-design.md)
