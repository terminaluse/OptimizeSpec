## 1. Workflow Structure and References

- [x] 1.1 Decide and document the repo-local workflow directory convention for self-improvement changes, including the default change path and artifact filenames
- [x] 1.2 Create the self-improvement skill pack skeleton for new/start, continue, apply, and verification workflows using concise trigger descriptions
- [x] 1.3 Add shared reference material that explains OpenSpec as the motivating artifact-guided workflow without requiring OpenSpec feature parity
- [x] 1.4 Add shared reference material for GEPA reflective evolution, Actionable Side Information, `optimize_anything(...)`, and this repo's candidate/evaluator/optimizer patterns
- [x] 1.5 Add shared reference material for Claude Managed Agents concepts needed by eval runners, including Agents, Environments, Sessions, resources, event streams, skills, and cleanup

## 2. Artifact Templates

- [x] 2.1 Implement an eval proposal template that captures target agent context, improvement target, input/output examples, numeric scoring intent, qualitative rubric, and unresolved discovery questions
- [x] 2.2 Implement a design template that requires target Managed Agent code discovery, runner invocation surface, rollout lifecycle, trace capture, ASI mapping, candidate surface, and optimizer configuration
- [x] 2.3 Implement spec templates and guidance for candidate surface, ASI contract, eval dataset and scorers, Managed Agent trace runtime, reflective optimization workflow, and apply workflow
- [x] 2.4 Implement a task template that orders implementation around candidate schema, eval case schema, runner, rollout, scorer, ASI builder, optimizer, commands, and validation
- [x] 2.5 Add examples showing proposals where users know the scorer and proposals where scorer or eval examples need collaborative discovery

## 3. Planning Skill Behavior

- [x] 3.1 Implement the new/start skill so it creates an eval change and drafts or prompts for the proposal without inventing missing target-agent or scoring details
- [x] 3.2 Implement the continue skill so it creates exactly one next artifact from completed dependencies and preserves the artifact order
- [x] 3.3 Ensure the design-generation path instructs the coding agent to inspect the target repo before proposing Managed Agent eval architecture
- [x] 3.4 Ensure the design-generation path records direct eval, optimize, compare, and candidate-inspection invocation forms appropriate to the target repo
- [x] 3.5 Ensure planning skills record unsupported non-Managed-Agent runtimes as blocked or out of scope for v1

## 4. Eval Data and Candidate Surface

- [x] 4.1 Define a portable eval case schema for inputs, expected outputs or output-shape expectations, deterministic scorer configuration, qualitative rubric, split, and metadata
- [x] 4.2 Define how approved eval examples compile into GEPA train and validation datasets, including behavior when there are too few examples for a split
- [x] 4.3 Define a target-repo-adaptable candidate schema for mutable Claude Managed Agent fields such as prompts, instructions, skills, tools, resources, environment, or subagents
- [x] 4.4 Implement seed/current candidate loading and candidate inspection output for the generated runner
- [x] 4.5 Add validation for missing, malformed, or unsupported eval cases and candidate fields

## 5. Managed Agent Runner and Rollouts

- [x] 5.1 Implement the direct eval runner operation that loads a change, selected eval cases, and a candidate, then evaluates without GEPA search
- [x] 5.2 Implement the rollout lifecycle for one candidate and one eval case: candidate compile, resource preparation, Managed Agent session start, input delivery, event streaming or polling, output collection, scoring, ASI construction, persistence, and cleanup
- [x] 5.3 Integrate rollout execution with existing target-repo Managed Agent factories or entrypoints instead of creating an unrelated duplicate path
- [x] 5.4 Capture Managed Agent runtime identifiers and traces, including agent ID and version, environment ID, session ID, event types, tool-use summaries, usage, generated files, errors, and cleanup results
- [x] 5.5 Implement timeout, terminated-session, required-action, and runtime-error handling so failed rollouts become scored failures with useful diagnostics

## 6. Scoring and ASI

- [x] 6.1 Implement deterministic scorer templates for exact match, structured JSON match, file existence/content checks, and custom predicate-style checks
- [x] 6.2 Implement qualitative rubric scoring support when deterministic scoring cannot capture the eval contract
- [x] 6.3 Implement the ASI builder with top-level fields for Input, Expected, Actual, Feedback, Error, Agent Trajectory, and higher-is-better scores
- [x] 6.4 Implement field-specific ASI keys for mutable candidate fields so GEPA reflection can target prompt, scorer, skill, environment, tool, resource, or subagent changes
- [x] 6.5 Persist ASI, scores, raw outputs, expected outputs, candidate snapshots, and runtime traces under stable run directories for every rollout

## 7. GEPA Optimizer Operations

- [x] 7.1 Implement the optimize operation that invokes GEPA with seed candidate, train and validation sets, evaluator, objective text, background text, reflection configuration, metric-call budget, runtime limit, and run directory
- [x] 7.2 Implement per-field reflection prompt templates that consume ASI and preserve successful behaviors while targeting observed failure patterns
- [x] 7.3 Implement component selection configuration for independent fields and document how tightly coupled fields are updated together or deferred
- [x] 7.4 Implement the compare operation that evaluates baseline and optimized or user-provided candidates on the same eval cases and reports aggregate and per-case deltas
- [x] 7.5 Ensure optimize and compare persist best candidate, candidate diffs, GEPA logs, score summaries, and validation results

## 8. Apply Skill

- [x] 8.1 Implement the apply skill so it refuses to run when proposal, design, specs, or tasks are missing
- [x] 8.2 Make the apply skill read all completed artifacts and summarize the planned target-repo changes before editing files
- [x] 8.3 Make the apply skill inspect the target repo's language, commands, dependencies, Managed Agent setup, and existing test conventions before implementation
- [x] 8.4 Make the apply skill add the generated runner, scorer, ASI, and optimizer code using the target repo's conventions
- [x] 8.5 Make the apply skill mark tasks complete incrementally only after implementation and local verification for each task

## 9. Validation and Documentation

- [x] 9.1 Add skill validation checks for frontmatter, trigger descriptions, required references, templates, and one-level progressive-disclosure paths
- [x] 9.2 Add fixture scenarios for proposal creation with complete examples, proposal creation with unknown scorer details, and design creation after Managed Agent repo inspection
- [x] 9.3 Add fixture scenarios for apply creating runnable direct eval and optimize operations in a small Claude Managed Agents target repo
- [x] 9.4 Add tests or smoke checks that verify direct eval, failed rollout ASI, field-specific ASI, optimize invocation, and compare output
- [x] 9.5 Document the operator workflow, required environment variables, expected commands, run artifact layout, and known v1 limitations
