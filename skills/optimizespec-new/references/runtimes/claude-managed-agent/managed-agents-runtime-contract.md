# Managed Agents Runtime Contract

Claude Managed Agents are the only supported v1 apply runtime. If the agent project does not use Claude Managed Agents, record the blocker and do not implement a parallel runtime path.

## SDK and Headers

Live runs require Anthropic Research Preview access and the Managed Agents SDK surfaces used by the agent project. The current preview setup in this repo uses the `managed-agents-2026-04-01-research-preview` beta for Managed Agents SDK calls. Runtime details can change while preview APIs evolve, so keep SDK/header setup isolated in runtime code and technical docs.

## Invocation Assumptions

Before implementation, inspect:

- Agent creation or version lookup
- Environment creation or lookup
- Session creation
- resource mounting
- event streaming or polling
- tools, skills, MCP servers, and permissions
- run logs and output collection
- test and command conventions

Reuse existing factories and session runners when available.

## Rollout Records

Each live rollout should record Agent id and version, Environment id, Session id, input attachment method, event summary, tool calls, generated files, usage, errors, timeouts, and cleanup or archive warnings.

## Preview Caveats

Live validation is opt-in because credentials, preview access, and API behavior are environment-dependent. Deterministic validation must remain enough to verify the local evidence-ledger and workflow contracts.
