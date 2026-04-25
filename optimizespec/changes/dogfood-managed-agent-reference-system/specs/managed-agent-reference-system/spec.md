## ADDED Requirements

### Requirement: Dogfood adapter reuses the reference harness
The generated optimization system SHALL wrap the existing Python Claude Managed Agent reference harness instead of copying or reimplementing a parallel runtime.

#### Scenario: Adapter imports existing harness
- **WHEN** the dogfood command script runs from the generated system directory
- **THEN** it imports `optimizespec.eval_validation` from `examples/py-claude-managed-agent/src`
- **AND** it uses the `optimizespec-managed-agent` fixture as the default target.

### Requirement: Runner exposes required operations
The generated optimization system SHALL expose direct eval, compare, optimize, show-candidate, and verify operations.

#### Scenario: Maintainer runs the full dogfood loop
- **WHEN** the maintainer runs `python managed_agent_dogfood.py run-all --run-dir <path>`
- **THEN** the system runs generate, direct eval, compare, optimize, and verify in order
- **AND** the final verification result is written to `verification/verification.json`.

### Requirement: Evidence ledger is complete
The generated optimization system SHALL persist the required evidence records for generated artifacts, direct eval, compare, optimize, and verification.

#### Scenario: Verification inspects the run directory
- **WHEN** `python managed_agent_dogfood.py verify --run-dir <path>` is executed
- **THEN** verification checks generated artifacts, eval summary, comparison output, optimizer lineage, leaderboard, command logs, candidate registry, per-case scores, ASI, rollout records, and promotion evidence
- **AND** verification fails if required evidence is missing.

### Requirement: Candidate surfaces are inspectable
The generated optimization system SHALL make both the target Claude Managed Agent candidate surface and the dogfood optimizer guidance candidate visible to reviewers.

#### Scenario: Maintainer asks to show the candidate
- **WHEN** the maintainer runs `python managed_agent_dogfood.py show-candidate`
- **THEN** the system prints the target runtime candidate fields as JSON
- **AND** the output includes `system_prompt`, `task_prompt`, `outcome_rubric`, `skills`, `environment_spec`, and `subagent_specs`
- **AND** it also prints the workflow-guidance candidate fields used by the deterministic dogfood optimizer.

### Requirement: Deterministic readiness is separated from live quality
The generated optimization system SHALL report deterministic system-loop readiness separately from live Claude Managed Agent quality improvement.

#### Scenario: Deterministic run succeeds
- **WHEN** `run-all` completes without live credentials
- **THEN** the system reports deterministic verification success
- **AND** it does not claim live Managed Agent quality improvement.
