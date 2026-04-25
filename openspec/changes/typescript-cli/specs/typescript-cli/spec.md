## ADDED Requirements

### Requirement: OptimizeSpec exposes a TypeScript CLI
The system SHALL provide the supported public `optimizespec` command through a TypeScript/Node CLI rather than a Python console script.

#### Scenario: User runs the command
- **WHEN** a user installs the release package and runs `optimizespec --help`
- **THEN** the command executes through the TypeScript CLI entrypoint and displays the supported command list

#### Scenario: Python console script is not the public entrypoint
- **WHEN** the project is packaged for release
- **THEN** the release documentation and package metadata identify the TypeScript/Node CLI as the supported public command surface

### Requirement: CLI package follows Node release conventions
The system SHALL define a Node package layout with explicit TypeScript source, compiled JavaScript output, executable bin shim, build script, and package file allowlist.

#### Scenario: Build compiles the CLI
- **WHEN** maintainers run the CLI build
- **THEN** TypeScript sources compile into `dist/` and the executable shim loads the compiled CLI

#### Scenario: Package contains release files
- **WHEN** maintainers create a release package
- **THEN** the package includes the compiled CLI, bin shim, required assets, and excludes tests, caches, run outputs, and development-only artifacts

### Requirement: CLI preserves approved OptimizeSpec operations
The TypeScript CLI SHALL expose approved OptimizeSpec operations for creating, continuing, validating, and applying optimization-system specs, and SHALL document any legacy prototype commands as examples rather than core product commands.

#### Scenario: User starts an optimization system
- **WHEN** a user wants to define an optimization system for a target agent repository
- **THEN** the CLI provides commands or instructions for creating the spec artifacts, eval contract, design, tasks, and apply plan

#### Scenario: User applies a spec
- **WHEN** a user applies an approved OptimizeSpec change to a target repository
- **THEN** the generated or updated runner code lives in the target repository and matches the target repository's stack where practical

#### Scenario: Validation command exists
- **WHEN** a user or agent wants to validate OptimizeSpec workflow artifacts
- **THEN** the CLI provides a validation command with deterministic exit codes and inspectable output

### Requirement: Python prototype is not the shipped product runtime
The system SHALL NOT require the current Python prototype package for normal OptimizeSpec CLI installation or spec-authoring usage.

#### Scenario: Release package is installed
- **WHEN** a user installs the public OptimizeSpec CLI package
- **THEN** they can create, inspect, validate, and apply specs without installing the Python prototype package

#### Scenario: Python prototype remains in repo
- **WHEN** maintainers keep the existing Python Managed Agents/GEPA implementation
- **THEN** it is located under examples, fixtures, or reference material and is clearly documented as non-product runtime code

#### Scenario: Compatibility adapter is temporarily retained
- **WHEN** a release temporarily delegates an example command to Python
- **THEN** the command is marked as legacy or example-only, fails with actionable setup guidance when Python prerequisites are absent, and is not required for normal spec creation or application

### Requirement: Generated optimization systems are target-repo artifacts
OptimizeSpec SHALL generate or guide optimization-system implementation inside the user's target repository instead of relying on a bundled Python runtime.

#### Scenario: Target repository is TypeScript
- **WHEN** a TypeScript target agent repository applies an OptimizeSpec plan
- **THEN** the generated eval runner and optimization commands are TypeScript unless the approved design explicitly chooses another language

#### Scenario: Target repository is Python
- **WHEN** a Python target agent repository applies an OptimizeSpec plan
- **THEN** the generated eval runner and optimization commands may be Python and should follow that repository's conventions

#### Scenario: Reference example is used
- **WHEN** a user wants to study the current Claude Managed Agents and GEPA prototype
- **THEN** documentation points them to the example or fixture location without presenting it as the installed product package

### Requirement: Agent-compatible commands support JSON output
Commands intended for agents, scripts, CI, or validation SHALL support structured `--json` output.

#### Scenario: Agent requests machine-readable status
- **WHEN** an agent invokes an agent-compatible command with `--json`
- **THEN** the command writes valid JSON to stdout and avoids progress spinners or decorative text in stdout

#### Scenario: Command fails in JSON mode
- **WHEN** an agent-compatible command fails with `--json`
- **THEN** the command exits non-zero and emits a structured error object with code, message, and remediation fields

### Requirement: CLI release documents migration from Python command
The system SHALL document how users migrate from the Python console script to the TypeScript CLI.

#### Scenario: Existing user upgrades
- **WHEN** an existing user reads the release notes or README
- **THEN** they can identify the new install command, command compatibility status, required Node version, the non-product status of the Python prototype, and removed or renamed commands

#### Scenario: Old command reference remains in docs
- **WHEN** documentation references an obsolete Python command path or environment variable
- **THEN** release validation fails until the reference is updated or explicitly marked as legacy

### Requirement: CLI behavior is covered by TypeScript tests
The system SHALL include TypeScript tests for command registration, help output, JSON output, spec scaffolding, failure behavior, and packaging assumptions.

#### Scenario: Tests run in CI
- **WHEN** maintainers run the TypeScript test suite
- **THEN** it verifies the CLI without requiring live Anthropic credentials by default

#### Scenario: Live commands are gated
- **WHEN** tests exercise live Managed Agents behavior
- **THEN** those tests require explicit environment flags and credentials and remain skipped by default
