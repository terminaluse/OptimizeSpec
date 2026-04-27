# Runner Contract

The runner is the command surface that turns eval artifacts into executable evidence. It must expose direct eval, compare, optimize, and candidate-inspection operations using the agent project's existing command conventions where possible.

For live agent optimization systems, read `references/core/live-eval-runner-contract.md` first. The optimization unit is a live rollout record: candidate x eval case x real agent runtime. The runner exposes live eval modes only; static prompt, config, fixture, dry-run, or template-output checks belong outside the optimization path.

## Required Operations

- Direct eval: evaluate one candidate against eval cases without GEPA search and persist rollout, score, ASI, and summary evidence.
- Compare: evaluate baseline and candidate on the same cases, persist per-case live deltas, aggregate deltas, guardrail movement, and comparison evidence.
- Optimize: run GEPA or another optimizer over train cases, score candidates through the runner and grader, persist optimizer lineage, leaderboard, events, selected candidate, rejected candidates, budgets, and evidence locations.
- Show candidate: print or serialize candidate fields and identifiers so reviewers can inspect the mutable surface.
- Verify: inspect generated evidence and report readiness without requiring live credentials unless the target fixture is explicitly live-only.

## Command Inputs

Commands should use either explicit artifact paths or a single artifact directory that derives those paths. Do not include both unless the directory is used for additional metadata.

- candidate path or candidate id, unless derived from an artifact directory
- eval cases path, unless derived from an artifact directory
- run directory, unless derived from an artifact directory
- artifact directory, only when the runner derives candidate, cases, run-output paths, or metadata from it
- max metric calls or budget
- timeout
- live runtime mode
- credential and environment configuration

## Command Outputs

Each operation should print a concise structured summary and write durable files. Outputs must identify the run directory, candidate ids, aggregate result, failures, live credential/runtime blockers, and next inspection path.

## Rollout Lifecycle

A rollout is one candidate on one eval case. It loads the candidate, compiles mutable fields into runtime behavior, invokes the real agent, captures final output or report plus runtime evidence, scores the result, builds ASI, writes per-case files, and cleans up or records cleanup warnings.

Managed Agents rollout records must keep runtime-neutral fields at the top level and nest Agent, Environment, Session, event, file, beta/header, and cleanup details under runtime metadata.

## Failure Behavior

Missing runtime identification, missing invocation details, missing credentials for live runs, invalid candidates, invalid eval cases, scorer errors, timeouts, and persistence failures must become explicit failed evidence. Do not silently skip cases or treat missing evidence as success.
