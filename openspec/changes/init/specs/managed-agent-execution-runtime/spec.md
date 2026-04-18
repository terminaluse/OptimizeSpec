## ADDED Requirements

### Requirement: Evaluator compiles text candidates into managed-agent executions
The system SHALL implement a GEPA evaluator that converts a GEPA-facing text candidate into the concrete Claude Managed Agents resources and session inputs needed for execution.

#### Scenario: Evaluator receives a candidate and task example
- **WHEN** GEPA calls the evaluator for a candidate and benchmark task
- **THEN** the evaluator compiles the candidate into an executable managed-agent run

### Requirement: Runtime executes the Anthropic session flow
The system SHALL execute the Claude Managed Agents workflow required by a task, including session startup, optional outcome definition, task input delivery, and artifact collection.

#### Scenario: Managed-agent run completes
- **WHEN** the Anthropic session reaches a terminal state
- **THEN** the runtime captures the deliverables, session metadata, and relevant execution diagnostics

### Requirement: Evaluator returns GEPA-compatible outputs
The system SHALL return either a numeric score or a `(score, side_info)` tuple from the evaluator in the format GEPA expects.

#### Scenario: Evaluation succeeds with diagnostics
- **WHEN** a candidate run completes and diagnostics are available
- **THEN** the evaluator returns a score plus structured side information instead of Anthropic-specific runtime objects

### Requirement: Runtime surfaces failures as evaluation results
The system SHALL convert compilation errors, session failures, and artifact retrieval failures into structured evaluation results that GEPA can consume.

#### Scenario: Runtime fails before task success
- **WHEN** the managed-agent compilation or session execution fails
- **THEN** the evaluator returns a scored failure result with diagnostic side information
