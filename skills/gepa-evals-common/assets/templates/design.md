## Context

Summarize target repo discovery and Claude Managed Agents runtime shape.

## Runner Invocation

Define direct eval, optimize, compare, and show-candidate commands or scripts.

## Candidate Surface

Map each mutable candidate field to target repo runtime behavior.

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

## Optimizer Acceptance

- Optimized metric:
- Diagnostic metrics:
- Guardrail metrics:
- Promotion rule:
- Regression tolerance:
- Required evidence:

## Risks and Blockers

Include unsupported runtime or missing credential concerns.
