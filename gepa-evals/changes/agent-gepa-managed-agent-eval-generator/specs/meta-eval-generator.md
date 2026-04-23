## ADDED Requirements

### Requirement: Meta-eval uses existing agent fixture
The system SHALL use this repo's existing Claude Managed Agent prototype as the example agent fixture for generated eval artifacts.

#### Scenario: Fixture is loaded
- **WHEN** the meta-eval runner starts
- **THEN** it reads fixture facts that identify candidate, runtime, evaluator, optimizer, task, and CLI source files

### Requirement: Meta-eval generates eval artifacts
The system SHALL generate proposal, design, spec, task, eval case, seed candidate, and apply-plan text for the existing agent fixture.

#### Scenario: Artifact generation is requested
- **WHEN** the user runs the generate command
- **THEN** the system writes generated artifacts to the requested output directory

### Requirement: Meta-eval scores required concepts
The system SHALL score generated artifact text by required concept coverage and report missing concepts in ASI.

#### Scenario: Generated design omits rollout lifecycle
- **WHEN** a design output lacks rollout lifecycle concepts
- **THEN** the scorer returns a partial score and ASI lists missing rollout terms

### Requirement: Meta-eval supports GEPA optimization
The system SHALL expose a GEPA optimize operation that can improve guidance fields used to generate artifacts.

#### Scenario: Optimization starts
- **WHEN** the optimize command is invoked with credentials and budget
- **THEN** GEPA receives the seed candidate, eval cases, evaluator, objective, background, and reflection config

### Requirement: Meta-eval scores actual system loop success
The system SHALL include an end-to-end eval case that runs generated-system commands and awards `1.0` only when the commands complete and optimization artifacts are produced.

#### Scenario: Generated system completes optimization loop
- **WHEN** the end-to-end system eval runs generate, direct eval, and optimize commands successfully
- **THEN** the scorer returns `1.0` and records the generated artifact paths in ASI

#### Scenario: Generated system fails optimization loop
- **WHEN** any required command fails or optimization artifacts are missing
- **THEN** the scorer returns `0.0` and records the command failure in ASI
