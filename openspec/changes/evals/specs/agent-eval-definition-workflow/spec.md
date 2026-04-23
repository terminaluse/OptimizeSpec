## ADDED Requirements

### Requirement: Eval proposal captures target agent context
The system SHALL require each eval proposal to identify the target agent, the agent runtime, the user-facing behavior being improved, and any known constraints on how the agent is invoked.

#### Scenario: User starts an eval change with target context
- **WHEN** the user describes an eval for a Claude Managed Agent
- **THEN** the proposal artifact records the target agent context and runtime assumptions needed for later design

#### Scenario: Target agent context is incomplete
- **WHEN** the user has not provided enough information to identify the target agent or runtime
- **THEN** the workflow records the missing context as an explicit unresolved question rather than inventing details

### Requirement: Eval proposal captures input and output examples
The system SHALL guide users to define representative eval input examples and expected output examples or output-shape expectations.

#### Scenario: User provides concrete examples
- **WHEN** the user provides input and expected output pairs
- **THEN** the proposal artifact preserves those pairs as eval contract material

#### Scenario: User only knows the desired behavior
- **WHEN** the user describes desired behavior without concrete examples
- **THEN** the workflow captures the behavior and asks the coding agent to help derive candidate eval examples

### Requirement: Eval proposal captures numeric scoring intent
The system SHALL require each eval proposal to describe how numeric scoring should work, including the preferred score range and what high, partial, and failing scores mean.

#### Scenario: User knows the numeric scorer
- **WHEN** the user provides an exact numeric scoring rule
- **THEN** the proposal artifact records the scoring rule in a form that can drive scorer implementation

#### Scenario: Numeric scoring is undecided
- **WHEN** the user does not know the best numeric scoring method
- **THEN** the proposal artifact records scorer discovery as an open item with candidate scoring directions

### Requirement: Eval proposal captures qualitative judgement
The system SHALL require each eval proposal to include qualitative scoring guidance such as rubrics, reviewer criteria, or natural-language success descriptions.

#### Scenario: User provides rubric criteria
- **WHEN** the user provides qualitative success criteria
- **THEN** the proposal artifact records those criteria alongside the numeric scoring intent

#### Scenario: Qualitative criteria conflict with examples
- **WHEN** examples and qualitative criteria imply different desired behavior
- **THEN** the workflow records the conflict as an unresolved eval-design question

### Requirement: Eval proposal supports collaborative discovery
The system SHALL allow a proposal to remain valid when it includes explicit unknowns that the design or apply phase must resolve through codebase inspection or user follow-up.

#### Scenario: Eval details are partially known
- **WHEN** the user can describe the improvement goal but not every scoring or runtime detail
- **THEN** the proposal artifact distinguishes known eval contract details from discovery tasks
