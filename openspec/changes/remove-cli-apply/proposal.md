## Why

Dogfooding showed that the TypeScript CLI `apply` command currently promises more than it delivers. The command validates a change and writes a small placeholder scaffold such as `eval-runner.ts`, `optimizer.ts`, or Python equivalents. It does not inspect the target agent deeply, reuse the agent's real runtime factories/tools/env/config, implement the evidence ledger, build ASI, wire compare/optimize/show-candidate correctly, or satisfy the runtime-specific apply contract.

That is a product risk. In the README and CLI help, `apply` reads like the command that turns approved artifacts into the actual optimization system. In practice, the real implementation path is the coding-agent skill `$optimizespec-apply`, because only the skill can inspect the repo, adapt to the runtime, and write the implementation described by the proposal/design/tasks.

For the release, OptimizeSpec should keep the CLI focused on project setup and artifact validation, and remove the misleading `apply` subcommand until it can either delegate clearly to an installed agent workflow or produce a real implementation that satisfies the runner/evidence contracts.

## What Changes

- Remove the `optimizespec apply` subcommand from the TypeScript CLI.
- Remove or quarantine the generic scaffold helpers behind the old apply command so they are not presented as product behavior.
- Update README and TECHNICAL docs to state that implementation is performed through `$optimizespec-apply`.
- Update CLI help and tests so `apply` is no longer listed as a supported CLI command.
- Preserve the `optimizespec-apply` skill as the implementation workflow.
- Keep `init`, `new change`, `continue`, `status`, and `validate` as the supported CLI surface for release.
- Leave any future `scaffold` command out of this change unless it is explicitly named and documented as a starter-template generator rather than an apply implementation.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `typescript-cli`: The CLI no longer exposes an `apply` command or claims to implement optimization systems.
- `self-improvement-apply-workflow`: Apply is skill-driven through `$optimizespec-apply`, not a TypeScript CLI subcommand.
- `release-documentation`: README and TECHNICAL docs describe the CLI as setup/artifact tooling and the skill as the implementation path.

## Impact

Affected areas include:

- `src/cli/index.ts`
- `test/cli.test.ts`
- `README.md`
- `TECHNICAL.md`
- Package dry-run expectations if command help or generated scaffold files were asserted
- Any OpenSpec/OptimizeSpec docs that mention `optimizespec apply`

This is a breaking CLI surface change before public release. It should reduce user confusion: users can still create, continue, inspect, and validate artifacts with the CLI, but implementation must happen through the installed skill workflow.
