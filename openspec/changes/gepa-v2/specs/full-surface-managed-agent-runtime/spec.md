## ADDED Requirements

### Requirement: Every candidate field affects managed-agent execution
The runtime SHALL compile every major candidate field into concrete Claude Managed Agents behavior rather than ignoring unsupported fields.

#### Scenario: Candidate changes only one non-prompt field
- **WHEN** a candidate differs only in `environment_spec`, `skills`, or `subagent_specs`
- **THEN** the resulting managed-agent execution reflects that field change during evaluation

### Requirement: Runtime supports candidate-defined skills
The runtime SHALL resolve candidate-defined skills into attached Anthropic skill refs for the primary agent or compiled subagents when the candidate includes them.

#### Scenario: Candidate includes non-empty skills
- **WHEN** the compiler parses a valid `skills` field
- **THEN** the created managed agent includes the resolved skills in its executable configuration

### Requirement: Runtime creates or reuses custom skills deterministically
The runtime SHALL reuse existing Anthropic custom skills when the candidate-defined skill content matches an already materialized artifact and SHALL create a new custom skill only when no matching reusable artifact exists.

#### Scenario: Candidate custom skill already exists
- **WHEN** the candidate includes a custom skill definition whose canonicalized contents match an existing materialized skill artifact
- **THEN** the runtime reuses that skill artifact instead of creating a duplicate

#### Scenario: Candidate custom skill is new
- **WHEN** the candidate includes a valid custom skill definition that has no matching existing skill artifact
- **THEN** the runtime creates the skill through the Anthropic Skills API before attaching it to the agent or subagent

### Requirement: Runtime supports candidate-defined environments
The runtime SHALL create the Anthropic environment from the candidate-provided `environment_spec` for each evaluation.

#### Scenario: Candidate changes package or networking config
- **WHEN** a candidate provides a different valid environment specification
- **THEN** the evaluation runs inside an environment created from that specification

### Requirement: Runtime supports candidate-defined subagents
The runtime SHALL compile valid `subagent_specs` into callable Claude Managed Agents subagents and wire them into the primary agent.

#### Scenario: Candidate includes callable subagent definitions
- **WHEN** the candidate provides valid `subagent_specs`
- **THEN** the primary agent is created with callable subagents derived from those specs
