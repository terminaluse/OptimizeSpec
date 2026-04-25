## ADDED Requirements

### Requirement: Eval designs describe task distribution and edge cases
The GEPA eval workflow SHALL require design artifacts to explain the real-world task distribution, edge cases, failure modes, and split strategy for each agent-quality eval.

#### Scenario: Eval design mirrors real usage
- **WHEN** a design describes representative tasks, common cases, rare-but-important cases, and ambiguous or adversarial inputs
- **THEN** the workflow can proceed to eval-case implementation

#### Scenario: Eval design only contains toy examples
- **WHEN** a design has examples but does not explain whether they represent real usage
- **THEN** validation records a task-distribution omission

### Requirement: Eval cases preserve criteria metadata
The GEPA eval workflow SHALL support criteria metadata in eval-case artifacts so cases can be traced back to primary criteria, secondary diagnostics, guardrails, and eval category.

#### Scenario: Eval case is tied to a criterion
- **WHEN** an eval case is loaded
- **THEN** its metadata can identify the criterion or category it measures when that metadata is present

#### Scenario: Legacy eval case lacks criteria metadata
- **WHEN** an existing simple eval case does not contain criteria metadata
- **THEN** the runtime remains backward compatible while planning validation can still flag missing criteria in generated artifacts

### Requirement: Grading strategies explain grader trust
The GEPA eval workflow SHALL require each scorer or grader plan to state the grader type, why it is appropriate, calibration evidence, reliability risks, and human review triggers.

#### Scenario: Deterministic grader is appropriate
- **WHEN** the success condition can be checked with exact match, string match, schema validation, file existence, or code execution
- **THEN** the workflow prefers deterministic or code-based grading and records why it is reliable

#### Scenario: LLM grader is required
- **WHEN** the success condition requires judgement that deterministic scoring cannot capture
- **THEN** the workflow requires a tight rubric, constrained score output, calibration examples, and reliability checks before using the grader for optimization

### Requirement: Validation scores eval-design quality
The validation harness SHALL score generated artifacts for criteria specificity, task distribution fit, edge-case coverage, grader appropriateness, calibration, and known blind spots.

#### Scenario: Generated artifacts contain strong eval design
- **WHEN** generated proposal, design, and eval-case artifacts connect criteria, cases, graders, and blind spots coherently
- **THEN** artifact quality scoring awards criteria and grader-trust credit

#### Scenario: Generated artifacts omit grader reliability
- **WHEN** generated artifacts include a scorer but do not explain why it can be trusted
- **THEN** artifact quality scoring records a grader-trust omission
