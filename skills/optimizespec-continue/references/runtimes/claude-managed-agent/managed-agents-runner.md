# Managed Agents Runner Reference

This runner reference applies when the target repo uses Claude Managed Agents.

Read `references/core/live-eval-runner-contract.md` before adapting this runtime reference. The Managed Agents runner must treat a live Session rollout as the eval primitive and must grade final output/report plus trace evidence, not prompt text coverage.

## Discovery Checklist

Before implementation, inspect the agent project for:

- language and Anthropic SDK usage
- Agent creation and version persistence
- Environment creation or lookup
- Session creation
- resource mounting
- event streaming or polling
- tools, skills, MCP servers, and permissions
- run logs and output collection
- test and command conventions

For other runtimes, use the core live eval, runner, evidence, grader, ASI, candidate, optimizer, and verification contracts to design the repo-local adapter for the actual runtime, and record any missing runtime-specific reference coverage.

## Rollout Lifecycle

A rollout is one candidate on one eval case.

1. Load change artifacts, eval case, scorer config, and candidate.
2. Compile candidate fields into an agent configuration overlay.
3. Create or update candidate-specific Agent resources, or reuse existing factories reproducibly.
4. Create or select the Environment.
5. Start a Session pinned to the candidate Agent version.
6. Attach eval inputs through messages, files, repositories, or resources.
7. Stream or poll until terminal evidence, bounded post-idle settle, timeout, failure, or required action.
8. Collect final output or report, event summaries, tool calls, usage, runtime IDs, generated files, timeout details, cleanup details, and errors.
9. Score the result.
10. Build ASI.
11. Persist artifacts.
12. Archive or clean up ephemeral resources when appropriate.

The persisted rollout record keeps candidate id, eval case id, final output, trace summary, tool activity, usage, errors, timeout, cleanup, timestamps, and score input references at the top level. Agent id/version, Environment id, Session id/status, event types, beta/header assumptions, files/resources, resolved skills, callable agents, and archive warnings belong under runtime metadata.

## Required Operations

Expose operations equivalent to:

- `eval`: direct evaluation without GEPA search.
- `optimize`: GEPA optimization over train examples.
- `compare`: baseline vs candidate evaluation on the same cases.
- `show-candidate`: print candidate fields.

Adapt command shape to the agent project. Existing CLIs, package scripts, or module commands are all acceptable.

## Path And Config Resolution

Generated runners must resolve candidate files, eval case files, source fixtures, run directories, credentials, timeouts, and environment configuration from explicit flags or a known project root. They should run from the repo root, the optimization-system folder, and CI without depending on accidental current working directory state.

Missing `ANTHROPIC_API_KEY`, preview SDK surfaces, permissions, or environment config should produce failed evidence with a runtime setup error. Runtime setup failures remain separate from prompt-quality ASI.
