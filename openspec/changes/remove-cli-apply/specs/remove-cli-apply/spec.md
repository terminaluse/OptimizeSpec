## ADDED Requirements

### Requirement: CLI apply command is not exposed
The TypeScript OptimizeSpec CLI SHALL NOT expose `apply` as a supported command for the release.

#### Scenario: User views CLI help
- **WHEN** a user runs `optimizespec --help`
- **THEN** the command list includes setup and artifact commands such as `init`, `new`, `continue`, `status`, and `validate`
- **AND** the command list does not include `apply`

#### Scenario: User invokes removed apply command
- **WHEN** a user runs `optimizespec apply`
- **THEN** the CLI exits non-zero
- **AND** the output indicates that `apply` is not a supported CLI command

### Requirement: Implementation apply is skill-driven
OptimizeSpec SHALL document `$optimizespec-apply` as the supported implementation workflow.

#### Scenario: User reads quick start
- **WHEN** the README shows how to implement an approved optimization-system change
- **THEN** it uses `$optimizespec-apply <change-name>`
- **AND** it does not instruct users to run `optimizespec apply`

#### Scenario: Technical docs describe CLI scope
- **WHEN** TECHNICAL lists TypeScript CLI commands
- **THEN** it lists only artifact/setup/validation commands
- **AND** it states that implementation is handled by the installed apply skill

### Requirement: Placeholder scaffold behavior is not presented as apply
The release SHALL NOT present generic runner scaffolding as the implementation of an OptimizeSpec change.

#### Scenario: Apply-only scaffold helpers are removed
- **WHEN** maintainers inspect the TypeScript CLI source
- **THEN** apply-only renderer/scaffold helpers are absent or not reachable from a public command

#### Scenario: Package tests run
- **WHEN** maintainers run the TypeScript test suite
- **THEN** tests no longer assert that CLI apply writes placeholder runner files
- **AND** tests assert the supported command surface instead

### Requirement: Proposal implementation path remains valid
OptimizeSpec artifacts SHALL continue to record where implementation code should live even though the CLI does not apply it.

#### Scenario: Proposal is drafted
- **WHEN** `optimizespec-new` creates or guides `proposal.md`
- **THEN** the proposal still includes `Optimization System Location`
- **AND** `$optimizespec-apply` uses that path during implementation

### Requirement: Release package remains valid without CLI apply
The npm release package SHALL build, test, and pack successfully after removing the CLI apply command.

#### Scenario: Release checks run
- **WHEN** maintainers run `npm test` and `npm run pack:check`
- **THEN** the package builds successfully
- **AND** packaged skills still include `optimizespec-apply`
