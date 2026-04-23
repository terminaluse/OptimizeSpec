# Managed Agents Runner Reference

The v1 runtime target is Claude Managed Agents only.

## Discovery Checklist

Before implementation, inspect the target repo for:

- language and Anthropic SDK usage
- Agent creation and version persistence
- Environment creation or lookup
- Session creation
- resource mounting
- event streaming or polling
- tools, skills, MCP servers, and permissions
- run logs and output collection
- test and command conventions

If the repo does not use Claude Managed Agents, stop. Other runtimes are out of scope for v1.

## Rollout Lifecycle

A rollout is one candidate on one eval case.

1. Load change artifacts, eval case, scorer config, and candidate.
2. Compile candidate fields into a target-agent configuration overlay.
3. Create or update candidate-specific Agent resources, or reuse existing factories reproducibly.
4. Create or select the Environment.
5. Start a Session pinned to the candidate Agent version.
6. Attach eval inputs through messages, files, repositories, or resources.
7. Stream or poll until idle, terminated, timeout, failure, or required action.
8. Collect outputs, event summaries, tool calls, usage, runtime IDs, generated files, and errors.
9. Score the result.
10. Build ASI.
11. Persist artifacts.
12. Archive or clean up ephemeral resources when appropriate.

## Required Operations

Expose operations equivalent to:

- `eval`: direct evaluation without GEPA search.
- `optimize`: GEPA optimization over train examples.
- `compare`: baseline vs candidate evaluation on the same cases.
- `show-candidate`: print candidate fields.

Adapt command shape to the target repo. Existing CLIs, package scripts, or module commands are all acceptable.
