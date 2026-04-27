# Managed Agents Runtime Reference

This is the included runtime reference for projects that use Claude Managed Agents. It is an implementation guide for the runtime-neutral contracts. If the agent project uses another hosted runtime or language, apply `references/core/live-eval-runner-contract.md` and the other core contracts to that runtime, then record the adapter assumptions and any missing runtime-specific reference coverage.

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

Each live rollout must follow `references/core/live-eval-runner-contract.md`: runtime-neutral top-level fields and Claude-specific details under `runtime_metadata`.

Top-level rollout fields include candidate id, eval case id, status, final output or report, trace summary, tool activity, usage, errors, timeout status, cleanup status, timestamps, and score input references.

Claude-specific runtime metadata includes Agent id and version, Environment id, Session id and status, input attachment method, event types, beta/header assumptions, mounted files/resources, generated file ids, resolved skills, callable agents, archive attempts, cleanup warnings, and preview SDK details.

The grader must consume live final outputs/reports and trace evidence. Prompt text coverage, fixture execution, and dry-run output are outside Managed Agents eval modes.

## Lifecycle Helpers

Managed Agents runners should handle stream draining, bounded settle polling after idle, timeout/interrupt, output retrieval, session archive retries, Agent/Environment cleanup, and cleanup-warning recording. If credentials, preview SDK surfaces, permissions, or environment config are missing, fail clearly and clean up any live resources that were created.

## Preview Caveats

Live validation is opt-in because credentials, preview access, and API behavior are environment-dependent. Deterministic validation must remain enough to verify the local evidence-ledger and workflow contracts.
