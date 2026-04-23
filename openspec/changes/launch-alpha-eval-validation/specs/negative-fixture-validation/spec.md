## ADDED Requirements

### Requirement: Negative fixtures validate missing eval contracts
The system SHALL include negative fixtures that omit eval input/output pairs, expected outputs, or scoring guidance and verify that the workflow asks for clarification or fails usefully.

#### Scenario: Eval input and output are missing
- **WHEN** a fixture request does not define eval inputs or expected outputs
- **THEN** the generated workflow does not invent a complete eval contract and records a clarification or blocked status

#### Scenario: Scoring guidance is missing
- **WHEN** a fixture request lacks numeric and qualitative scoring details
- **THEN** the generated workflow records the missing scoring information and avoids claiming the eval is ready to optimize

### Requirement: Negative fixtures validate unsupported runtimes
The system SHALL include negative fixtures for non-Claude agent runtimes and verify that the v1 workflow blocks or reports unsupported runtime status.

#### Scenario: Fixture uses unsupported runtime
- **WHEN** fixture metadata identifies a runtime other than Claude Managed Agents
- **THEN** the workflow records that the runtime is unsupported for v1 and avoids generating a misleading apply plan

### Requirement: Negative fixtures validate missing invocation details
The system SHALL include negative fixtures where the target agent's run commands, source references, or resource setup are insufficient for an eval runner design.

#### Scenario: Invocation details are absent
- **WHEN** the design phase cannot identify how to run the target agent
- **THEN** the workflow records the missing invocation details and blocks apply or marks it unsafe

### Requirement: Negative fixture results are scored as useful failures
The system SHALL score negative fixture behavior based on whether the workflow fails usefully, asks for clarification, and preserves actionable diagnostics.

#### Scenario: Negative fixture fails usefully
- **WHEN** the workflow identifies the intended missing information or unsupported assumption
- **THEN** the negative fixture scorer awards credit for the useful failure

#### Scenario: Negative fixture falsely succeeds
- **WHEN** the workflow proceeds as if an invalid fixture is ready for optimization
- **THEN** the negative fixture scorer assigns a failed score and reports the false-success condition

