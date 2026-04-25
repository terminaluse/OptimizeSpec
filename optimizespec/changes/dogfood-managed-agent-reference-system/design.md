## Context

The target is the Python Claude Managed Agent reference harness under `examples/py-claude-managed-agent/`, driven by the `optimizespec-managed-agent` fixture. Runtime inference is high confidence because the fixture declares Claude Managed Agents, names the mutable candidate fields, and points to the existing Python runtime, evaluator, optimizer, task, and CLI modules.

The generated dogfood system is not product source. It lives under `runs/optimizespec-dogfood/dogfood-managed-agent-reference-system` because this repo keeps generated optimization systems out of committed examples. The system still needs to be real and runnable: it should import the existing harness and expose the expected operations.

## Optimization System Location

The proposal's create-new decision stands.

- Implementation path: `runs/optimizespec-dogfood/dogfood-managed-agent-reference-system`
- Runtime output path: `runs/optimizespec-dogfood/dogfood-managed-agent-reference-system/runs/<run-id>/`
- Existing code to reuse: `optimizespec.eval_validation` for fixture loading, artifact generation, direct eval, compare, optimize, and verification.
- Dependency boundary: add the repo root and `examples/py-claude-managed-agent/src` to `sys.path` inside the generated dogfood script so it runs from the source checkout without packaging a second runtime.

## Runner Invocation

The generated system should expose:

- `python managed_agent_dogfood.py show-candidate`
- `python managed_agent_dogfood.py direct-eval --run-dir <path>`
- `python managed_agent_dogfood.py compare --run-dir <path>`
- `python managed_agent_dogfood.py optimize --run-dir <path> --max-metric-calls 1`
- `python managed_agent_dogfood.py verify --run-dir <path>`
- `python managed_agent_dogfood.py run-all --run-dir <path>`

`run-all` should execute generate, direct eval, compare, optimize, and verify in that order.

## Contract References

- Runner: `references/core/runner-contract.md`
- Evidence: `references/core/eval-system-evidence.md`
- Grader: `references/core/grader-contract.md`
- ASI: `references/core/asi-contract.md`
- Candidate surface: `references/core/candidate-surface.md`
- Optimizer: `references/core/optimizer-contract.md`
- Verification: `references/core/verification-contract.md`
- Runtime: `references/runtimes/claude-managed-agent/managed-agents-runtime-contract.md`
- Managed Agent runner: `references/runtimes/claude-managed-agent/managed-agents-runner.md`
- Runtime ASI: `references/runtimes/claude-managed-agent/scorers-and-asi.md`

## Candidate Surface

The target fixture describes these Claude Managed Agent runtime fields:

- `system_prompt`: instruction content compiled into the agent behavior.
- `task_prompt`: task framing for reference eval cases.
- `outcome_rubric`: expected outcome and scorer guidance.
- `skills`: skill references or custom skill materialization.
- `environment_spec`: environment resources and permissions.
- `subagent_specs`: optional subagent configuration guarded by preview support.

The generated deterministic dogfood system reuses `optimizespec.eval_validation`, whose optimizer candidate is the workflow-guidance surface: `fixture_analysis_guidance`, `proposal_generation_guidance`, `design_generation_guidance`, `spec_task_generation_guidance`, `apply_generation_guidance`, and `scoring_asi_guidance`. `show-candidate` should expose both the target runtime surface and the optimizer guidance candidate so reviewers do not conflate them.

## Eval Design

- Eval category: system and optimizer-acceptance.
- Real task distribution: fixture-generated proposal/design/spec/task cases plus command-loop cases from `optimizespec.eval_validation`.
- Edge cases: missing ASI, missing judge records, missing optimizer lineage, aggregate-only scoring, unsupported runtime, and missing promotion evidence.
- Failure modes: generated script cannot import the harness; commands write only aggregate scores; optimizer completes without lineage; verification confuses deterministic machinery with live agent quality.
- Split strategy: use fixture defaults; train cases feed direct eval and optimizer reflection, validation cases feed comparison and promotion checks.
- What this eval does not measure: live API behavior unless a separate live smoke is run.

## Rollout Lifecycle

One deterministic rollout loads the fixture, loads or defaults a candidate, loads fixture eval cases, executes the `EvalValidationExecutor`, scores the result, builds ASI, persists rollout files, and updates the evidence ledger. For live runs later, the existing harness is responsible for creating or reusing Managed Agent resources, environments, sessions, events, and cleanup.

## Runtime-Specific Plan

For Claude Managed Agents, reuse the existing Python harness rather than rebuilding Agent, Environment, Session, resource, event streaming, tool, skill, MCP, permission, and cleanup logic. The generated dogfood system is a narrow command adapter over that harness.

Deterministic commands must not require `ANTHROPIC_API_KEY`. If a live option is added, it should explicitly load `.env`, require credentials, and label the result as live evidence.

## Trace Capture

Use the reference harness evidence files for input, expected output, actual output, final answer, generated files, event summaries, runtime ids, usage, errors, command arguments, return codes, and elapsed time. The generated script should print concise JSON command results and let reviewers inspect the run directory.

## Evidence Ledger

The run directory must contain:

- `generated/proposal.md`
- `generated/design.md`
- `generated/specs/eval-validation-spec.md`
- `generated/tasks.md`
- `generated/eval-cases.yaml`
- `generated/seed-candidate.yaml`
- `generated/apply-plan.md`
- `eval/summary.json`
- `compare/comparison.json`
- `optimize/candidates.json`
- `optimize/run_log.txt`
- `evidence/manifest.json`
- `evidence/candidate-registry.json`
- `evidence/evaluations/<candidate-id>/summary.json`
- `evidence/evaluations/<candidate-id>/cases/<case-id>/score.json`
- `evidence/evaluations/<candidate-id>/cases/<case-id>/judge.json`
- `evidence/evaluations/<candidate-id>/cases/<case-id>/side_info.json`
- `evidence/evaluations/<candidate-id>/cases/<case-id>/rollout.json`
- `evidence/comparisons/comparison.json`
- `evidence/optimizer/lineage.json`
- `evidence/optimizer/leaderboard.json`
- `evidence/optimizer/events.jsonl`
- `evidence/promotion.json`
- `verification/verification.json`

Verification fails when required records are missing.

## Scoring and ASI

Use `optimizespec.eval_validation.custom_scorers()` and the fixture default eval cases. ASI must include top-level input, expected, actual, feedback, errors, trajectory, runtime, scores, and field-specific feedback for mutable workflow-guidance candidate fields.

## Grading Strategy

- Grader type: deterministic/code.
- Why this grader is appropriate: the dogfood run checks generated artifacts, JSON evidence, and command behavior.
- Calibration examples: existing positive fixture and negative fixtures under `tests/fixtures/reference-agents/`.
- Reliability risks: a command adapter can pass import and command checks while leaving verification evidence incomplete.
- Human review triggers: any generated path outside `runs/`, any live quality claim, or any failed verification.

## GEPA Configuration

Use fixture default candidates and eval cases. For the dogfood run, use `max_metric_calls=1` to keep it fast and deterministic enough for local verification. Use the existing reflection model default from `eval_validation.cmd_optimize`; increase budget only for release-quality experiments.

## Optimizer Lineage

Reuse `eval_validation.write_optimizer_evidence` through `cmd_optimize`. The generated system must preserve selected candidate id, seed candidate, best candidate, reflection model, metric-call budget, leaderboard, events, and no-promotion or promotion decision.

## Optimizer Acceptance

- Optimized metric: verification success over required artifacts and evidence.
- Diagnostic metrics: direct eval mean score, compare candidate score, optimizer output presence, command log completeness.
- Guardrail metrics: no generated files outside the recorded path; no credential requirement for deterministic commands; no missing evidence records.
- Promotion rule: verification success with complete evidence.
- Regression tolerance: zero required evidence omissions.
- Required evidence: all files listed in the evidence ledger section.

## Verification Plan

Run the generated script with `run-all`, then inspect `verification/verification.json`. Also run `node bin/optimizespec.js validate dogfood-managed-agent-reference-system` from the repo root to validate planning artifacts. Deterministic success proves the system loop only; live Managed Agent quality improvement remains unclaimed unless a separate live run is executed.

## Risks and Blockers

- The TypeScript CLI does not implement apply; use `$optimizespec-apply` to build the harness adapter from these artifacts.
- Live Managed Agent checks require credentials and preview access.
- Generated output is ignored by git, so any reusable release dogfood script would need a separate product change.
