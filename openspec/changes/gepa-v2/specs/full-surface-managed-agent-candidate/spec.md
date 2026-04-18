## ADDED Requirements

### Requirement: Candidate surface includes all major managed-agent fields
The system SHALL represent the Claude Managed Agents optimization surface as a GEPA-compatible `dict[str, str]` with, at minimum, `system_prompt`, `task_prompt`, `outcome_rubric`, `skills`, `environment_spec`, and `subagent_specs`.

#### Scenario: Seed candidate is prepared for optimization
- **WHEN** an optimization run is initialized
- **THEN** the seed candidate contains named text fields for every major managed-agent component the runtime intends to optimize

### Requirement: Skills field supports hybrid declarative skill specs
The `skills` candidate field SHALL support a hybrid declarative format that can express either references to existing Anthropic skills or custom skill definitions that can be materialized through the Skills API.

#### Scenario: Candidate reuses an existing skill
- **WHEN** the candidate `skills` field references an existing skill id and optional version
- **THEN** the compiler can preserve that reusable skill reference without requiring new skill creation

#### Scenario: Candidate defines a new custom skill
- **WHEN** the candidate `skills` field provides custom skill content rather than an existing skill id
- **THEN** the compiler can convert that content into a typed custom skill specification for later Skills API resolution

### Requirement: Structured candidate fields compile through Anthropic structured outputs
The system SHALL compile structured candidate fields into typed internal models using Anthropic structured outputs before runtime execution.

#### Scenario: Structured candidate is prepared for runtime execution
- **WHEN** the evaluator receives a candidate containing `skills`, `environment_spec`, or `subagent_specs`
- **THEN** the compiler uses an Anthropic structured-output schema to produce typed internal representations for those fields

### Requirement: Structured candidate fields have stable canonical formats
The system SHALL define canonical text formats for structured fields after compilation so semantically equivalent values can be compiled consistently.

#### Scenario: Equivalent structured candidate variants are compiled
- **WHEN** two candidate fields express the same structured value with different formatting
- **THEN** the runtime canonicalizes them into the same effective compiled representation after typed compilation

#### Scenario: Equivalent custom skills are expressed with different formatting
- **WHEN** two candidate `skills` payloads define the same custom skill content with different formatting
- **THEN** the runtime canonicalizes them into the same effective skill specification before resource resolution

### Requirement: Candidate identity reflects the full surface
The system SHALL derive candidate identity from the full GEPA-facing text contents rather than from only prompt fields.

#### Scenario: Structured field changes while prompts stay the same
- **WHEN** a candidate changes `environment_spec` and keeps all other fields unchanged
- **THEN** the resulting candidate identity differs from the prior candidate identity

### Requirement: Candidate parsing failures are tolerant but explicit
The system SHALL convert malformed candidate structures or structured-output compile failures into informative parsed failures or defaults without terminating the optimization loop.

#### Scenario: Structured field is malformed
- **WHEN** a candidate contains an invalid `skills` or `subagent_specs` payload
- **THEN** the evaluator records a scored failure or explicit diagnostic that GEPA can use for reflection instead of crashing the run
