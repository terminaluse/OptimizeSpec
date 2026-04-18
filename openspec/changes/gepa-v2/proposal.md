## Why

The current GEPA integration proves the loop can run, but it does not yet treat the full Claude Managed Agents configuration as a first-class optimization surface. We need a v2 design that keeps the simpler `optimize_anything()` API while allowing GEPA to mutate and evaluate every major agent component that materially changes runtime behavior.

## What Changes

- Redefine the GEPA candidate surface around the full Claude Managed Agents configuration instead of a prompt-dominant subset.
- Keep the integration on `optimize_anything()` and strengthen the evaluator/compiler layer so every candidate field is parsed, canonicalized, compiled, and exercised during evaluation.
- Add full-surface runtime support for candidate-provided `skills`, `environment_spec`, and `subagent_specs`, including hybrid Skills API materialization for `skills` and real subagent creation instead of the current guarded placeholder path.
- Add field-specific reflection guidance and richer evaluator side information so GEPA can improve structured configuration fields without switching to the more complex adapter API.
- Expand the benchmark and experiment defaults so structured fields have real opportunities to affect task outcomes and GEPA has enough budget to search the larger space.

## Capabilities

### New Capabilities

- `full-surface-managed-agent-candidate`: Represent the full Claude Managed Agents optimization surface as a GEPA-compatible `dict[str, str]` candidate with stable canonical formats for prompts and structured configuration fields, including declarative hybrid skill specs.
- `managed-agent-candidate-compiler`: Parse, validate, canonicalize, resolve, and compile GEPA candidate fields into fresh Claude Managed Agents resources for each evaluation.
- `full-surface-managed-agent-runtime`: Execute Claude Managed Agents evaluations where `system_prompt`, `task_prompt`, `outcome_rubric`, `skills`, `environment_spec`, and `subagent_specs` all materially affect runtime behavior, including create-or-reuse custom skill resolution via the Skills API.
- `structured-reflection-guidance`: Provide field-specific reflection prompts and evaluator feedback so GEPA can improve structured candidate fields while staying on `optimize_anything()`.
- `full-surface-gepa-benchmarking`: Define task suites, budgets, and comparison outputs that measure whether full-surface candidate mutations improve end-to-end Managed Agents performance.

### Modified Capabilities

- None.

## Impact

Affected systems include the GEPA candidate schema, candidate parsing and canonicalization logic, Anthropic Skills API resolution, Anthropic Managed Agents runtime compilation, subagent support, evaluator side information, benchmark task definitions, experiment defaults, and OpenSpec planning artifacts for the repo.
