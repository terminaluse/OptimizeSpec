## ADDED Requirements

### Requirement: Launch documentation defines alpha readiness criteria
The system SHALL document the launch-alpha readiness criteria for the GEPA eval skill workflow, including required fixtures, required commands, required evidence artifacts, and passing score thresholds.

#### Scenario: User reads launch criteria
- **WHEN** a maintainer opens the launch-readiness documentation
- **THEN** they can identify what must pass before alpha launch and where evidence is written

### Requirement: Launch documentation includes reproducible commands
The system SHALL document reproducible commands for generation, direct eval, compare, optimization, verification, and optional live Managed Agent validation.

#### Scenario: Maintainer runs documented smoke commands
- **WHEN** a maintainer follows the documented deterministic launch-alpha commands
- **THEN** the commands can run without live Anthropic credentials and produce the expected run artifacts

#### Scenario: Maintainer runs optional live commands
- **WHEN** a maintainer opts into live Managed Agent validation with credentials
- **THEN** the documentation identifies the required environment variables, expected cost risk, and evidence outputs

### Requirement: Launch documentation explains known limitations
The system SHALL document current limitations, including Claude Managed Agent-only runtime support, deterministic fixture limits, qualitative scoring limits, live-run cost, and non-goals for the alpha.

#### Scenario: User evaluates runtime support
- **WHEN** a user checks whether another agent runtime is supported
- **THEN** the documentation clearly states that only Claude Managed Agents are supported in this alpha

### Requirement: Launch documentation links validation evidence to release decisions
The system SHALL explain how generated summaries, comparisons, optimizer artifacts, ASI, and negative fixture results should be reviewed before release.

#### Scenario: Maintainer reviews release evidence
- **WHEN** validation completes
- **THEN** the documentation tells the maintainer which files to inspect and how to interpret pass, fail, and warning states

