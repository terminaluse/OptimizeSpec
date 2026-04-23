## ADDED Requirements

### Requirement: Apply reads completed artifacts before implementation
The apply skill SHALL read the completed proposal, design, specs, and tasks before making code changes.

#### Scenario: Apply starts on complete artifacts
- **WHEN** the user asks to apply an eval change with all required artifacts present
- **THEN** the apply skill reads those artifacts and summarizes the implementation plan before editing files

#### Scenario: Apply starts before artifacts are complete
- **WHEN** required artifacts are missing
- **THEN** the apply skill reports the missing artifacts and does not implement the change

### Requirement: Apply inspects target repo before editing
The apply skill SHALL inspect the target repository's Claude Managed Agents implementation and adapt generated code to its existing language, structure, commands, and conventions.

#### Scenario: Target repo has existing Managed Agent entrypoints
- **WHEN** the apply skill finds existing agent creation or session-running code
- **THEN** it integrates eval execution with that code rather than creating an unrelated duplicate path

#### Scenario: Target repo lacks discoverable Managed Agents code
- **WHEN** the apply skill cannot find a Claude Managed Agents implementation
- **THEN** it pauses with a clear blocker instead of guessing a runtime architecture

### Requirement: Apply implements eval runner and scorer
The apply skill SHALL add or update code that can run approved eval cases against the target Claude Managed Agent and compute the required numeric and qualitative scores.

#### Scenario: Eval examples are deterministic
- **WHEN** the artifacts define exact input/output checks
- **THEN** the apply skill implements deterministic scoring for those checks

#### Scenario: Eval examples require rubric judgement
- **WHEN** the artifacts define qualitative scoring criteria
- **THEN** the apply skill implements a rubric judgement path and records the judgement in side information

### Requirement: Apply implements GEPA optimization entrypoint
The apply skill SHALL add or update an entrypoint that runs GEPA using the approved eval dataset, evaluator, objective, background, and candidate surface.

#### Scenario: User runs optimization command
- **WHEN** the generated optimization entrypoint is invoked with valid environment configuration
- **THEN** it starts a GEPA run against the target Managed Agent eval suite

#### Scenario: User runs direct evaluation command
- **WHEN** the generated direct-eval entrypoint is invoked
- **THEN** it evaluates the seed or current candidate without launching a full optimization search

### Requirement: Apply persists inspectable outputs
The apply skill SHALL ensure eval and optimization runs produce inspectable artifacts such as scores, side information, candidate snapshots, outputs, errors, and logs.

#### Scenario: Eval run completes
- **WHEN** an eval case finishes
- **THEN** the system writes run artifacts that allow the user to inspect what happened

#### Scenario: Eval run fails
- **WHEN** an eval case fails before scoring normally
- **THEN** the system writes a scored failure artifact with error details

### Requirement: Apply updates tasks incrementally
The apply skill SHALL mark tasks complete only after the corresponding implementation and verification step has been completed.

#### Scenario: Task implementation succeeds
- **WHEN** a task's code changes are complete and verified as far as local context allows
- **THEN** the apply skill marks that task complete in `tasks.md`

#### Scenario: Task implementation is blocked
- **WHEN** a task cannot be completed because of missing credentials, unsupported runtime, or unclear artifacts
- **THEN** the apply skill leaves the task unchecked and reports the blocker
