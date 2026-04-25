## Context

Summarize what you found in the agent project and describe its Claude Managed Agents runtime shape.

## Runner Invocation

Define direct eval, optimize, compare, and show-candidate commands or scripts.

## Contract References

List the reference contracts used for runner, evidence, grader, ASI, candidate surface, optimizer, runtime, and verification decisions.

## Candidate Surface

Map each mutable candidate field to the agent project's runtime behavior.

## Eval Design

- Eval category: system|agent-quality|optimizer-acceptance
- Real task distribution:
- Edge cases:
- Failure modes:
- Split strategy:
- What this eval does not measure:

## Rollout Lifecycle

Describe one candidate x eval case execution from input preparation to cleanup.

## Trace Capture

List outputs, event summaries, tool calls, usage, runtime IDs, generated files, and errors to capture.

## Evidence Ledger

Define the run directory, manifest, candidate registry, evaluation summary, per-case score records, judge records, ASI records, rollout records, comparison records, optimizer records, and promotion decision. Explain how reviewers inspect missing or failed evidence.

## Scoring and ASI

Define deterministic scorers, qualitative scorers, top-level ASI, and field-specific ASI.

## Grading Strategy

- Grader type: deterministic|code|llm|human|hybrid
- Why this grader is appropriate:
- Calibration examples:
- Reliability risks:
- Human review triggers:

## GEPA Configuration

Define train/val split, objective, background, reflection model, component selector, per-field prompts, budget, timeout, and run directory.

## Optimizer Lineage

Define candidate ids, parent ids, mutation summaries, leaderboard records, optimizer event logs, selected candidate, rejected candidates, and rollback path.

## Optimizer Acceptance

- Optimized metric:
- Diagnostic metrics:
- Guardrail metrics:
- Promotion rule:
- Regression tolerance:
- Required evidence:

## Verification Plan

Define deterministic smoke checks, live Managed Agents checks if credentials are available, emitted evidence inspection, and readiness reporting.

## Risks and Blockers

Include unsupported runtime or missing credential concerns.
