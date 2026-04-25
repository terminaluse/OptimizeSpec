## ADDED Requirements

### Requirement: Common references are split by scope
The OptimizeSpec skill references SHALL separate runtime-neutral contracts from runtime-specific contracts inside the common skill reference tree.

#### Scenario: A user inspects common references
- **WHEN** the user opens `skills/optimizespec-common/references/`
- **THEN** generic contracts are grouped under `core/`
- **AND** runtime-specific contracts are grouped under `runtimes/<runtime-id>/`

#### Scenario: Claude Managed Agent contracts are present
- **WHEN** the v1 skill pack is installed
- **THEN** Claude Managed Agent-specific contracts are available under `references/runtimes/claude-managed-agent/`

### Requirement: Phase skills load references by target runtime
Phase skills SHALL load core contracts for generic OptimizeSpec work and load runtime-specific contracts only when the target runtime requires them.

#### Scenario: Proposal work starts
- **WHEN** `optimizespec-new` drafts a proposal
- **THEN** it loads the relevant `core/` contracts
- **AND** it records the target runtime and runtime unknowns without requiring runtime-specific implementation details too early

#### Scenario: Design targets Claude Managed Agents
- **WHEN** `optimizespec-continue` writes a design for a Claude Managed Agent project
- **THEN** it loads both relevant `core/` contracts and `runtimes/claude-managed-agent/` contracts

#### Scenario: Apply sees an unsupported runtime
- **WHEN** `optimizespec-apply` reads artifacts for a runtime without a supported runtime reference subtree
- **THEN** it records or reports an unsupported-runtime blocker instead of creating a parallel runtime implementation

### Requirement: Installed skill folders remain self-contained
Each installed OptimizeSpec skill folder SHALL contain every reference path named by its own `SKILL.md`, templates, and reference indexes.

#### Scenario: A phase skill references core contracts
- **WHEN** a phase skill names `references/core/<file>.md`
- **THEN** that file exists inside the same phase skill folder

#### Scenario: A phase skill references Claude Managed Agent contracts
- **WHEN** a phase skill names `references/runtimes/claude-managed-agent/<file>.md`
- **THEN** that file exists inside the same phase skill folder

### Requirement: Generic templates do not hardcode Claude Managed Agents as universal
Generic OptimizeSpec templates SHALL describe target runtime as a field and reserve Claude Managed Agent-specific requirements for runtime-specific design guidance.

#### Scenario: A proposal template is opened
- **WHEN** the template includes target agent metadata
- **THEN** it includes a runtime field without presenting Claude Managed Agents as the only possible product concept

#### Scenario: Apply support is documented
- **WHEN** docs or skill instructions describe v1 apply support
- **THEN** they state that Claude Managed Agents are the currently supported implementation runtime
- **AND** they do not imply that core OptimizeSpec contracts are Claude-only

### Requirement: Existing behavior is preserved for Claude Managed Agents
The restructuring SHALL preserve current Claude Managed Agent v1 behavior.

#### Scenario: A Claude Managed Agent project is optimized
- **WHEN** artifacts identify Claude Managed Agents as the runtime
- **THEN** the skill workflow can still find runner, runtime, scorer/ASI, evidence, optimizer, and verification guidance

#### Scenario: Release package is checked
- **WHEN** maintainers run package verification
- **THEN** the package includes the relocated reference files required by installed skills
