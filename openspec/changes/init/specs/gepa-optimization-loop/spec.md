## ADDED Requirements

### Requirement: Integration supports GEPA optimization modes
The system SHALL support GEPA single-task, multi-task, and generalization modes through the documented `dataset` and `valset` parameters.

#### Scenario: Train and validation sets are provided
- **WHEN** the optimization entrypoint receives both `dataset` and `valset`
- **THEN** the system runs GEPA in generalization mode rather than treating all tasks as one evaluation set

### Requirement: Integration wires objective and background into GEPA
The system SHALL pass natural-language objective and optional background text into `optimize_anything(...)` so the reflection model has task-specific guidance.

#### Scenario: Optimization run is configured with domain guidance
- **WHEN** an operator provides objective and background text for a run
- **THEN** the GEPA invocation includes those values as reflection guidance inputs

### Requirement: Optimization loop ingests side information from evaluator outputs
The system SHALL feed evaluator-produced side information back into GEPA so reflections and candidate proposals can use actionable diagnostics.

#### Scenario: Evaluator returns contextual diagnostics
- **WHEN** a candidate performs poorly and the evaluator returns expected-versus-actual details
- **THEN** the optimizer uses that side information as part of subsequent reflection and proposal steps

### Requirement: Optimization runs can resume with persisted state
The system SHALL persist enough optimization metadata to resume a GEPA run without losing candidate history and evaluation context.

#### Scenario: Long-running search is interrupted
- **WHEN** a GEPA optimization process stops before completion and is restarted
- **THEN** the system restores the saved optimization state and continues the run
