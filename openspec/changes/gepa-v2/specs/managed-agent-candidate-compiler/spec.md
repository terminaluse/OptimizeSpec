## ADDED Requirements

### Requirement: Compiler parses candidate fields into typed internal models
The system SHALL compile prompt and structured candidate fields into typed internal representations before creating Claude Managed Agents resources.

#### Scenario: Candidate is submitted for evaluation
- **WHEN** the evaluator receives a GEPA candidate
- **THEN** the compiler produces typed internal prompt, skill, environment, and subagent models before runtime execution begins

### Requirement: Compiler models skills as reusable refs or custom skill specs
The compiler SHALL parse the `skills` field into typed internal models that distinguish between direct reusable skill references and custom skill definitions that require materialization.

#### Scenario: Skills field mixes refs and custom definitions
- **WHEN** the candidate `skills` field contains both existing skill refs and custom skill content
- **THEN** the compiler produces typed internal skill models that preserve which entries are reusable refs and which require Skills API resolution

### Requirement: Compiler uses Anthropic structured outputs for candidate parsing
The system SHALL use Anthropic structured outputs as the primary candidate-to-typed-model compiler path for structured fields.

#### Scenario: Structured fields are compiled
- **WHEN** the compiler processes `skills`, `environment_spec`, or `subagent_specs`
- **THEN** it invokes Anthropic structured-output parsing against a schema that defines the expected typed candidate shape

### Requirement: Compiler canonicalizes structured fields before runtime use
The system SHALL canonicalize parsed structured fields before creating Anthropic resources so runtime behavior is based on stable compiled inputs.

#### Scenario: Structured fields are parsed successfully
- **WHEN** the compiler accepts `skills`, `environment_spec`, or `subagent_specs`
- **THEN** the runtime uses canonicalized structured values rather than raw unnormalized text

### Requirement: Compiler resolves deterministic skill identities before runtime use
The system SHALL derive deterministic identities for custom candidate-defined skills from their canonicalized contents before runtime resource resolution.

#### Scenario: Equivalent custom skill definitions recur across evaluations
- **WHEN** multiple evaluations encounter the same canonical custom skill definition
- **THEN** the compiler exposes a stable identity that the runtime can use to look up or create the corresponding skill resource

### Requirement: Compiler creates fresh managed-agent resources per evaluation
The system SHALL create fresh Claude Managed Agents resources from the compiled candidate for each evaluation run.

#### Scenario: Candidate is evaluated on multiple tasks
- **WHEN** the same candidate is evaluated on separate benchmark tasks
- **THEN** each evaluation uses newly created Anthropic agent and environment resources derived from that candidate

### Requirement: Compiler failures surface field-specific diagnostics
The system SHALL report which candidate field or compile stage failed when candidate compilation cannot produce executable managed-agent resources.

#### Scenario: Subagent compilation fails
- **WHEN** `subagent_specs` cannot be compiled into callable agents
- **THEN** the evaluator returns a scored failure with diagnostics that identify the subagent field as the failed compile surface

#### Scenario: Structured-output parsing fails
- **WHEN** Anthropic structured-output parsing cannot produce a valid typed candidate
- **THEN** the evaluator returns a scored failure with diagnostics that identify the structured field or schema boundary that failed

#### Scenario: Skill materialization planning fails
- **WHEN** the compiler cannot derive a valid reusable ref or custom skill specification from the `skills` field
- **THEN** the evaluator returns a scored failure with diagnostics that identify the skills field as the failed compile surface
