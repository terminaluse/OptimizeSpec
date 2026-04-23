## ADDED Requirements

### Requirement: Evals compile into GEPA datasets
The system SHALL convert approved eval examples into GEPA-compatible training and validation datasets when enough examples are available.

#### Scenario: Proposal contains multiple eval examples
- **WHEN** the proposal or specs define enough eval examples for a split
- **THEN** the generated optimization workflow separates examples into train and validation sets

#### Scenario: Proposal contains too few eval examples
- **WHEN** there are not enough examples to form a meaningful validation set
- **THEN** the generated workflow records the limitation and still supports direct evaluation of the available examples

### Requirement: Runner exposes direct eval, optimize, compare, and candidate inspection operations
The system SHALL expose user-invokable operations for direct evaluation, GEPA optimization, candidate comparison, and candidate inspection using command shapes that fit the target repository.

#### Scenario: User invokes direct evaluation
- **WHEN** the user runs the generated direct-eval operation with a change path and candidate
- **THEN** the system evaluates the candidate on the selected eval cases without launching GEPA search

#### Scenario: User invokes optimization
- **WHEN** the user runs the generated optimize operation with a change path and budget
- **THEN** the system starts a GEPA optimization run using the approved eval suite and evaluator

#### Scenario: User invokes comparison
- **WHEN** the user runs the generated compare operation with baseline and candidate inputs
- **THEN** the system reports per-case and aggregate score deltas using the same eval suite

#### Scenario: User inspects candidate
- **WHEN** the user runs the generated candidate-inspection operation
- **THEN** the system prints the seed or current candidate fields that GEPA can mutate

### Requirement: Rollout executes one candidate on one eval case
The system SHALL define a rollout as one isolated execution of one candidate against one eval case through the target Claude Managed Agent runtime.

#### Scenario: Rollout starts
- **WHEN** the evaluator receives a candidate and eval case
- **THEN** it compiles the candidate, prepares the eval input, starts a Managed Agent session, and records the runtime identifiers for that rollout

#### Scenario: Rollout completes
- **WHEN** the Managed Agent session reaches a terminal, idle, timeout, or failure state
- **THEN** the evaluator collects outputs, traces, errors, usage, and generated artifacts before scoring

### Requirement: Evaluator returns score and side information
The system SHALL implement a GEPA-compatible evaluator that returns a numeric score and structured side information for every eval case.

#### Scenario: Eval case succeeds
- **WHEN** the target Managed Agent produces an output that satisfies the scorer
- **THEN** the evaluator returns a high numeric score and side information containing the actual output and positive judgement

#### Scenario: Eval case fails
- **WHEN** the target Managed Agent produces an incorrect output, errors, or times out
- **THEN** the evaluator returns a low numeric score and side information containing failure diagnostics useful for reflection

### Requirement: Evaluator emits field-specific ASI
The system SHALL include candidate-field-specific side information for each mutable candidate field when diagnostics can guide that field's reflection.

#### Scenario: Prompt field causes output-format failure
- **WHEN** a rollout fails because the agent ignored output-format instructions
- **THEN** side information includes targeted feedback for the prompt or instruction field responsible for that behavior

#### Scenario: Runtime configuration causes execution failure
- **WHEN** a rollout fails because skills, environment, tools, or resources are misconfigured
- **THEN** side information includes targeted feedback for the corresponding candidate configuration field

### Requirement: Evaluator supports numeric and qualitative scoring
The system SHALL support eval scoring that combines deterministic numeric checks with qualitative rubric judgement when the artifact contract calls for both.

#### Scenario: Deterministic scorer is sufficient
- **WHEN** the eval contract defines an exact-match or structured-output check
- **THEN** the evaluator can score the run without requiring qualitative model grading

#### Scenario: Qualitative judgement is required
- **WHEN** the eval contract includes rubric criteria that cannot be checked deterministically
- **THEN** the evaluator records qualitative judgement in side information and reflects it in the numeric score

### Requirement: Optimization includes objective and background
The system SHALL generate GEPA objective and background text from the approved artifacts so reflection has the target-agent context, eval goals, scoring semantics, and candidate-field descriptions.

#### Scenario: GEPA run starts
- **WHEN** the optimization entrypoint invokes GEPA
- **THEN** it passes objective and background text derived from the eval artifacts

### Requirement: Optimization configures reflection controls
The system SHALL configure GEPA reflection with a reflection model, component selection strategy, per-field reflection prompts where needed, metric-call budget, rollout runtime limit, run directory, and trace capture settings.

#### Scenario: Candidate fields are independent
- **WHEN** the design identifies candidate fields that can improve independently
- **THEN** the optimizer can use a round-robin or equivalent component selector

#### Scenario: Candidate fields are tightly coupled
- **WHEN** the design identifies candidate fields that must co-evolve
- **THEN** the optimizer configures reflection to update those fields together or records why that is deferred

### Requirement: Optimization can run direct eval before search
The system SHALL provide a way to evaluate the seed candidate against the eval suite before running a full GEPA optimization search.

#### Scenario: User validates eval setup
- **WHEN** the user requests a dry run or direct evaluation
- **THEN** the system runs the current candidate against the eval examples and reports scores without mutating the candidate

### Requirement: Run artifacts are persisted
The system SHALL persist enough optimization and evaluation artifacts to compare seed behavior, candidate behavior, scores, side information, and runtime failures.

#### Scenario: Optimization evaluates a candidate
- **WHEN** GEPA evaluates any candidate on an eval case
- **THEN** the system writes inspectable run artifacts for that candidate and eval case
