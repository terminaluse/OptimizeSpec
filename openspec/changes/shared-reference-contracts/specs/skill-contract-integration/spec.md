## ADDED Requirements

### Requirement: Proposal templates include evidence and contract awareness
OptimizeSpec proposal templates SHALL give the user a concise view of evidence and contract expectations without turning the proposal into an implementation design.

#### Scenario: Proposal is drafted
- **WHEN** a new eval proposal is created
- **THEN** it names the expected evidence model at a high level and records any unknowns about candidate versions, scoring records, judge records, ASI, or promotion evidence

#### Scenario: Evidence details are too deep for proposal
- **WHEN** runner mechanics, file layout, or detailed optimizer lineage are needed
- **THEN** the proposal records the decision or unknown and defers detailed mechanics to design

### Requirement: Design templates specify runner and optimizer mechanics
OptimizeSpec design templates SHALL require enough detail to implement and audit the eval runner and optimizer system.

#### Scenario: Design is complete
- **WHEN** a design is ready for apply work
- **THEN** it specifies invocation commands, rollout lifecycle, eval case execution, scoring and judging flow, ASI generation, candidate mutation surface, optimizer loop, evidence ledger, and verification plan

#### Scenario: Runtime is Claude Managed Agents
- **WHEN** the design targets Claude Managed Agents
- **THEN** it references the managed-agents runtime contract for SDK/header setup, invocation assumptions, and rollout evidence

### Requirement: Validation checks contract behavior instead of exact prose
OptimizeSpec validation SHALL prefer structured artifact, fixture, and behavior checks over exact markdown wording assertions.

#### Scenario: A generated design omits evidence
- **WHEN** validation inspects a design or fixture output that lacks run manifests, candidate versions, per-case scores, judge records, ASI records, optimizer lineage, or promotion evidence
- **THEN** validation lowers the score or fails the relevant quality check

#### Scenario: Contract wording changes
- **WHEN** markdown reference prose is rewritten without changing the required behavior
- **THEN** tests that inspect artifact behavior and structured outputs continue to pass

### Requirement: Verification inspects emitted evidence
Verification guidance SHALL instruct agents to inspect emitted run evidence before claiming an eval system is ready.

#### Scenario: Deterministic smoke verification runs
- **WHEN** a local smoke test runs without live Anthropic credentials
- **THEN** verification checks that expected evidence files or structured summaries are emitted for the smoke run

#### Scenario: Live Managed Agents verification runs
- **WHEN** a live Managed Agents smoke is run with credentials
- **THEN** verification inspects run manifest, rollout records, per-case scores, judge output when present, ASI, optimizer lineage, and promotion decision before reporting readiness
