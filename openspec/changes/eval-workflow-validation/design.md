## Context

The current repo has a working GEPA self-improvement core in `src/agent_gepa/self_improvement.py`, CLI entry points for direct eval, compare, and optimize, and fixture changes under `gepa-evals/changes/`. The existing `agent-gepa-managed-agent-eval-generator` fixture already proves a narrow system loop: generate artifacts, run direct eval, run GEPA with a tiny budget, and score 1.0 when the loop emits the expected output files.

The validation gap is confidence. Static skill validation and one happy-path fixture do not prove that the skill workflow can reliably handle realistic Claude Managed Agent repos, incomplete user inputs, artifact quality expectations, optimizer execution, and failure modes. This change adds a validation layer around the skill pack so validation readiness is measured by runnable evidence rather than subjective review.

Constraints:

- Runtime scope remains Claude Managed Agents only.
- Validation should reuse the existing GEPA self-improvement primitives instead of adding a separate optimizer stack.
- Live Anthropic calls must be optional for routine tests; local fixtures should cover deterministic smoke paths.
- A successful optimization-loop eval scores 1.0 only when the actual system runs end to end and persists expected evidence.

## Goals / Non-Goals

**Goals:**

- Provide representative positive and negative Claude Managed Agent fixtures for validating the GEPA eval skills.
- Add a harness that invokes the skill workflow against fixture inputs and records generated artifacts, command logs, summaries, and failures.
- Score generated artifacts for required validation content, including eval contracts, design-level runner details, ASI, scorer semantics, GEPA invocation, compare paths, and limitations.
- Enforce hard contracts only for machine-consumed boundaries: fixture metadata, eval cases, candidate fields, rollout results, score results, ASI, command evidence, and run summaries.
- Score agent-written proposal, design, spec, task, and apply-plan prose semantically so useful variation is allowed while critical omissions are still caught.
- Verify applied systems by running direct eval, compare, and optimize commands against generated artifacts.
- Preserve inspectable rollout evidence: `summary.json`, `comparison.json`, GEPA candidate outputs, command logs, `side_info.json`, and generated files.
- Document validation criteria and the commands needed to reproduce the evidence.

**Non-Goals:**

- Add support for Codex, generic shell agents, browser agents, or other non-Claude runtimes.
- Guarantee that every optimized candidate improves live production behavior; this validation checks the workflow and optimizer mechanics.
- Replace OpenSpec or change the OpenSpec artifact graph.
- Build a hosted eval service or persistent dashboard.
- Require live API credentials for the full default test suite.

## Decisions

### Use the existing self-improvement core as the validation runtime

The harness will use `EvalCase`, `RolloutResult`, `ScoreResult`, `evaluate_candidate`, `compare_candidates`, and `optimize_candidate` from `src/agent_gepa/self_improvement.py`. Fixture-specific behavior will live in small rollout executors and custom scorers.

Rationale: this avoids two competing eval models and keeps ASI, persistence, and GEPA invocation identical between package features and eval workflow validation.

Alternative considered: create a separate validation runner under `gepa-evals/`. That would make fixtures easier to isolate, but it risks validating a different system than the one users will actually apply.

### Treat fixture agents as versioned validation inputs

Add a fixture directory structure that can represent multiple Claude Managed Agent targets:

- `gepa-evals/fixtures/agents/<fixture-id>/agent.yaml`
- `gepa-evals/fixtures/agents/<fixture-id>/request.md`
- optional source snippets, expected generated artifacts, and failure notes

Each fixture should declare runtime type, relevant source files, existing commands, candidate fields, expected skill workflow behavior, and whether live credentials are required.

Rationale: fixture agents become the stable benchmark for validation confidence and can grow without changing the core eval API.

Alternative considered: encode all fixtures directly in Python tests. That is simpler initially but makes it harder for agents and humans to inspect what the workflow is supposed to learn from each target.

### Add a skill execution harness with command-level evidence

The harness should run the GEPA eval workflow in an isolated output directory for each fixture. At minimum it should support:

- `generate`: produce proposal, design, specs, tasks, eval cases, seed candidate, and apply plan from fixture input.
- `eval`: run artifact quality and system-loop eval cases against a candidate.
- `compare`: compare baseline and candidate guidance across the same cases.
- `optimize`: invoke GEPA with `max_metric_calls` controls and persist optimizer artifacts.
- `verify`: assert expected files, scores, and failure behavior.

The harness can start as a Python module under `gepa-evals/eval_validation/` or as fixture-specific scripts, but common command behavior should converge on reusable helpers once more than one fixture exists.

Rationale: validation evidence needs repeatable commands and durable artifacts, not just unit assertions.

Alternative considered: manually run the skills in the interactive agent session and inspect output. That is useful for development but not sufficient for regression testing or readiness claims.

### Score generated artifacts semantically and structurally

Artifact quality scorers should combine required-term checks, section checks, YAML/schema checks, and targeted semantic checks. The first scorer set should cover:

- Proposal: states target agent, eval objective, input/output contract, numeric and qualitative scoring.
- Design: explains actual eval runner invocation, rollout lifecycle, scorer execution, ASI construction, optimizer invocation, compare behavior, and credential assumptions.
- Specs and tasks: include SHALL requirements and implementation tasks for direct eval, rollouts, scorers, ASI, GEPA optimize, compare, and validation.
- Eval cases: parse as YAML, include train/val or train/test splits, expected outputs, scorer definitions, and metadata needed by custom scorers.
- Apply output: exposes runnable commands and writes expected evidence artifacts.

Rationale: validation readiness depends on generated artifacts containing the operational details a coding agent needs, especially the eval runner and optimizer mechanics.

Alternative considered: use only exact golden-file matching. That is brittle for agent-generated artifacts and discourages useful variation.

### Separate hard data contracts from semantic prose contracts

The validation layer should use strict typed contracts for data and execution surfaces that downstream code consumes:

- Fixture metadata
- Eval cases and scorer definitions
- Candidate field maps
- Rollout results
- Score results
- Actionable Side Information
- Command evidence
- Run summaries and comparison summaries

Generated proposal, design, spec, task, and apply-plan text should not be locked to golden files or exact phrasing. Those artifacts should be scored by required concepts, structural sections, semantic fit to the fixture, and critical omissions.

Rationale: the optimizer and harness need reliable structured data, but agent-written prose should stay flexible enough to adapt to different repos and still be useful.

Alternative considered: define rigid schemas for every generated artifact. That would simplify validation but would overfit the skill workflow to one template and make it worse at handling real user repos.

### Make the optimization-loop scorer binary at the system boundary

The applied system scorer should assign 1.0 only if the actual loop completes:

1. Generate or apply artifacts for the target fixture.
2. Run direct eval and write `summary.json`.
3. Run GEPA optimize with a small budget and write optimizer evidence such as `candidates.json` and `run_log.txt`.
4. Optionally run compare and write `comparison.json`.
5. Confirm command return codes are zero and required files exist.

Any missing required artifact, nonzero command, unhandled exception, or unsupported runtime assumption scores 0.0 with ASI that includes command tails and missing files.

Rationale: this matches the user's desired eval: if the actual system runs and performs an optimization loop, it scores 1.0.

Alternative considered: partially credit command progress. Partial scores are useful for artifact quality, but the validation gate should remain binary so it cannot hide a broken optimizer path.

### Keep live Managed Agent runs separate from default deterministic validation

Default CI and local smoke tests should use deterministic fixture executors. Live Managed Agent validation should be opt-in through an environment flag and require `ANTHROPIC_API_KEY`.

Rationale: eval workflow validation should be reproducible and affordable by default, while still allowing a manual live gate before release.

Alternative considered: require live API calls for all eval workflow validation. That would better simulate production but makes the test suite expensive, slower, and unavailable to contributors without credentials.

### Negative fixtures must be first-class eval cases

Negative fixtures should check that the workflow asks for clarification or fails usefully when:

- Eval input/output pairs are missing.
- Numeric or qualitative scoring is ambiguous.
- The fixture claims an unsupported runtime.
- Existing agent invocation details are absent.
- Required credentials or resources are impossible to infer.
- Generated eval cases cannot be parsed or scored.

Rationale: a reliable skill should not confidently invent an eval system when the information needed for GEPA is missing.

Alternative considered: rely on code review to catch unclear behavior. That does not scale and misses regressions in agent-facing instructions.

## Eval Runner and Optimizer Flow

The eval workflow validation runner should use the same lifecycle for every positive fixture:

1. Load fixture metadata, seed candidate, and eval cases.
2. Select mutable candidate fields, usually guidance fields for fixture analysis, proposal, design, specs/tasks, apply, scoring, and ASI.
3. For each eval case, call the fixture rollout executor with the candidate and timeout.
4. The executor either renders deterministic generated artifacts or invokes the generated system commands in an isolated run directory.
5. Score the rollout using built-in or custom scorers.
6. Build ASI with input, expected output, actual output, feedback, errors, command traces, generated files, usage, and field-specific feedback.
7. Persist each rollout under `rollouts/<candidate-id>/<case-id>/`.
8. For direct eval, write `summary.json`.
9. For compare, evaluate baseline and candidate, then write `comparison.json` with score deltas and candidate diffs.
10. For optimize, call `optimize_candidate(...)`, which wraps GEPA `optimize_anything(...)` with `GEPAEvaluator`, train/val splits, objective, background, reflection model, `max_metric_calls`, run dir, and custom scorers.

The user-facing validation commands should be small and explicit. The exact command names can be finalized in tasks, but the shape should be:

```bash
python -m agent_gepa.eval_validation generate --fixture <fixture-id> --output-dir <run-dir>/generated
python -m agent_gepa.eval_validation eval --fixture <fixture-id> --candidate <candidate.yaml> --run-dir <run-dir>/eval
python -m agent_gepa.eval_validation compare --fixture <fixture-id> --baseline <seed.yaml> --candidate <candidate.yaml> --run-dir <run-dir>/compare
python -m agent_gepa.eval_validation optimize --fixture <fixture-id> --candidate <seed.yaml> --max-metric-calls 1 --run-dir <run-dir>/optimize
python -m agent_gepa.eval_validation verify --run-dir <run-dir>
```

For generated applied systems, the harness should also support invoking fixture-specific commands, such as the existing `agent_eval_generator.py generate`, `eval`, and `optimize` operations, so the validation can prove that apply output is actually runnable.

## Risks / Trade-offs

- [Risk] Required-term scoring can reward keyword stuffing. -> Mitigation: combine required terms with YAML parsing, section checks, command evidence, and binary system-loop scoring.
- [Risk] Deterministic fixtures may not capture live Managed Agent failure modes. -> Mitigation: add an opt-in live fixture gate and document that broader release should include one successful live run.
- [Risk] GEPA with `max_metric_calls=1` proves wiring but not meaningful optimization. -> Mitigation: use the small budget for fast system-loop validation and add a larger optional quality run for release evidence.
- [Risk] Harness code can duplicate fixture-specific scripts. -> Mitigation: start with explicit fixture scripts where useful, then extract shared helpers once a second positive fixture and one negative fixture exist.
- [Risk] Negative fixture expected behavior can be subjective. -> Mitigation: encode expected outcomes as concrete assertions: clarification marker, unsupported runtime marker, nonzero score behavior, or missing-info error.
- [Risk] Launch docs may drift from commands. -> Mitigation: tests should execute the documented smoke commands or generate command snippets from the same harness entry points.

## Migration Plan

1. Add the eval workflow validation fixtures and harness without changing existing CLI behavior.
2. Wire tests around deterministic fixture commands and artifact scorers.
3. Add optional live Managed Agent validation behind an explicit environment flag.
4. Document validation commands and evidence paths.
5. Keep the existing `gepa-evals/changes/*` examples working throughout; if harness entry points replace fixture-specific scripts, leave compatibility wrappers or update docs and tests together.

Rollback is straightforward because this change adds validation surfaces rather than modifying the Managed Agent runtime contract. If a new harness path is unstable, disable its validation gate while retaining the existing self-improvement CLI and fixture scripts.

## Open Questions

- Should eval workflow validation live under `src/agent_gepa/eval_validation.py` for package CLI reuse, or under `gepa-evals/eval_validation/` as repo-local validation tooling?
- What is the minimum number of positive fixtures required for eval validation: one realistic fixture plus the existing package optimizer, or two distinct Claude Managed Agent fixtures?
- Should the optional live gate be required before broader release, or only before claiming production readiness?
- How strict should artifact semantic scoring be before it starts blocking useful variation in generated specs and designs?
