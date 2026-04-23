## ADDED Requirements

### Requirement: Harness invokes the GEPA eval workflow against fixtures
The system SHALL provide a validation harness that runs the GEPA eval skill workflow against fixture agent inputs and records the generated artifacts and command evidence.

#### Scenario: Harness generates workflow artifacts
- **WHEN** the harness runs generation for a fixture
- **THEN** it produces proposal, design, specs, tasks, eval cases, seed candidate, and apply-plan artifacts in an isolated output directory

#### Scenario: Harness detects missing artifacts
- **WHEN** generation completes without one or more required artifacts
- **THEN** the harness records the missing paths and returns a failed validation result

### Requirement: Harness exposes repeatable validation commands
The system SHALL expose repeatable commands for generation, direct eval, candidate comparison, GEPA optimization, and verification.

#### Scenario: Direct eval command runs
- **WHEN** the user invokes the harness eval command with a fixture and candidate
- **THEN** the harness evaluates the candidate on the fixture eval cases and writes a summary artifact

#### Scenario: Compare command runs
- **WHEN** the user invokes the harness compare command with baseline and candidate inputs
- **THEN** the harness evaluates both candidates on the same cases and writes per-case score deltas and candidate diffs

#### Scenario: Optimize command runs
- **WHEN** the user invokes the harness optimize command with a fixture, candidate, and metric-call budget
- **THEN** the harness invokes GEPA through the self-improvement optimizer and writes optimizer evidence to the run directory

#### Scenario: Verify command runs
- **WHEN** the user invokes the harness verify command for a run directory
- **THEN** the harness checks required files, command return codes, score thresholds, and declared fixture expectations

### Requirement: Harness captures command-level evidence
The system SHALL persist command arguments, return codes, stdout tails, stderr tails, elapsed time, generated files, scores, ASI, and errors for each validation operation.

#### Scenario: Command succeeds
- **WHEN** a harness command exits successfully
- **THEN** the run directory contains evidence sufficient to reproduce what was invoked and what artifacts were created

#### Scenario: Command fails
- **WHEN** a harness command exits with an error or timeout
- **THEN** the run directory contains failure diagnostics that can be included in ASI and scorer feedback

### Requirement: Harness uses isolated run directories
The system SHALL isolate each fixture validation run so generated artifacts, rollouts, optimizer state, and logs do not overwrite unrelated runs.

#### Scenario: Multiple fixtures run
- **WHEN** two fixture validations are executed
- **THEN** each fixture writes to a distinct run directory with stable subdirectories for generated artifacts, eval, compare, optimize, and verification

