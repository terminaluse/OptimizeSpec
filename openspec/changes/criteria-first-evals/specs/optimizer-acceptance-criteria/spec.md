## ADDED Requirements

### Requirement: GEPA workflows define an optimizer objective
Each GEPA eval workflow SHALL define the metric GEPA optimizes and distinguish it from diagnostic metrics and guardrail metrics.

#### Scenario: Optimizer objective is explicit
- **WHEN** a design configures GEPA optimization
- **THEN** it names the optimized metric, explains why that metric represents the primary criterion, and states whether it is higher-is-better

#### Scenario: Multiple metrics exist
- **WHEN** the eval has primary, secondary, cost, latency, safety, or reliability metrics
- **THEN** the workflow identifies which metrics are diagnostics and which metrics can block candidate promotion

### Requirement: Promotion requires acceptance rules
The GEPA eval workflow SHALL require optimizer acceptance rules before an optimized candidate is treated as better than the baseline.

#### Scenario: Candidate improves primary score
- **WHEN** a GEPA candidate improves the optimized metric
- **THEN** it is promoted only if it also satisfies guardrails, regression tolerance, and required evidence rules

#### Scenario: Candidate violates guardrail
- **WHEN** a GEPA candidate improves the primary score but regresses a guardrail metric beyond tolerance
- **THEN** the workflow blocks promotion and records the guardrail failure in ASI or comparison output

### Requirement: Compare output separates metric roles
Compare artifacts SHALL distinguish primary metric deltas, diagnostic metric deltas, guardrail status, and promotion decision.

#### Scenario: Compare result is acceptable
- **WHEN** baseline and candidate evaluations complete
- **THEN** comparison output includes optimized metric delta, diagnostic deltas, guardrail pass/fail status, and acceptance decision

#### Scenario: Compare result lacks acceptance context
- **WHEN** comparison output only lists aggregate score changes
- **THEN** validation records an optimizer-acceptance omission

### Requirement: System-loop success is not used as the sole quality gate
The workflow SHALL NOT treat system-loop success alone as evidence that a target agent improved on meaningful agent-quality criteria.

#### Scenario: Optimization loop runs successfully
- **WHEN** the actual system runs direct eval and GEPA optimization successfully
- **THEN** system-loop success can score 1.0 for machinery readiness

#### Scenario: Quality launch claim is made
- **WHEN** documentation or validation claims the target agent is better
- **THEN** the claim references agent-quality criteria and comparison evidence beyond system-loop success
