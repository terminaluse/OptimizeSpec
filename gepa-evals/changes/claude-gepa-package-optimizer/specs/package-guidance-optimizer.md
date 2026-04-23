## ADDED Requirements

### Requirement: Package optimizer exposes semantic operations
The system SHALL expose direct eval, optimize, compare, and candidate inspection operations for this package optimizer.

#### Scenario: User invokes direct eval
- **WHEN** the user runs the package optimizer eval command
- **THEN** the system evaluates the seed or provided candidate on the package guidance eval cases without GEPA search

#### Scenario: User invokes optimize
- **WHEN** the user runs the package optimizer optimize command
- **THEN** the system invokes GEPA with package guidance eval cases, scorer, ASI, objective, background, and run directory

### Requirement: Package optimizer evaluates required concept coverage
The system SHALL score package guidance answers by the fraction of required terms present in the generated answer.

#### Scenario: Answer misses required concepts
- **WHEN** a generated answer omits required package concepts
- **THEN** the scorer returns a partial score and ASI lists the missing terms

### Requirement: Package optimizer emits ASI
The system SHALL emit top-level and field-specific ASI for every package guidance rollout.

#### Scenario: Rollout completes
- **WHEN** the package optimizer evaluates a candidate on one eval case
- **THEN** it persists score, rollout, candidate, and side information artifacts
