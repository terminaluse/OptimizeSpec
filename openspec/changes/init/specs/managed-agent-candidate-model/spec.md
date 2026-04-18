## ADDED Requirements

### Requirement: Candidate surface is GEPA-compatible text
The system SHALL expose Claude Managed Agents candidates to GEPA as either a single string or a `dict[str, str]` of named text fields rather than as nested runtime objects.

#### Scenario: Candidate is loaded for optimization
- **WHEN** the optimization loop starts with a seed candidate
- **THEN** the candidate is provided to GEPA in a documented text-compatible shape that the evaluator can accept directly

### Requirement: Named text fields map to managed-agent concerns
The system SHALL define a stable mapping from named candidate fields to Claude Managed Agents concerns such as agent instructions, outcome rubric text, tool policy, environment specification, and related mutable configuration.

#### Scenario: Candidate uses dictionary mode
- **WHEN** a candidate is represented as `dict[str, str]`
- **THEN** each field name has a defined meaning and can be compiled deterministically by the runtime

### Requirement: Candidate fields are independently mutable
The system SHALL allow GEPA to mutate one text field without requiring unrelated fields to be regenerated.

#### Scenario: Reflection updates only one parameter
- **WHEN** GEPA proposes a change to the outcome rubric field only
- **THEN** the system preserves the other candidate fields unchanged

### Requirement: Candidate identity is reproducible
The system SHALL derive a deterministic identity for a candidate from its GEPA-facing text contents so repeated evaluations can be traced, deduplicated, or replayed.

#### Scenario: Equivalent text candidate reappears
- **WHEN** the optimizer produces a candidate with the same string contents as a previously seen candidate
- **THEN** the system detects the candidate as the same logical candidate or assigns the same deterministic identity
