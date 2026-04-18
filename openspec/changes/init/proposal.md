## Why

This project needs a GEPA integration that matches GEPA's actual `optimize_anything` API instead of a broader custom abstraction. GEPA optimizes text-representable artifacts through a small surface area centered on `seed_candidate`, `dataset` or `valset`, and an `evaluator`, so the Claude Managed Agents integration needs to be designed around that boundary.

## What Changes

- Redefine the GEPA integration around `optimize_anything(...)` using a GEPA-facing candidate of type `str`, `dict[str, str]`, or seedless `None`.
- Define a text-first candidate schema for Claude Managed Agents where each mutable part of the agent system is represented as a named text field GEPA can mutate.
- Add an evaluator/runtime layer that compiles a text candidate into Anthropic Managed Agents resources, runs task sessions, and returns `score` or `(score, side_info)` in the format GEPA expects.
- Add train, validation, objective, and background wiring so the integration supports single-task, multi-task, and generalization modes.
- Add structured Actionable Side Information capture so Claude session traces, errors, deliverables, and evaluator diagnostics can be fed back into GEPA reflection.

## Capabilities

### New Capabilities

- `managed-agent-gepa-candidate-surface`: Represent the Claude Managed Agents configuration as a GEPA-compatible text candidate using `str` or `dict[str, str]` fields.
- `managed-agent-gepa-evaluator-runtime`: Compile GEPA candidates into Managed Agent executions and return GEPA-compatible scores and side information.
- `gepa-task-mode-wiring`: Support GEPA single-task, multi-task, and generalization modes through dataset and valset integration.
- `gepa-asi-and-objective-integration`: Feed structured side information, objective text, and background context into GEPA in a way that improves reflection quality.

### Modified Capabilities

- None.

## Impact

Affected systems include the project's candidate representation, Anthropic Managed Agents integration, benchmark task definitions, evaluator implementation, experiment logging, and GEPA orchestration entrypoint. This change narrows the integration contract so GEPA sees only text candidates and evaluator outputs, while Anthropic-specific resource creation remains behind the evaluator/runtime boundary.
