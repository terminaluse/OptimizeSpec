## ADDED Requirements

### Requirement: Machine-consumed artifacts follow hard contracts
The system SHALL enforce strict structural contracts for fixture metadata, eval cases, candidate fields, rollout results, score results, Actionable Side Information, command evidence, and run summaries.

#### Scenario: Machine-consumed artifact is valid
- **WHEN** a machine-consumed artifact is parsed by the harness or optimizer
- **THEN** the artifact satisfies the required schema fields and type expectations before the workflow continues

#### Scenario: Machine-consumed artifact is invalid
- **WHEN** a machine-consumed artifact is missing required fields or has incompatible types
- **THEN** the harness fails validation with parser or schema diagnostics instead of passing malformed data downstream

### Requirement: Agent-written artifacts use semantic scoring
The system SHALL score proposal, design, spec, task, and apply-plan prose by required concepts, structural sections, semantic fit, and critical omissions rather than exact wording or golden-file equality.

#### Scenario: Agent-written artifact uses different wording
- **WHEN** a generated prose artifact contains the required concepts with different phrasing from the reference examples
- **THEN** the scorer can award credit without requiring exact text matches

#### Scenario: Agent-written artifact omits a critical concept
- **WHEN** a generated prose artifact omits required runner, scorer, ASI, optimizer, or validation detail
- **THEN** the scorer records the omission and lowers the score

### Requirement: Proposal artifacts are scored for eval contract completeness
The system SHALL score generated proposals for target-agent identification, eval objective, input examples, expected output examples, numeric scoring, qualitative scoring, and unresolved discovery questions.

#### Scenario: Proposal contains a complete eval contract
- **WHEN** the proposal includes the required eval contract fields
- **THEN** the proposal scorer awards full credit for contract completeness

#### Scenario: Proposal omits scoring details
- **WHEN** the proposal lacks numeric or qualitative scoring details
- **THEN** the proposal scorer records the omission and lowers the score

### Requirement: Design artifacts are scored for runner and optimizer detail
The system SHALL score generated designs for concrete direct-eval invocation, rollout lifecycle, scorer execution, ASI construction, GEPA optimization invocation, compare behavior, persistence, cleanup, and credential assumptions.

#### Scenario: Design explains the actual eval runner
- **WHEN** the design names how the target repo will invoke eval, compare, optimize, and candidate inspection
- **THEN** the design scorer awards credit for runner invocation detail

#### Scenario: Design omits optimization mechanics
- **WHEN** the design does not explain how rollouts are passed into GEPA or how optimizer artifacts are persisted
- **THEN** the design scorer records a critical omission

### Requirement: Spec and task artifacts are scored for implementation coverage
The system SHALL score generated specs and tasks for requirements and implementation steps covering direct eval, rollouts, scorers, ASI, GEPA optimize, compare, validation, negative cases, and validation documentation.

#### Scenario: Specs and tasks cover all required subsystems
- **WHEN** generated specs and tasks include every required subsystem
- **THEN** the scorer awards full implementation-coverage credit

#### Scenario: Specs or tasks are missing a subsystem
- **WHEN** generated specs or tasks omit a required subsystem
- **THEN** the scorer identifies the missing subsystem in feedback

### Requirement: Eval-case artifacts are parsed and scored
The system SHALL parse generated eval-case artifacts and score them for valid structure, train and validation or test splits, inputs, expected outputs, scorers, metadata, and custom scorer references.

#### Scenario: Eval cases parse successfully
- **WHEN** the generated eval-case file is valid YAML with required case fields
- **THEN** the scorer can load the cases and evaluate structural completeness

#### Scenario: Eval cases are malformed
- **WHEN** the generated eval-case file cannot be parsed or lacks required fields
- **THEN** the scorer returns a failed score with parser diagnostics

### Requirement: Artifact scorers return numeric and qualitative feedback
The system SHALL return a numeric score and qualitative feedback for every artifact-quality eval case.

#### Scenario: Artifact quality case is scored
- **WHEN** a generated artifact is evaluated
- **THEN** the scorer returns a score from 0.0 to 1.0 and feedback suitable for ASI reflection
