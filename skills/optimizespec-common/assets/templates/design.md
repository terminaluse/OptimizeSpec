## Context

Summarize what you found in the agent project and describe the inferred target runtime, evidence, confidence, and important unknowns.

## Optimization System Location

Confirm the proposal's create-or-reuse decision, the path where executable optimization code will live, why that path belongs in the repo's eval, test, tooling, or agent package-adjacent surface, the existing agent code it will import or adapt, how modules and runtime dependencies will be importable from that path, and where run outputs will be written.

## Runner Invocation

Define direct eval, optimize, compare, and show-candidate commands or scripts.

Direct eval and optimize must execute the real agent runtime unless a runtime blocker is explicitly recorded. For Claude Managed Agents, this means live Session rollouts.

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

## Runtime-Specific Plan

Name the core contracts and any runtime references used for this design. For Claude Managed Agents, include Agent, Environment, Session, resources, event streaming or polling, tools, skills, MCP servers, permissions, and cleanup behavior. For runtimes without a bundled reference, record the adapter assumptions, production integrations to reuse, and missing runtime-specific reference coverage.

## Trace Capture

List outputs, event summaries, tool calls, usage, runtime IDs, generated files, and errors to capture.

## Evidence Ledger

Define the run directory, manifest, candidate registry, evaluation summary, per-case score records, judge records, ASI records, rollout records, comparison records, optimizer records, best-candidate evidence, and any optional promotion decision. Explain how reviewers inspect missing or failed evidence.

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

Define candidate ids, parent ids, mutation summaries, live-score leaderboard records, optimizer event logs, selected candidate, rejected candidates, budgets, evidence locations, and rollback path.

## Optimizer Acceptance

- Optimized metric:
- Diagnostic metrics:
- Guardrail metrics:
- Best-candidate selection rule:
- Optional promotion or release rule:
- Regression tolerance:
- Required evidence:

## Verification Plan

Define live runtime checks, emitted evidence inspection, runtime blocker behavior when credentials are missing, and readiness reporting.

## Risks and Blockers

Include missing runtime reference, missing credential, or missing production-integration concerns.
