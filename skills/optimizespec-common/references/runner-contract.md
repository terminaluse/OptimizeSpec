# Runner Contract

The runner is the command surface that turns eval artifacts into executable evidence. It must expose direct eval, compare, optimize, and candidate-inspection operations using the target repo's existing command conventions where possible.

## Required Operations

- Direct eval: evaluate one candidate against eval cases without GEPA search and persist the evidence ledger.
- Compare: evaluate baseline and candidate on the same cases, persist per-case deltas, aggregate deltas, guardrail movement, and comparison evidence.
- Optimize: run GEPA over train cases, evaluate or prepare validation evidence, persist optimizer lineage, leaderboard, events, selected candidate, and rejection evidence.
- Show candidate: print or serialize candidate fields and identifiers so reviewers can inspect the mutable surface.
- Verify: inspect generated evidence and report readiness without requiring live credentials unless the target fixture is explicitly live-only.

## Command Inputs

Commands should accept or clearly derive:

- change or eval artifact directory
- candidate path or candidate id
- eval cases path
- run directory
- max metric calls or budget
- timeout
- live or dry-run mode
- credential or environment preflight behavior

## Command Outputs

Each operation should print a concise structured summary and write durable files. Outputs must identify the run directory, candidate ids, aggregate result, failures, and next inspection path.

## Rollout Lifecycle

A rollout is one candidate on one eval case. It loads the candidate, compiles mutable fields into runtime behavior, invokes the target agent, captures output and runtime evidence, scores the result, builds ASI, writes per-case files, and cleans up or records cleanup warnings.

## Failure Behavior

Unsupported runtimes, missing invocation details, missing credentials for live runs, invalid candidates, invalid eval cases, scorer errors, timeouts, and persistence failures must become explicit failed evidence. Do not silently skip cases or treat missing evidence as success.
