## ADDED Requirements

### Requirement: Design inspects Managed Agents runtime usage
The system SHALL require the design artifact to identify how the target repository creates, stores, updates, and invokes Claude Managed Agents resources.

#### Scenario: Target repo contains Managed Agents code
- **WHEN** the design phase runs against a target repo with Claude Managed Agents integration
- **THEN** the design artifact records where Agents, Environments, Sessions, resources, tools, skills, and event streams are configured

#### Scenario: Target repo creates agents per request
- **WHEN** codebase inspection finds that the target repo creates Agents inside a request or task path
- **THEN** the design artifact records this as a runtime concern that the eval implementation must account for

### Requirement: Design defines eval execution architecture
The system SHALL require the design artifact to explain how eval cases will be executed against the target Claude Managed Agent.

#### Scenario: Eval case runs through a session
- **WHEN** an eval case is designed for a Managed Agent
- **THEN** the design artifact specifies how the input is provided, how the session is started, and how the final output is collected

#### Scenario: Eval needs mounted resources
- **WHEN** eval inputs require files, repositories, or other resources
- **THEN** the design artifact specifies how those resources are attached to the Managed Agent session

### Requirement: Design defines runner invocation surface
The system SHALL require the design artifact to name how users will invoke direct eval, optimization, comparison, and candidate inspection operations in the target repository.

#### Scenario: Target repo has an existing CLI
- **WHEN** the target repo already exposes command-line entrypoints
- **THEN** the design artifact specifies how the eval runner and optimizer operations will be added to or alongside that CLI

#### Scenario: Target repo uses package scripts
- **WHEN** the target repo convention is package scripts, Make targets, or module commands
- **THEN** the design artifact specifies those invocation forms instead of assuming a new global CLI

### Requirement: Design defines rollout lifecycle
The system SHALL require the design artifact to describe the lifecycle for one rollout from candidate loading through Managed Agent execution, scoring, ASI construction, persistence, and cleanup.

#### Scenario: Rollout uses candidate-specific resources
- **WHEN** the design uses candidate-specific Managed Agent resources for eval isolation
- **THEN** the design artifact specifies how those resources are created, pinned, archived, or reused

#### Scenario: Rollout uses existing target-agent factories
- **WHEN** the design reuses existing target-agent creation code
- **THEN** the design artifact explains how candidate overlays are applied reproducibly

### Requirement: Design defines trace and artifact collection
The system SHALL require the design artifact to specify which runtime traces, outputs, errors, and metadata will be captured for scoring and GEPA reflection.

#### Scenario: Managed Agent run completes
- **WHEN** an eval run finishes successfully
- **THEN** the eval system captures the output, relevant event stream metadata, and run identifiers needed for debugging

#### Scenario: Managed Agent run fails
- **WHEN** an eval run fails or times out
- **THEN** the eval system captures errors and partial trace information as scored failure diagnostics

### Requirement: Design defines ASI mapping
The system SHALL require the design artifact to specify how runtime traces and scorer results map into top-level and field-specific Actionable Side Information.

#### Scenario: Scorer produces qualitative feedback
- **WHEN** qualitative feedback is produced for a rollout
- **THEN** the design artifact specifies where that feedback appears in ASI

#### Scenario: Runtime trace identifies a field-specific issue
- **WHEN** trace or scorer diagnostics point to a mutable candidate field
- **THEN** the design artifact specifies the corresponding field-specific ASI key

### Requirement: Design identifies optimizable candidate fields
The system SHALL require the design artifact to identify which target-agent fields GEPA can safely mutate and how those fields map to the existing Managed Agent configuration.

#### Scenario: Target agent exposes prompt fields
- **WHEN** the target repo has mutable prompt or instruction fields
- **THEN** the design artifact maps those fields into the proposed GEPA candidate surface

#### Scenario: Target agent exposes runtime configuration
- **WHEN** the target repo exposes mutable skills, tools, environment, MCP, or resource configuration
- **THEN** the design artifact states whether each field is in scope for the first optimization loop

### Requirement: Design rejects unsupported runtimes in v1
The system SHALL require the design phase to stop or mark the change blocked when the target repo is not a Claude Managed Agents project.

#### Scenario: Target repo uses another agent runtime
- **WHEN** codebase inspection shows the target agent does not use Claude Managed Agents
- **THEN** the design artifact records that the v1 workflow does not support the runtime and avoids producing a misleading apply plan
