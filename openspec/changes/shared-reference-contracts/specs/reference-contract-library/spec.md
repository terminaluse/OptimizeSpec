## ADDED Requirements

### Requirement: Shared OptimizeSpec contracts live in a common reference library
The OptimizeSpec skill system SHALL maintain shared markdown contracts for cross-cutting eval-system expectations under the common skill references directory.

#### Scenario: Common contracts are available
- **WHEN** an agent works on proposal, design, apply, or verify phases for an OptimizeSpec system
- **THEN** the agent can find shared reference contracts for evidence, runner behavior, grader behavior, ASI, candidate surfaces, optimizer behavior, runtime invocation, and verification

#### Scenario: A contract applies across multiple phases
- **WHEN** a concept such as evidence persistence or grader trust applies to more than one phase
- **THEN** its durable requirements are documented in a shared reference contract instead of being duplicated independently in each phase skill

### Requirement: The common skill exposes a reference index
The common OptimizeSpec skill SHALL provide an index that explains which reference contracts exist and when each should be loaded.

#### Scenario: Proposal work begins
- **WHEN** a skill drafts a new eval proposal
- **THEN** the reference index identifies the criteria-first, candidate surface, grader, and evidence contracts as relevant context

#### Scenario: Design or apply work begins
- **WHEN** a skill designs or implements the eval runner and optimizer system
- **THEN** the reference index identifies the runner, evidence, grader, ASI, optimizer, runtime, and verification contracts as relevant context

### Requirement: Phase skills stay reference-driven
Phase-specific skills SHALL cite shared contracts and load them progressively instead of embedding every cross-cutting requirement inline.

#### Scenario: A phase skill needs implementation detail
- **WHEN** a phase skill needs details outside its local workflow instructions
- **THEN** it loads the smallest relevant reference contract set from the common reference library

#### Scenario: A shared requirement changes
- **WHEN** evidence, runner, grader, ASI, optimizer, runtime, or verification expectations change
- **THEN** the change can be made in the shared contract without rewriting equivalent prose across every phase skill

### Requirement: Markdown contracts remain concise and actionable
Shared contracts SHALL define required behavior, required artifacts, and review questions without becoming long narrative documentation.

#### Scenario: A contract is used by a coding agent
- **WHEN** a coding agent reads a reference contract during implementation
- **THEN** the contract gives enough concrete artifact and behavior expectations to guide implementation

#### Scenario: A contract is too broad
- **WHEN** a reference document accumulates unrelated expectations
- **THEN** the workflow splits it into a narrower contract so skills can load only relevant context
