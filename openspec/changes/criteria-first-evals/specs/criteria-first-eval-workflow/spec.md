## ADDED Requirements

### Requirement: GEPA eval proposals define success criteria before scoring mechanics
The GEPA eval workflow SHALL require proposal artifacts to define success criteria before eval examples, scorers, ASI, design, or apply work is considered ready.

#### Scenario: Proposal includes criteria-first content
- **WHEN** a new GEPA eval proposal is created
- **THEN** it includes user outcome, primary criterion, secondary criteria, guardrails, thresholds, non-goals, and known blind spots

#### Scenario: Criteria are missing or vague
- **WHEN** the user request does not define what "better" means
- **THEN** the proposal records explicit unknowns and discovery questions instead of inventing a complete eval contract

### Requirement: Success criteria are specific, measurable, achievable, and relevant
The GEPA eval workflow SHALL guide agents to assess whether success criteria are specific, measurable, achievable for the target runtime, and relevant to the target agent's user outcome.

#### Scenario: Criterion is actionable
- **WHEN** a criterion names observable behavior, measurement method, target threshold, and user relevance
- **THEN** the workflow treats it as ready for eval-case and scorer design

#### Scenario: Criterion is not actionable
- **WHEN** a criterion is vague, unmeasurable, unrealistic, or disconnected from the target agent's purpose
- **THEN** the workflow records the weakness and asks for clarification or refinement

### Requirement: Eval categories are separated
The GEPA eval workflow SHALL distinguish system evals, agent quality evals, and optimizer acceptance criteria.

#### Scenario: System-loop eval succeeds
- **WHEN** a system-loop eval scores 1.0 because direct eval, compare, optimize, and evidence persistence all ran
- **THEN** the artifacts state that this proves the machinery works but does not by itself prove the target agent improved on product-quality criteria

#### Scenario: Agent quality eval is required
- **WHEN** the workflow claims the target agent improved
- **THEN** the claim is backed by an agent-quality eval tied to explicit success criteria

### Requirement: Proposal artifacts include critical unknowns
The GEPA eval workflow SHALL preserve missing criteria, missing task distribution, missing grader trust, and missing optimizer acceptance details as explicit unknowns.

#### Scenario: User knows the eval contract
- **WHEN** the user provides criteria, examples, scoring, and grader details
- **THEN** the proposal captures them directly

#### Scenario: User needs help defining the eval
- **WHEN** the user does not know the eval contract
- **THEN** the proposal captures the current hypothesis and lists discovery questions needed before implementation
