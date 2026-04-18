## Context

This change introduces a GEPA integration for Claude Managed Agents, but the integration must follow GEPA's actual `optimize_anything` contract rather than a broader artifact system. The key API surface is small: `seed_candidate`, `evaluator`, optional `dataset` and `valset`, optional `objective` and `background`, and `config`.

The most important constraint is that GEPA optimizes text-representable artifacts. In practice that means the GEPA-facing candidate must be either a single string, a `dict[str, str]`, or `None` for seedless mode. Claude Managed Agents can still expose a wide mutable surface, but every optimizable part has to be encoded as text fields that the evaluator can compile into Anthropic resources.

The second key constraint is that the evaluator is the true integration boundary. GEPA does not directly manage Anthropic agents, environments, files, or sessions. Instead, our evaluator receives a candidate plus optionally a task example and optimization state, runs the Anthropic workflow, and returns a numeric score or `(score, side_info)` for GEPA to optimize.

## Goals / Non-Goals

**Goals:**
- Define a GEPA-facing candidate interface for Claude Managed Agents using `str` or `dict[str, str]`.
- Keep Anthropic-specific compilation and execution entirely inside the evaluator/runtime layer.
- Support GEPA's three operating modes: single-task search, multi-task search, and generalization mode.
- Produce rich Actionable Side Information that helps GEPA reflection improve candidates over time.
- Preserve enough run metadata to support replay, diagnostics, and optimization resume workflows.

**Non-Goals:**
- Expose nested Python objects or provider-specific runtime objects directly to GEPA.
- Replace Claude Managed Agents' internal session loop with custom orchestration.
- Design a generic artifact optimizer independent of the `optimize_anything` contract.
- Optimize arbitrary binary assets in the initial version.

## Decisions

### 1. Use a GEPA-facing text candidate instead of a custom nested candidate object

The integration will expose candidates to GEPA as either a single string or a flat dictionary of named text fields. For Claude Managed Agents, the default shape should be `dict[str, str]` so multiple mutable surfaces can be optimized independently while still fitting GEPA's expected candidate model.

Example fields include agent system prompt, task bootstrap prompt, outcome rubric text, environment specification text, skill text, and tool policy text.

This is preferred over a nested manifest object because it matches the documented `optimize_anything` interface and keeps GEPA's proposer operating over text parameters it can directly rewrite.

Alternatives considered:
- A nested Python manifest object passed into GEPA.
  Rejected because GEPA's documented candidate surface is text-based rather than arbitrary object graphs.
- One monolithic prompt string only.
  Rejected because it makes component-level mutation and side information less targeted.

### 2. Keep Anthropic resource creation behind the evaluator/runtime boundary

The evaluator will be responsible for turning the GEPA candidate into concrete Anthropic Managed Agents inputs. That includes materializing or selecting agent definitions, preparing files, configuring environments, launching sessions, defining outcomes, and collecting deliverables and traces.

This is preferred because the evaluator is GEPA's scoring hook and is the documented place where arbitrary domain-specific execution happens.

Alternatives considered:
- Make GEPA directly aware of Anthropic resources.
  Rejected because it expands beyond GEPA's actual API boundary and couples search logic to provider runtime objects.

### 3. Treat `dataset` and `valset` as the task-mode selector

The integration will rely on GEPA's built-in mode selection:
- no `dataset` and no `valset` for single-task search
- `dataset` only for multi-task search
- both `dataset` and `valset` for generalization mode

This is preferred because it uses GEPA's existing evaluation loop instead of inventing another task orchestration abstraction on top.

Alternatives considered:
- Custom train and validation orchestration outside GEPA.
  Rejected because GEPA already exposes this distinction directly.

### 4. Use `objective` and `background` for reflection guidance, not runtime execution

The project will use GEPA's `objective` and `background` parameters to shape reflection and candidate improvement, while keeping runtime task instructions inside the evaluator's task example or candidate fields. This preserves the intended role of `objective` and `background` as guidance for the reflection LLM.

Alternatives considered:
- Put all execution and reflection guidance into the candidate only.
  Rejected because GEPA already provides `objective` and `background` for this purpose.

### 5. Standardize ASI around GEPA's `(score, side_info)` contract

The evaluator will return either a scalar score or a `(score, side_info)` tuple, with `side_info` containing both run-level diagnostics and optional parameter-specific feedback. Multi-objective metrics will be placed under `side_info["scores"]` and normalized so higher is better, for example `cost_inv` or `latency_inv`.

This is preferred because it matches GEPA's documented ASI structure and gives reflection targeted information about why a candidate failed.

Alternatives considered:
- Emit only a single scalar score.
  Rejected because it throws away the main optimization signal GEPA uses for reflective improvement.

### 6. Persist optimization artifacts outside GEPA's core contract

Run records, candidate snapshots, Anthropic traces, and replay metadata will be persisted by the project runtime, but those details will remain implementation details outside the GEPA interface itself. GEPA only needs the candidate, the evaluation result, and the configured optimization parameters.

This is preferred because it keeps the GEPA boundary narrow while still supporting real-world operability.

Alternatives considered:
- Push storage semantics into the GEPA candidate structure.
  Rejected because persistence is an implementation concern, not part of the documented optimization API.

## Risks / Trade-offs

- [Candidate fields may be too coarse or too fragmented] -> Start with a small `dict[str, str]` schema and refine field granularity based on reflection quality and mutation usefulness.
- [Evaluator logic can become a monolith] -> Split the evaluator into compilation, execution, grading, and ASI-building helpers behind one GEPA-compatible callable.
- [Side information may be noisy or low-signal] -> Standardize field names and include expected versus actual outputs, session errors, and parameter-specific notes.
- [Generalization may be weak if train and validation tasks are not separated cleanly] -> Use explicit `dataset` and `valset` splits from the start.
- [Seedless mode can generate low-quality starting points] -> Prefer a strong seed candidate initially and add seedless mode only where exploratory search is valuable.
- [Anthropic beta/runtime behavior may change] -> Keep Anthropic-specific details isolated behind the evaluator/runtime layer and version-pin integration code where possible.

## Migration Plan

1. Redefine the candidate schema as GEPA-compatible text fields.
2. Implement evaluator helpers that compile text candidates into Anthropic Managed Agents executions.
3. Implement task example schemas for single-task, multi-task, and train or validation runs.
4. Implement score and side-information builders aligned to GEPA's expected return format.
5. Wire `optimize_anything(...)` with objective, background, dataset, valset, and config.
6. Add replay, diagnostics, and resume support around the evaluator runtime.

Rollback remains straightforward because this is still a greenfield addition. If the candidate schema or evaluator contract proves ineffective, the main rollback path is to simplify the GEPA-facing candidate fields and keep Anthropic execution details behind stable helper APIs.

## Open Questions

- What is the smallest useful initial `dict[str, str]` candidate schema for Claude Managed Agents?
- Which parts of the Anthropic agent setup should be represented as separate text fields versus bundled into one field?
- Should the first implementation support both string and dict candidates, or standardize immediately on `dict[str, str]`?
- Which metrics should be treated as the primary scalar score versus additional entries in `side_info["scores"]`?
- Should the evaluator use `OptimizationState` immediately for warm-starting from prior best example evaluations, or defer that until the base loop works?
