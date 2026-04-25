## Context

This change uses this repo's existing Claude Managed Agent prototype as the example agent. The fixture points at `src/optimizespec/candidate.py`, `runtime.py`, `evaluator.py`, `optimizer.py`, `tasks.py`, and `cli.py`.

The generated artifact evaluator is deterministic and credential-free. It composes proposal/design/spec/task/eval/apply artifact text from a mutable candidate and fixture facts, then scores required concept coverage. This lets the package evaluate whether its skill guidance is specific enough before running live agent sessions.

## Runner Invocation

```bash
python optimizespec/changes/optimizespec-managed-agent-eval-generator/agent_eval_generator.py show-candidate
python optimizespec/changes/optimizespec-managed-agent-eval-generator/agent_eval_generator.py generate --output-dir runs/agent-eval-generator/generated
python optimizespec/changes/optimizespec-managed-agent-eval-generator/agent_eval_generator.py eval --run-dir runs/agent-eval-generator/eval
python optimizespec/changes/optimizespec-managed-agent-eval-generator/agent_eval_generator.py compare --run-dir runs/agent-eval-generator/compare
python optimizespec/changes/optimizespec-managed-agent-eval-generator/agent_eval_generator.py optimize --max-metric-calls 12 --run-dir runs/agent-eval-generator/optimize
```

The `end-to-end-optimization-loop` eval case invokes the generated system itself: `generate`, `eval`, and `optimize --max-metric-calls 1` against a reduced non-recursive case set. It scores `1.0` only when the commands exit successfully and GEPA writes optimization artifacts.

## Candidate Surface

- `fixture_analysis_guidance`: Fixture discovery and source-file grounding.
- `proposal_generation_guidance`: Proposal artifact content.
- `design_generation_guidance`: Runtime design, rollout lifecycle, ASI, and optimizer config.
- `spec_task_generation_guidance`: Requirements and implementation tasks.
- `apply_generation_guidance`: Apply behavior and command surface.
- `scoring_asi_guidance`: Eval case scoring and ASI contract.

## Rollout Lifecycle

1. Load the fixture agent descriptor and eval case.
2. Select candidate guidance fields relevant to the requested artifact.
3. Compose generated artifact text for the existing `optimizespec` agent.
4. Score required-term coverage.
5. Build ASI with missing terms and field-specific feedback.
6. Persist rollout artifacts.

## Trace Capture

The deterministic executor captures fixture path, requested artifact type, selected candidate fields, required terms, generated text, usage estimates, and errors. A future live executor should capture the Managed Agent session events that occur while an agent uses the skills to create the artifacts.

## Scoring and ASI

The scorer computes required-term coverage for artifact-generation cases. The system-loop case uses a command-success scorer: it requires successful `generate`, `eval`, and `optimize` execution plus output artifacts. ASI includes `Input`, `Expected`, `Actual`, `Feedback`, `Error`, `Agent Trajectory`, `scores`, and field-specific diagnostics for every mutable guidance field.

## GEPA Configuration

The optimizer uses train/val cases from `eval-cases.yaml`, a required-term scorer, objective/background text specific to the existing `optimizespec` agent, round-robin field selection, and run directory capture.

## Risks and Blockers

- This is not a live end-to-end skill execution test; it is a deterministic meta-eval over artifact generation quality.
- Live skill execution requires a Claude Managed Agent runner that can invoke the local skills in a workspace.
