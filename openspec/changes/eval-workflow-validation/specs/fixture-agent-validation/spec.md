## ADDED Requirements

### Requirement: Fixture agents declare validation metadata
The system SHALL represent each validation fixture agent with metadata that identifies the target runtime, source references, invocation surface, candidate fields, expected workflow behavior, and credential requirements.

#### Scenario: Fixture metadata is loaded
- **WHEN** the validation harness loads a fixture agent
- **THEN** it can determine the fixture id, Claude Managed Agent runtime type, relevant source files, existing commands, mutable candidate fields, and whether live credentials are required

#### Scenario: Fixture metadata is incomplete
- **WHEN** required fixture metadata is missing
- **THEN** the validation harness marks the fixture invalid before running eval or optimization commands

### Requirement: Positive fixtures exercise the full validation workflow
The system SHALL include positive Claude Managed Agent fixtures that can exercise artifact generation, direct eval, compare, and GEPA optimization using deterministic local execution by default.

#### Scenario: Positive fixture is validated
- **WHEN** the harness runs a positive fixture with the seed candidate
- **THEN** it generates artifacts, runs direct eval, runs compare, runs a small GEPA optimization loop, and persists evidence for each operation

#### Scenario: Positive fixture requires live execution
- **WHEN** a fixture requires live Managed Agent API calls
- **THEN** the harness only runs that fixture when the required environment flag and credentials are present

### Requirement: Fixtures preserve inspectable expected behavior
The system SHALL store enough expected behavior with each fixture for generated eval artifacts and applied systems to be scored without relying on ad hoc human judgement.

#### Scenario: Expected artifacts are declared
- **WHEN** a fixture expects generated files or commands
- **THEN** the fixture declares those expected outputs so the harness can assert them during verification

#### Scenario: Fixture includes qualitative expectations
- **WHEN** a fixture needs qualitative artifact review
- **THEN** the fixture declares rubric terms or semantic checks that the artifact-quality scorer can evaluate

