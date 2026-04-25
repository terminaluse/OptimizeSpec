## ADDED Requirements

### Requirement: Eval systems persist an auditable run ledger
Applied GEPA eval systems SHALL persist enough evidence for each run to audit candidates, scores, judge output, ASI, rollouts, optimizer decisions, and promotion outcomes.

#### Scenario: A direct eval run completes
- **WHEN** a candidate is evaluated against eval cases
- **THEN** the system records a run manifest, candidate identifier, eval case identifiers, per-case scores, aggregate summary, judge output when present, side information when present, and rollout evidence

#### Scenario: An optimization loop completes
- **WHEN** GEPA proposes, evaluates, compares, or selects candidates
- **THEN** the system records candidate lineage, optimizer events, leaderboard or comparison results, and the decision that accepted, rejected, or promoted a candidate

### Requirement: Candidate versions are identifiable
The evidence ledger SHALL make every evaluated candidate version identifiable and traceable to its mutable surface.

#### Scenario: A candidate is generated
- **WHEN** the optimizer creates a candidate
- **THEN** the ledger records candidate id, parent candidate id when applicable, mutated files or fields, creation reason, and enough metadata to reproduce or inspect the candidate

#### Scenario: A candidate is promoted
- **WHEN** a candidate replaces the baseline or becomes the selected output
- **THEN** the ledger records the promotion reason, compared candidates, objective metric result, guardrail result, and any manual review requirement

### Requirement: Per-case evidence is preserved
Eval systems SHALL preserve case-level evidence rather than only aggregate scores.

#### Scenario: A case receives a numeric score
- **WHEN** a scorer returns a numeric result
- **THEN** the ledger stores the score, score bounds or higher-is-better direction, criterion measured, scorer identity, and any error or abstention

#### Scenario: A judge produces qualitative output
- **WHEN** an LLM, human, or hybrid grader produces qualitative judgment
- **THEN** the ledger stores the rubric version or criterion, rationale summary, structured judge output, calibration status when known, and reliability warnings when present

#### Scenario: Actionable side information is produced
- **WHEN** a rollout produces feedback intended for GEPA reflection
- **THEN** the ledger stores the ASI, the case and candidate it came from, the failure or improvement signal it describes, and whether it was passed into the optimizer

### Requirement: Evidence separates system-loop proof from agent-quality proof
The evidence ledger SHALL distinguish machinery success from evidence that the target agent improved on meaningful criteria.

#### Scenario: The system loop succeeds
- **WHEN** direct eval, compare, optimize, and persistence steps all run successfully
- **THEN** the ledger may record system-loop success but does not treat that result as an agent-quality improvement claim

#### Scenario: Agent improvement is claimed
- **WHEN** artifacts claim the target agent improved
- **THEN** the claim is backed by agent-quality eval results tied to criteria, case-level evidence, grader output, and promotion rules

### Requirement: Evidence layout is documented before apply work is complete
Eval design artifacts SHALL define where run evidence is written and how reviewers inspect it before implementation is considered ready.

#### Scenario: Design specifies the runner
- **WHEN** a design describes how evals and optimization will run
- **THEN** it also describes the run ledger path, required files, candidate identifiers, score records, judge records, ASI records, optimizer lineage, and promotion record

#### Scenario: Design omits evidence persistence
- **WHEN** a design only states that scores will be printed or summarized
- **THEN** validation treats the design as incomplete for a GEPA self-improvement system
