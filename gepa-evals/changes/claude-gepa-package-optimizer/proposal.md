## Target Agent

- Name: `claude-gepa-package-guidance`
- Runtime: Claude Managed Agents in live use; local fixture executor for credential-free package optimizer smoke tests
- Invocation: `python gepa-evals/changes/claude-gepa-package-optimizer/package_optimizer.py <command>`
- Constraints: v1 remains focused on Claude Managed Agents and GEPA `optimize_anything(...)`; local smoke runs do not call Anthropic APIs

## Improvement Target

Optimize the text guidance a package-maintenance agent uses when explaining and operating this `claude-gepa` package. The optimized candidate should help an agent explain the package purpose, GEPA boundary, eval workflow, rollout lifecycle, ASI requirements, commands, verification, and v1 runtime limits accurately.

## Candidate Surface

- `package_summary`: Explains the package purpose and GEPA-facing boundary.
- `eval_workflow`: Explains direct eval, optimize, compare, and candidate-inspection operations.
- `rollout_lifecycle`: Explains candidate x eval case rollout execution.
- `asi_guidance`: Explains required Actionable Side Information.
- `verification_guidance`: Explains validation and artifact inspection.
- `v1_limitations`: Explains current runtime and live-credential limits.

## Eval Examples

### Example: package-purpose

- Input: "Explain what this package is for and how GEPA interacts with it."
- Expected: Answer should mention GEPA, Claude Managed Agents, `dict[str, str]`, evaluator, and `side_info`.
- Split: train

### Example: workflow-commands

- Input: "How do I run direct eval, optimization, comparison, and inspect the candidate?"
- Expected: Answer should mention `self-eval`, `self-optimize`, `self-compare`, `self-show-candidate`, and `run-dir`.
- Split: train

### Example: asi-contract

- Input: "What should Actionable Side Information contain for reflection?"
- Expected: Answer should mention `Input`, `Expected`, `Actual`, `Feedback`, `Error`, `Agent Trajectory`, `scores`, and field-specific diagnostics.
- Split: train

### Example: rollout-lifecycle

- Input: "What is one rollout in this package optimizer?"
- Expected: Answer should mention candidate, eval case, Managed Agent session, trace capture, scoring, ASI, persistence, and cleanup.
- Split: val

### Example: v1-limits

- Input: "What are the v1 limitations and live-run requirements?"
- Expected: Answer should mention Claude Managed Agents only, other runtimes out of scope, `ANTHROPIC_API_KEY`, direct eval first, and small budgets.
- Split: val

## Scoring

- Numeric score range: `0.0` to `1.0`
- High score means: all required terms for the eval case are present in the generated answer.
- Partial score means: some required terms are present and missing terms are listed in ASI.
- Failing score means: no required terms are present or the rollout errors.
- Deterministic scorer: required-term coverage scorer.
- Qualitative rubric: Answer should be accurate, concise, and operationally useful for a coding agent maintaining this package.

## ASI Contract

Each rollout must include `Input`, `Expected`, `Actual`, `Feedback`, `Error`, `Agent Trajectory`, `scores`, runtime metadata, and field-specific feedback for the mutable package-guidance fields.

## Unknowns

- Live Claude Managed Agent integration can replace the local fixture executor later.
- Qualitative LLM grading is deferred; v1 uses deterministic required-term coverage.
