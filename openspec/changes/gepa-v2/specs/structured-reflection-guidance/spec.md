## ADDED Requirements

### Requirement: Reflection guidance is field-specific
The system SHALL provide field-specific reflection guidance for full-surface candidates rather than using one generic proposal prompt for every field.

#### Scenario: GEPA proposes an update to a structured field
- **WHEN** the reflection loop selects `skills`, `environment_spec`, or `subagent_specs` for mutation
- **THEN** the proposer uses guidance tailored to that field's structure and semantics

### Requirement: Evaluator returns field-specific actionable feedback
The system SHALL include field-specific diagnostics in evaluator side information so GEPA can infer which candidate component likely caused failure.

#### Scenario: Output is wrong due to a configuration field
- **WHEN** the evaluator identifies `environment_spec` or `skills` as a likely cause of failure
- **THEN** the side information includes actionable feedback keyed to that field

#### Scenario: Skills API resolution fails
- **WHEN** the evaluator or runtime cannot reuse or create a candidate-defined custom skill
- **THEN** the returned side information includes actionable feedback keyed to `skills` that explains whether the failure was due to invalid content, lookup mismatch, or Skills API creation failure

### Requirement: Structured-field validation feedback is reflection-visible
The system SHALL surface structured-output parse failures and canonicalization failures for structured fields in the same feedback channel GEPA uses for candidate improvement.

#### Scenario: Candidate contains malformed structured text
- **WHEN** `subagent_specs` or `skills` fails validation
- **THEN** the returned side information includes the validation failure in a form the reflection model can use for a follow-up mutation

### Requirement: Prompt and structured fields can be improved independently
The system SHALL support reflection updates to one field class without forcing unrelated fields to be regenerated.

#### Scenario: Reflection updates only the outcome rubric
- **WHEN** GEPA selects `outcome_rubric` alone for mutation
- **THEN** the structured config fields remain unchanged in the proposed candidate
