# Candidate Surface Contract

The candidate surface defines what GEPA is allowed to mutate. Keep it as small as possible and tie every mutable field or file to actual runtime behavior.

## Mutable Surface

Common text-representable agent fields include:

- `system_prompt`
- `task_prompt`
- `outcome_rubric`
- `skills`
- `environment_spec`
- `tool_policy`
- `resource_policy`
- `subagent_specs`

Agent projects may use different names, and runtime-specific contracts may add more concrete fields. Every field must compile into runtime behavior or be removed from the mutable surface.

## Candidate Identifiers

Every evaluated candidate must have a stable id. Record parent id when a candidate is derived from another candidate, plus mutation reason, changed fields, and source path or diff.

## Immutable Eval Inputs

Eval cases, scoring rules, guardrails, and promotion criteria are not candidate fields. GEPA should not improve its score by changing the test. Changes to eval definitions require a separate artifact update and review.

## Diffs, Rollback, and Promotion

Persist diffs between baseline and candidate fields. A promotion decision must state which candidate becomes selected, why, what guardrails passed, and how to roll back to the previous candidate.
