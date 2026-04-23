## ADDED Requirements

### Requirement: Skill pack uses concise triggerable skills
The system SHALL package the workflow as focused skills with clear metadata descriptions for starting, continuing, applying, and validating eval-driven GEPA changes.

#### Scenario: User starts an eval workflow
- **WHEN** the user asks to create a new eval or self-improvement change
- **THEN** the relevant skill can trigger from its description and create the first workflow artifact

#### Scenario: User asks to apply a completed plan
- **WHEN** the user asks to apply an eval change
- **THEN** the apply skill can trigger separately from the planning skills

### Requirement: Skills use progressive disclosure
The system SHALL keep core skill instructions concise and place detailed OpenSpec motivation, Claude Managed Agents guidance, GEPA patterns, scorer patterns, and templates in bundled references or assets.

#### Scenario: Skill needs runtime-specific details
- **WHEN** a skill needs Claude Managed Agents implementation guidance
- **THEN** it loads the relevant reference file rather than embedding all runtime details in `SKILL.md`

#### Scenario: Skill needs scorer examples
- **WHEN** a skill needs to generate or implement scorer logic
- **THEN** it loads scorer-pattern references only for that task

### Requirement: Skill pack includes artifact templates
The system SHALL provide reusable templates for proposal, design, specs, and tasks that are specialized for agent eval and GEPA optimization.

#### Scenario: Proposal artifact is created
- **WHEN** the workflow creates a proposal artifact
- **THEN** it uses an eval-focused template that includes target agent, input/output examples, numeric scoring, qualitative rubric, and unknowns

#### Scenario: Design artifact is created
- **WHEN** the workflow creates a design artifact
- **THEN** it uses a template that requires Claude Managed Agent runtime discovery and eval architecture decisions

### Requirement: Skill pack includes local reference material from this repo
The system SHALL include bundled reference material derived from this repo's GEPA and Claude Managed Agents prototype so future agents can adapt proven patterns.

#### Scenario: Apply skill designs GEPA evaluator code
- **WHEN** the apply skill needs GEPA evaluator guidance
- **THEN** it can reference the bundled evaluator, runtime, candidate, and optimizer patterns

### Requirement: Skill pack validates skill structure
The system SHALL include or document validation checks that confirm generated skills have valid frontmatter, trigger descriptions, references, and required files.

#### Scenario: Skill files are generated or modified
- **WHEN** the implementation creates or changes a skill
- **THEN** validation verifies the skill can be discovered and loaded by the intended agent environment

### Requirement: OpenSpec is used as workflow motivation
The system SHALL document OpenSpec's repo and artifact-guided flow as the motivating reference for the skill pack while avoiding feature-parity requirements.

#### Scenario: Agent reads workflow reference
- **WHEN** a coding agent reads the bundled workflow guidance
- **THEN** it sees OpenSpec called out as motivation for artifact structure, repo-local workflow, and apply ergonomics
