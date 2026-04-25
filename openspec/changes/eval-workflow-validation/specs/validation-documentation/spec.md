## ADDED Requirements

### Requirement: Validation documentation defines readiness criteria
The system SHALL document the eval workflow readiness criteria for the OptimizeSpec skill workflow, including required fixtures, required commands, required evidence artifacts, and passing score thresholds.

#### Scenario: User reads validation criteria
- **WHEN** a maintainer opens the validation documentation
- **THEN** they can identify what must pass before eval validation and where evidence is written

### Requirement: Validation documentation includes reproducible commands
The system SHALL document reproducible commands for generation, direct eval, compare, optimization, verification, and optional live Managed Agent validation.

#### Scenario: Maintainer runs documented smoke commands
- **WHEN** a maintainer follows the documented deterministic eval-validation commands
- **THEN** the commands can run without live Anthropic credentials and produce the expected run artifacts

#### Scenario: Maintainer runs optional live commands
- **WHEN** a maintainer opts into live Managed Agent validation with credentials
- **THEN** the documentation identifies the required environment variables, expected cost risk, and evidence outputs

### Requirement: Validation documentation explains known limitations
The system SHALL document current limitations, including Claude Managed Agent-only runtime support, deterministic fixture limits, qualitative scoring limits, live-run cost, and non-goals for the validation workflow.

#### Scenario: User evaluates runtime support
- **WHEN** a user checks whether another agent runtime is supported
- **THEN** the documentation clearly states that only Claude Managed Agents are supported in this validation workflow

### Requirement: Validation documentation links evidence to release decisions
The system SHALL explain how generated summaries, comparisons, optimizer artifacts, ASI, and negative fixture results should be reviewed before release.

#### Scenario: Maintainer reviews release evidence
- **WHEN** validation completes
- **THEN** the documentation tells the maintainer which files to inspect and how to interpret pass, fail, and warning states
