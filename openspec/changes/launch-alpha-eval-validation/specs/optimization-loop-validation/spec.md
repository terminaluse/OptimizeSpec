## ADDED Requirements

### Requirement: System-loop validation scores successful optimization as 1.0
The system SHALL assign a score of 1.0 to the optimization-loop eval only when the actual generated or applied system runs an end-to-end optimization loop and writes the required evidence artifacts.

#### Scenario: Optimization loop completes
- **WHEN** generation or apply succeeds, direct eval writes `summary.json`, GEPA optimize writes optimizer evidence, all required commands return zero, and required files exist
- **THEN** the system-loop scorer returns 1.0

#### Scenario: Optimization loop is incomplete
- **WHEN** any required command fails, times out, or omits a required evidence artifact
- **THEN** the system-loop scorer returns 0.0 with the missing files and command diagnostics

### Requirement: Direct eval validation persists rollout evidence
The system SHALL validate that direct eval runs persist summary, per-case rollout, score, side-info, candidate, and error artifacts.

#### Scenario: Direct eval runs on fixture cases
- **WHEN** the harness runs direct eval for a fixture candidate
- **THEN** the run directory contains `summary.json` and per-case rollout artifacts with scores and ASI

### Requirement: Compare validation reports score deltas
The system SHALL validate that candidate comparison runs evaluate baseline and candidate on identical cases and persist aggregate and per-case score deltas.

#### Scenario: Compare runs on fixture cases
- **WHEN** the harness compares two candidates
- **THEN** it writes a comparison artifact containing baseline scores, candidate scores, deltas, and candidate diffs

### Requirement: GEPA validation uses bounded optimizer budgets
The system SHALL allow optimization-loop validation to run with a small metric-call budget for smoke testing and a larger optional budget for release evidence.

#### Scenario: Smoke optimization runs
- **WHEN** the harness runs with `max_metric_calls` set to a small value
- **THEN** GEPA is invoked and optimizer evidence is written even if quality improvement is not guaranteed

#### Scenario: Release optimization runs
- **WHEN** the user runs an optional larger launch-readiness validation
- **THEN** the harness records whether optimized candidates improve validation or test scores over the seed candidate

### Requirement: Optimization-loop ASI includes system evidence
The system SHALL include command traces, missing files, generated artifact paths, optimizer outputs, and failure details in ASI for optimization-loop eval cases.

#### Scenario: System loop fails
- **WHEN** an optimization-loop eval receives a 0.0 score
- **THEN** its ASI contains enough command and artifact evidence for GEPA reflection to target the failing candidate fields

