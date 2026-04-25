# GEPA Reflection Reference

GEPA improves text-representable candidates by using reflective evolution. The evaluator must return a scalar score plus Actionable Side Information (ASI). ASI is the "why" signal: it tells the reflection model what failed, what worked, and how a candidate field might improve.

## Candidate Surface

Use `dict[str, str]` unless the agent project has a strong reason to do otherwise. Typical text-representable agent fields include:

- `system_prompt`
- `task_prompt`
- `outcome_rubric`
- `skills`
- `environment_spec`
- `tool_policy`
- `resource_policy`
- `subagent_specs`

Only include fields that the runner actually compiles into runtime behavior. Runtime-specific contracts may narrow or extend this list.

## Evaluator Contract

```python
def evaluator(candidate: dict[str, str], example: EvalCase) -> tuple[float, dict]:
    rollout = run_candidate(candidate, example)
    score = score_rollout(rollout, example)
    side_info = build_asi(candidate, example, rollout, score)
    return score, side_info
```

## ASI Rules

- Include input, expected, actual, feedback, errors, and trajectory.
- Include both failures and successes so reflection can preserve working behavior.
- Put multi-objective metrics in `scores`; all scores must be higher-is-better.
- Add `<field>_specific_info` for mutable fields when diagnostics can guide that field.

## Reflection Configuration

Configure:

- reflection model
- module/component selector
- per-field reflection prompts
- metric-call budget
- per-rollout timeout
- run directory
- stdio/log capture

Use round-robin selection for independent fields. Update fields together when they are tightly coupled.
