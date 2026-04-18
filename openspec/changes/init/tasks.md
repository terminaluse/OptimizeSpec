## 1. GEPA-facing candidate surface

- [x] 1.1 Define the initial `dict[str, str]` candidate schema for Claude Managed Agents fields
- [x] 1.2 Decide whether to support both `str` and `dict[str, str]` candidate modes in the first version
- [x] 1.3 Implement candidate serialization, loading, and deterministic identity generation from text contents
- [x] 1.4 Implement utilities for reading and updating individual candidate text fields

## 2. Evaluator and runtime boundary

- [x] 2.1 Implement a GEPA evaluator callable that accepts a candidate and optional task example in GEPA's expected signature
- [x] 2.2 Implement runtime helpers that compile candidate text fields into Claude Managed Agents agent, environment, file, and outcome inputs
- [x] 2.3 Implement session execution and artifact collection for one managed-agent evaluation run
- [x] 2.4 Implement failure handling that converts Anthropic runtime errors into scored evaluator results

## 3. Score and ASI construction

- [x] 3.1 Implement scalar score generation for benchmark runs
- [x] 3.2 Implement `side_info` builders with expected, actual, error, feedback, and run metadata fields
- [x] 3.3 Implement `side_info["scores"]` generation with higher-is-better normalization for auxiliary objectives
- [x] 3.4 Implement parameter-specific diagnostics for individual candidate text fields
- [x] 3.5 Implement GEPA logging or stdio capture support for evaluator diagnostics

## 4. GEPA task-mode integration

- [x] 4.1 Define task example schemas for single-task, multi-task, and train or validation execution
- [x] 4.2 Implement `optimize_anything(...)` wiring for `dataset`, `valset`, `objective`, `background`, and `config`
- [x] 4.3 Implement an initial run configuration for generalization mode with separate training and validation tasks
- [ ] 4.4 Add support for seedless mode only if the objective and background are sufficient to generate a useful starting candidate

## 5. Persistence and resume workflows

- [x] 5.1 Persist candidate snapshots, evaluator outputs, and Anthropic run metadata for replay and debugging
- [ ] 5.2 Persist enough optimization metadata to resume interrupted GEPA runs
- [ ] 5.3 Evaluate whether to use `OptimizationState` in the evaluator for warm-starting from prior best example results

## 6. Validation and operator workflows

- [x] 6.1 Create a small benchmark suite to validate the end-to-end GEPA evaluator loop against Claude Managed Agents
- [x] 6.2 Add smoke tests for candidate loading, evaluator execution, score construction, and GEPA run startup
- [x] 6.3 Document how to configure objective, background, datasets, and Anthropic credentials for a run
- [x] 6.4 Document how to inspect side information and replay failed evaluations
