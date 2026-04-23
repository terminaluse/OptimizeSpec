## 1. Fixture Agent Inventory

- [ ] 1.1 Define the fixture metadata schema for Claude Managed Agent validation fixtures, including runtime, source references, commands, mutable candidate fields, credential requirements, and expected outputs.
- [ ] 1.2 Add one additional positive Claude Managed Agent fixture that differs from the existing managed-agent eval-generator fixture.
- [ ] 1.3 Add fixture expected-behavior files or metadata for generated artifacts, required commands, required run evidence, and qualitative rubric checks.
- [ ] 1.4 Add fixture loading validation that fails before execution when required metadata is missing or malformed.

## 2. Hard Contract Validation

- [ ] 2.1 Implement strict validation for machine-consumed fixture metadata.
- [ ] 2.2 Implement strict validation for eval-case YAML, scorer definitions, train/validation/test splits, and custom scorer references.
- [ ] 2.3 Implement strict validation for candidate field maps and mutable field declarations.
- [ ] 2.4 Implement strict validation for rollout result, score result, ASI, command evidence, summary, and comparison artifacts.
- [ ] 2.5 Add tests that malformed machine-consumed artifacts fail with actionable parser or schema diagnostics.

## 3. Launch-Alpha Harness

- [ ] 3.1 Add a launch-alpha harness entrypoint for `generate`, `eval`, `compare`, `optimize`, and `verify`.
- [ ] 3.2 Implement isolated run-directory layout for generated artifacts, direct eval, compare, optimize, verification, command logs, and rollouts.
- [ ] 3.3 Wire direct eval to reuse `evaluate_candidate(...)` from the self-improvement core.
- [ ] 3.4 Wire compare to reuse `compare_candidates(...)` and persist score deltas plus candidate diffs.
- [ ] 3.5 Wire optimize to reuse `optimize_candidate(...)` with configurable `max_metric_calls`, reflection model, run directory, and timeout.
- [ ] 3.6 Capture command arguments, return codes, stdout tails, stderr tails, elapsed time, generated files, and errors for every harness operation.
- [ ] 3.7 Add compatibility support for invoking fixture-specific generated-system commands when validation needs to prove applied output is runnable.

## 4. Semantic Artifact Scoring

- [ ] 4.1 Implement proposal scoring for target-agent identification, eval objective, input/output examples, numeric scoring, qualitative scoring, and discovery questions.
- [ ] 4.2 Implement design scoring for eval runner invocation, rollout lifecycle, scorer execution, ASI construction, GEPA optimization, compare behavior, persistence, cleanup, and credentials.
- [ ] 4.3 Implement spec and task scoring for required subsystem coverage without requiring exact wording or golden-file equality.
- [ ] 4.4 Implement eval-case artifact scoring that parses YAML and checks inputs, expected outputs, scorers, splits, metadata, and custom scorer references.
- [ ] 4.5 Implement apply-plan scoring for runnable commands, expected evidence artifacts, unsupported-runtime handling, and target-repo fit.
- [ ] 4.6 Add tests showing semantically valid prose can pass with different wording while launch-critical omissions fail.

## 5. Optimization-Loop Validation

- [ ] 5.1 Implement the binary system-loop scorer that returns 1.0 only when generation or apply, direct eval, GEPA optimize, command return codes, and required evidence files all succeed.
- [ ] 5.2 Persist `summary.json`, per-case rollout files, `side_info.json`, candidate snapshots, and score files for direct eval validation.
- [ ] 5.3 Persist `comparison.json` with baseline scores, candidate scores, deltas, and candidate diffs for compare validation.
- [ ] 5.4 Persist optimizer evidence including GEPA candidate outputs and run logs for optimize validation.
- [ ] 5.5 Include command traces, missing files, generated paths, optimizer outputs, and failures in ASI for system-loop eval cases.
- [ ] 5.6 Add a small-budget deterministic optimization smoke test with `max_metric_calls=1`.
- [ ] 5.7 Add an optional larger-budget release validation path that reports whether optimized candidates improve validation or test scores.

## 6. Negative Fixture Validation

- [ ] 6.1 Add a negative fixture with missing eval input and expected output details.
- [ ] 6.2 Add a negative fixture with missing numeric or qualitative scoring guidance.
- [ ] 6.3 Add a negative fixture for an unsupported non-Claude runtime.
- [ ] 6.4 Add a negative fixture with insufficient invocation or source details for designing an eval runner.
- [ ] 6.5 Implement negative-fixture scorers that award credit for clarification, blocked status, unsupported-runtime status, or useful failure diagnostics.
- [ ] 6.6 Add tests that negative fixtures fail usefully and that false success is scored as failure.

## 7. Live Managed Agent Gate

- [ ] 7.1 Add an opt-in environment flag for live Claude Managed Agent validation.
- [ ] 7.2 Require `ANTHROPIC_API_KEY` before live fixture execution starts.
- [ ] 7.3 Ensure deterministic validation remains the default path without live credentials.
- [ ] 7.4 Persist live-run evidence separately from deterministic smoke artifacts.

## 8. Documentation and Verification

- [ ] 8.1 Document alpha launch readiness criteria, required fixtures, required commands, required artifacts, and passing thresholds.
- [ ] 8.2 Document deterministic smoke commands for generation, direct eval, compare, optimize, and verify.
- [ ] 8.3 Document optional live Managed Agent validation commands, credentials, expected costs, and evidence paths.
- [ ] 8.4 Document current limitations, including Claude Managed Agent-only support and deterministic fixture limits.
- [ ] 8.5 Add tests or smoke checks that execute the documented deterministic commands.
- [ ] 8.6 Run the full test suite and record the validation commands used before marking the change complete.
