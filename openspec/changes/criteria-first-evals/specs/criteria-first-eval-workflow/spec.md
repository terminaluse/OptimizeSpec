## ADDED Requirements

### Requirement: OptimizeSpec proposals define success criteria before scoring mechanics
The OptimizeSpec workflow SHALL require proposal artifacts to define success criteria before eval examples, scorers, ASI, design, or apply work is considered ready.

#### Scenario: Proposal includes criteria-first content
- **WHEN** a new OptimizeSpec proposal is created
- **THEN** it includes user outcome, primary criterion, secondary criteria, guardrails, thresholds, non-goals, and known blind spots

#### Scenario: Criteria are missing or vague
- **WHEN** the user request does not define what "better" means
- **THEN** the proposal records explicit unknowns and discovery questions instead of inventing a complete eval contract

### Requirement: Success criteria are specific, measurable, achievable, and relevant
The OptimizeSpec workflow SHALL guide agents to assess whether success criteria are specific, measurable, achievable for the target runtime, and relevant to the target agent's user outcome.

#### Scenario: Criterion is actionable
- **WHEN** a criterion names observable behavior, measurement method, target threshold, and user relevance
- **THEN** the workflow treats it as ready for eval-case and scorer design

#### Scenario: Criterion is not actionable
- **WHEN** a criterion is vague, unmeasurable, unrealistic, or disconnected from the target agent's purpose
- **THEN** the workflow records the weakness and asks for clarification or refinement

### Requirement: Eval categories are separated
The OptimizeSpec workflow SHALL distinguish system evals, agent quality evals, and optimizer acceptance criteria.

#### Scenario: System-loop eval succeeds
- **WHEN** a system-loop eval scores 1.0 because direct eval, compare, optimize, and evidence persistence all ran
- **THEN** the artifacts state that this proves the machinery works but does not by itself prove the target agent improved on product-quality criteria

#### Scenario: Agent quality eval is required
- **WHEN** the workflow claims the target agent improved
- **THEN** the claim is backed by an agent-quality eval tied to explicit success criteria

### Requirement: Proposal artifacts include critical unknowns
The OptimizeSpec workflow SHALL preserve missing criteria, missing task distribution, missing grader trust, and missing optimizer acceptance details as explicit unknowns.

#### Scenario: User knows the eval contract
- **WHEN** the user provides criteria, examples, scoring, and grader details
- **THEN** the proposal captures them directly

#### Scenario: User needs help defining the eval
- **WHEN** the user does not know the eval contract
- **THEN** the proposal captures the current hypothesis and lists discovery questions needed before implementation

### Requirement: Criteria-first workflow stays lightweight for users
The OptimizeSpec workflow SHALL keep criteria-first rigor inside the proposal and design stages instead of adding extra user-facing phases or a long intake questionnaire.

#### Scenario: User gives partial intent
- **WHEN** the user provides the target agent, desired improvement, representative examples, or obvious failure modes
- **THEN** the skill drafts a proposed eval contract with inferred criteria, scoring, grader strategy, guardrails, and open questions for confirmation

#### Scenario: More information is needed
- **WHEN** missing information materially affects eval validity or implementation
- **THEN** the skill asks a small number of plain-language follow-up questions and records the remaining unknowns instead of blocking on exhaustive criteria collection

#### Scenario: Proposal is ready for review
- **WHEN** the proposal is drafted
- **THEN** the user can review and correct a concise eval contract rather than authoring primary metrics, diagnostics, guardrails, task distribution, grading, and promotion rules from scratch

#### Scenario: Proposal needs implementation depth
- **WHEN** runner mechanics, detailed grader calibration, rollout lifecycle, or implementation planning are needed
- **THEN** the workflow records only the proposal-level decision or unknown and defers the deeper detail to design
