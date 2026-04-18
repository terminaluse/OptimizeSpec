## ADDED Requirements

### Requirement: Evaluator supports structured side information
The system SHALL build `side_info` payloads that include run diagnostics useful for GEPA reflection, such as expected output, actual output, errors, feedback, and run metadata.

#### Scenario: Candidate fails a task
- **WHEN** the evaluator detects an incorrect or incomplete managed-agent result
- **THEN** it returns side information with enough context for GEPA to infer likely improvements

### Requirement: Multi-objective metrics use higher-is-better semantics
The system SHALL place auxiliary objective values in `side_info["scores"]` and normalize them so larger values indicate better performance.

#### Scenario: Runtime records latency and cost
- **WHEN** the evaluator includes latency and cost diagnostics in side information
- **THEN** it reports normalized metrics such as `latency_inv` or `cost_inv` rather than raw lower-is-better values

### Requirement: Evaluator can include parameter-specific diagnostics
The system SHALL support parameter-specific side information keyed to individual candidate fields so GEPA can reason about which text parameter likely caused a failure.

#### Scenario: One field is identified as problematic
- **WHEN** the evaluator determines that the tool policy field likely caused a bad result
- **THEN** the side information includes a field-specific diagnostic entry for that candidate parameter

### Requirement: Runtime diagnostics can be captured automatically
The system SHALL support GEPA-compatible logging and stdio capture so evaluator logs can become part of Actionable Side Information.

#### Scenario: Evaluator emits diagnostic logs
- **WHEN** the evaluator uses GEPA logging or stdio during execution
- **THEN** those diagnostics are attached to evaluation side information for later reflection
