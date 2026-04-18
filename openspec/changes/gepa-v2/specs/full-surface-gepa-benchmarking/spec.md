## ADDED Requirements

### Requirement: Benchmark suite exercises the full candidate surface
The benchmark SHALL include tasks where prompts, environment configuration, skills, and subagent configuration can each materially influence task outcomes.

#### Scenario: Benchmark is used for optimization
- **WHEN** GEPA evaluates candidates on the train and validation suites
- **THEN** the suite includes tasks that can reward changes outside the prompt fields alone

### Requirement: Benchmark preserves a simple regression subset
The benchmark SHALL retain a stable subset of simple tasks that catch regressions in basic file-output correctness.

#### Scenario: Runtime change affects simple tasks
- **WHEN** a new candidate or runtime change regresses basic output formatting or file-writing behavior
- **THEN** the simple regression tasks expose the regression in evaluation results

### Requirement: Default optimization budgets match the benchmark size
The system SHALL use optimization and per-session runtime defaults that allow GEPA to search beyond the seed candidate on the benchmark.

#### Scenario: Operator runs the default compare workflow
- **WHEN** the default end-to-end optimization command is executed
- **THEN** the configured metric-call budget and session runtime ceiling are high enough for GEPA to evaluate mutated candidates

### Requirement: Comparison outputs show full-surface candidate changes
The system SHALL record and report the input candidate, final candidate, and per-task evaluation deltas for benchmark runs.

#### Scenario: Full-surface optimization finishes
- **WHEN** an optimization run completes
- **THEN** the resulting artifacts make it possible to inspect which fields changed and how those changes affected evaluation scores
