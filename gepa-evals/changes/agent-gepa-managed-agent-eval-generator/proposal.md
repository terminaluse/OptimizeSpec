## Target Agent

- Name: `agent-gepa-managed-agent`
- Runtime: Claude Managed Agents
- Fixture: `gepa-evals/fixtures/agents/agent-gepa-managed-agent`
- Invocation under test: generate eval artifacts for the existing package prototype and score whether they contain the required eval/GEPA design concepts.

## Improvement Target

Evaluate whether the GEPA eval skills can produce a useful eval plan and optimizer design for an existing Claude Managed Agent repo. This is a meta-eval: the input is an example agent fixture, the output is generated eval artifacts, and the scorer checks whether those artifacts are complete, runtime-aware, ASI-first, and implementable.

## Candidate Surface

- `fixture_analysis_guidance`: How to inspect and summarize the existing agent repo.
- `proposal_generation_guidance`: How to create the self-improvement proposal.
- `design_generation_guidance`: How to define runner invocation, rollouts, trace capture, ASI, and GEPA config.
- `spec_task_generation_guidance`: How to create specs and tasks for implementation.
- `apply_generation_guidance`: How to implement direct eval, optimize, compare, and candidate inspection without duplicating existing runtime code.
- `scoring_asi_guidance`: How to specify numeric scoring, qualitative judgement, and ASI.

## Eval Examples

### Example: proposal-for-existing-agent

- Input: Existing `agent-gepa-managed-agent` fixture plus request to create a proposal.
- Expected: Proposal identifies target runtime, existing source files, candidate fields, eval examples, scoring, ASI, and unknowns.
- Split: train

### Example: design-for-existing-agent

- Input: Existing fixture plus request to create a design.
- Expected: Design references runtime/evaluator/optimizer files, direct eval/optimize/compare/show-candidate operations, rollout lifecycle, trace capture, ASI mapping, and cleanup.
- Split: train

### Example: specs-tasks-for-existing-agent

- Input: Existing fixture plus request to create specs and tasks.
- Expected: Specs/tasks cover candidate surface, eval dataset/scorers, Managed Agent runner, ASI, GEPA optimization, apply behavior, and validation.
- Split: train

### Example: generated-eval-cases

- Input: Existing fixture plus request to define eval cases.
- Expected: Eval cases include file-transform behavior, structured candidate validity, runtime failure handling, score semantics, train/val splits, and ASI expectations.
- Split: val

### Example: generated-apply-plan

- Input: Existing fixture plus request to apply the plan.
- Expected: Apply plan reuses `ManagedAgentRuntime`, `ManagedAgentEvaluator`, and `optimize_demo`; exposes direct eval, optimize, compare, and candidate inspection; and blocks unsupported runtimes.
- Split: val

### Example: end-to-end-optimization-loop

- Input: Existing fixture plus request to run the generated system end to end.
- Expected: Generated system creates artifacts, runs direct eval, invokes GEPA optimize, and produces optimization artifacts such as `candidates.json` and `run_log.txt`.
- Split: test

## Scoring

- Numeric score range: `0.0` to `1.0`
- High score means: generated artifact text contains every required term for that eval case.
- Partial score means: some required terms are missing and ASI lists them.
- Failing score means: generated output is empty, irrelevant, or errors.
- Deterministic scorer: required-term coverage, plus end-to-end system loop success for the system-run case.
- Qualitative rubric: Generated artifacts should be specific to the existing `agent-gepa` Managed Agent implementation rather than generic eval advice.

## ASI Contract

Each rollout must include fixture input, expected required concepts, generated artifact text, missing concepts, runtime action trace, scores, and field-specific feedback for candidate guidance fields.

## Unknowns

- This local meta-eval scores deterministic artifact generation; a live agent-run eval can later execute the actual `gepa-evals-*` skills in a Claude Managed Agent session.
