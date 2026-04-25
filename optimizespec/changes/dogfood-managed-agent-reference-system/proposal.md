## Target Agent

- Name: `optimizespec-managed-agent` reference agent.
- Runtime: Claude Managed Agents.
- Runtime evidence and confidence: High. `tests/fixtures/reference-agents/optimizespec-managed-agent/agent.yaml` declares `runtime: Claude Managed Agents`, names the candidate fields, and points to the Python runtime, evaluator, optimizer, and CLI modules under `examples/py-claude-managed-agent/src/optimizespec/`.
- Invocation: existing reference commands include `optimizespec eval-demo`, `optimizespec optimize-demo`, `optimizespec compare-demo`, and `optimizespec show-seed`; deterministic fixture commands are exposed by `python -m optimizespec.eval_validation`.
- Constraints: deterministic validation must run without live credentials; live Managed Agent checks require `ANTHROPIC_API_KEY` and preview access; generated dogfood systems should remain ignored test output for this product repo.

## Optimization System Location

- Decision: create a new generated dogfood system.
- Path: `runs/optimizespec-dogfood/dogfood-managed-agent-reference-system`
- Why this path fits the repo: this repository treats generated optimization systems and evidence ledgers as test output rather than product source. The path is ignored by `.gitignore`, so the dogfood system can be generated and executed without becoming a committed example.
- Existing agent code to reuse: `examples/py-claude-managed-agent/src/optimizespec/eval_validation.py`, `candidate.py`, `runtime.py`, `evaluator.py`, `optimizer.py`, `tasks.py`, and `self_improvement.py`.
- Existing tools, skills, MCP servers, env vars, or permissions to reuse: pytest, the editable Python reference harness, GEPA, fixture metadata, `.env` for `ANTHROPIC_API_KEY` when live checks are requested, and current Python module command conventions.
- Run outputs path: `runs/optimizespec-dogfood/dogfood-managed-agent-reference-system/runs/<run-id>/`.

## Improvement Target

Build a real dogfood optimization system that wraps the existing Claude Managed Agent reference harness and proves the OptimizeSpec workflow can produce runnable direct eval, compare, optimize, show-candidate, and verify operations with an inspectable evidence ledger.

## Success Criteria

- User outcome: a maintainer can run one generated dogfood system and inspect whether OptimizeSpec produced a usable optimization loop for the Managed Agent reference harness.
- Primary criterion: `verify` succeeds after the generated system runs direct eval, compare, and optimize against the `optimizespec-managed-agent` fixture.
- Secondary criteria: commands reuse existing harness modules, keep train and validation evidence separate, expose candidate fields, and write command evidence.
- Guardrails: do not copy a parallel Managed Agents runtime; do not require live credentials for deterministic checks; do not claim live agent-quality improvement from deterministic system-loop success.
- Acceptable threshold: direct eval writes summary, per-case score, rollout, and ASI evidence.
- Good threshold: direct eval, compare, optimize, show-candidate, and verify all run from the generated system and produce required evidence records.
- Promotion threshold: generated verification succeeds with no missing required evidence records and writes a promotion or no-promotion decision.
- Non-goals: changing product CLI behavior, adding a new supported runtime, or committing the generated dogfood system as a product example.
- Blind spots: deterministic fixture success does not prove live Claude Managed Agents API behavior.

## Draft Eval Contract

I inferred this from the user request. The user should confirm or correct it.

- Primary success: the generated dogfood system executes the reference harness end to end and `verify` reports success.
- Guardrails: generated implementation stays under the recorded path, imports the existing harness, and separates deterministic readiness from live improvement claims.
- Scoring: `0.0` to `1.0`, higher is better. The main score is verification completeness over required evidence files and command outputs.
- Grader: deterministic/code-based checks over command return codes, generated files, JSON evidence, and verification output.
- Open questions: whether this manual dogfood run should become a checked release script later.

## Candidate Surface

The target Claude Managed Agent fixture records these runtime candidate fields:

- `system_prompt`
- `task_prompt`
- `outcome_rubric`
- `skills`
- `environment_spec`
- `subagent_specs`

This dogfood system reuses `optimizespec.eval_validation`, whose deterministic optimizer mutates the workflow-guidance candidate fields used to generate and grade OptimizeSpec artifacts:

- `fixture_analysis_guidance`
- `proposal_generation_guidance`
- `design_generation_guidance`
- `spec_task_generation_guidance`
- `apply_generation_guidance`
- `scoring_asi_guidance`

## Eval Examples

### Example: deterministic-direct-eval

- Input: run direct eval for `optimizespec-managed-agent` with system-loop cases skipped.
- Expected: `eval/summary.json` plus evidence ledger score, rollout, side-info, and manifest records.
- Output shape: JSON summary and `evidence/evaluations/<candidate-id>/cases/<case-id>/...`.
- Split: train

### Example: deterministic-compare-optimize-verify

- Input: run compare, optimize with a one-call budget, then verify.
- Expected: `compare/comparison.json`, optimizer lineage, leaderboard, command logs, and successful verification output.
- Output shape: JSON comparison, optimizer files, `verification/verification.json`.
- Split: val

## Scoring

- Numeric score range: `0.0` to `1.0`.
- High score means: verification succeeds with all required evidence present.
- Partial score means: commands run but optional diagnostics, command logs, or lineage fields are incomplete.
- Failing score means: any command fails, required evidence is absent, or verification reports contract errors.
- Deterministic scorer: `optimizespec.eval_validation.verify_run_dir` plus file and JSON checks.
- Qualitative rubric: generated code should be understandable as a thin adapter over the real harness, not a placeholder scaffold.

## Grading Strategy

- Grader type: deterministic/code.
- Why this grader is appropriate: the dogfood objective is mostly structural and evidence-based.
- Calibration examples: positive fixture `optimizespec-managed-agent`; negative fixtures for missing ASI, missing judge records, missing optimizer lineage, and unsupported runtime.
- Reliability risks: a generic scaffold can pass CLI validation while failing the evidence contract.
- Human review triggers: any live Managed Agent claim, any generated code outside the recorded path, or any no-promotion decision caused by missing evidence.

## Optimizer Acceptance

- Optimized metric: verification completeness for the generated dogfood run.
- Diagnostic metrics: eval mean score, compare delta count, optimize best-candidate presence, command return codes, and missing evidence count.
- Guardrail metrics: generated path compliance, live credential independence for deterministic checks, and runtime reuse.
- Promotion rule: promote only if `verify` succeeds and required evidence records exist.
- Regression tolerance: zero missing required evidence records.
- Required evidence: run manifest, candidate registry, per-case scores, judge records when present, ASI, rollout records, comparison records, optimizer lineage, leaderboard, command logs, and promotion or no-promotion decision.

## Evidence Model

- Run manifest: fixture id, runtime, command, candidate ids, case ids, and output roots.
- Candidate versions: seed, baseline, candidate, and optimizer-selected workflow-guidance candidates with mutable fields.
- Per-case scoring records: score, feedback, scorer identity, split, errors, and expected/actual values.
- Judge records: deterministic grader metadata and structured output.
- ASI records: `Input`, `Expected`, `Actual`, `Feedback`, `Error`, `Agent Trajectory`, `Runtime`, `scores`, and field-specific feedback.
- Rollout evidence: fixture execution trace, generated files, runtime ids, usage, errors, and cleanup status.
- Optimizer lineage: selected candidate id, seed and best candidate summaries, reflection model, budget, and leaderboard.
- Promotion evidence: explicit promotion or no-promotion decision and rollback path.
- Unknowns: whether to convert this manual dogfood workflow into a release command.

## Contract References

- Criteria-first: `references/core/criteria-first-evals.md`
- Candidate surface: `references/core/candidate-surface.md`
- Grader: `references/core/grader-contract.md`
- Evidence: `references/core/eval-system-evidence.md`
- Runtime: `references/runtimes/claude-managed-agent/managed-agents-runtime-contract.md`
- Runtime runner: `references/runtimes/claude-managed-agent/managed-agents-runner.md`

## ASI Contract

The generated system must preserve the ASI shape emitted by the reference harness: `Input`, `Expected`, `Actual`, `Feedback`, `Error`, `Agent Trajectory`, `Runtime`, `scores`, and field-specific entries for the mutable workflow-guidance candidate fields.

## Unknowns

- Whether this should become an automated release dogfood script after the manual run proves useful.
