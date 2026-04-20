## 1. Candidate compiler foundation

- [x] 1.1 Define the full GEPA-facing `dict[str, str]` candidate schema for `system_prompt`, `task_prompt`, `outcome_rubric`, `skills`, `environment_spec`, and `subagent_specs`
- [x] 1.2 Add typed internal models for compiled candidate data, including prompt fields, skills, environment config, and subagent specs
- [x] 1.3 Implement Anthropic structured-output parsing for raw candidate compilation using a stable schema and typed parsed result
- [x] 1.4 Implement canonicalization of structured fields after structured-output parsing and use canonical text for candidate identity and debugging
- [x] 1.5 Add tests for successful compilation, canonicalization, and scored failures when structured-output parsing cannot produce a valid typed candidate

## 2. Full-surface runtime compilation

- [x] 2.1 Refactor the runtime so every candidate field materially affects managed-agent execution
- [x] 2.2 Implement hybrid candidate-defined skills resolution so reusable skill refs are attached directly and missing custom skills are created through the Skills API before attachment to the primary agent or compiled subagents
- [x] 2.3 Implement candidate-defined environment compilation into fresh Anthropic environments per evaluation
- [x] 2.4 Replace the current subagent guardrail with real callable-agent creation and attachment from `subagent_specs`
- [x] 2.5 Add runtime tests and smoke checks that verify non-prompt field changes alter the compiled execution path
- [x] 2.6 Remove or reduce misleading successful-run archive warnings such as `skipped session archive because session status was running` when the session later settles to `idle`

## 3. Evaluator feedback and reflection guidance

- [x] 3.1 Extend evaluator `side_info` to include structured-output parse failures, compile-stage failures, and field-specific diagnostics
- [x] 3.2 Add field-specific reflection prompt templates for prompt fields versus structured config fields
- [x] 3.3 Ensure prompt and structured fields can be mutated independently without regenerating unrelated candidate fields
- [x] 3.4 Record comparison-friendly artifacts showing raw candidate text, compiled canonical forms, and field-level feedback
- [x] 3.5 Add tests that verify invalid structured candidates become informative scored failures rather than uncaught exceptions

## 4. Benchmark and optimization defaults

- [x] 4.1 Expand the benchmark with tasks that make skills, environment configuration, and subagent delegation materially relevant
- [x] 4.2 Preserve the existing simple file-output tasks as a regression subset in the train and validation suite
- [x] 4.3 Set default optimization budgets and per-session runtime ceilings high enough for full-surface search to move beyond the seed candidate
- [x] 4.4 Update the compare workflow to report full-surface candidate diffs and per-task score deltas on the expanded benchmark
- [x] 4.5 Add a documented small-budget smoke run and a larger default run path for full-surface optimization

## 5. End-to-end verification

- [x] 5.1 Run targeted live evaluations that change one structured field at a time and verify the runtime behavior changes accordingly, including create-versus-reuse behavior for candidate-defined skills
- [ ] 5.2 Run an end-to-end `optimize_anything()` job on the expanded benchmark and verify GEPA accepts at least one non-seed candidate
- [ ] 5.3 Capture and review the input candidate, final candidate, and evaluation deltas from the verification run, incorporating the follow-up context recorded in `manual-test-findings.md`
- [x] 5.4 Update project documentation to explain the structured-output compiler path, required Anthropic features, and operator workflow for full-surface runs
