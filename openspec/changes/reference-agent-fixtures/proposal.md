## Why

The repo currently blurs reference inputs with generated optimization systems by committing full optimization-system changes under the Python Managed Agents example. That makes the product boundary harder to reason about: reference agents should help us test the CLI and skills, while optimization systems should be generated during tests or user workflows.

## What Changes

- Move reference agent definitions into an explicit test-fixture location.
- Remove committed full optimization-system examples from the normal repo surface unless they are minimal golden snapshots.
- Update tests so they generate optimization-system changes and runner output into temporary directories.
- Keep the Python Managed Agents implementation as a reference/test harness only, not as a committed optimization-system product example.
- Document the fixture boundary: committed reference agents are inputs; generated optimization systems are outputs.
- Add verification that release packaging, docs, and tests do not depend on committed generated optimization systems.

## Capabilities

### New Capabilities

- `reference-agent-fixtures`: Fixture ownership, generated-output boundaries, and verification rules for reference agents and optimization-system test outputs.

### Modified Capabilities

- None.

## Impact

Affected areas include `examples/py-claude-managed-agent/optimizespec/fixtures/agents`, `examples/py-claude-managed-agent/optimizespec/changes`, Python regression tests that import committed example optimization systems, TypeScript CLI tests that generate scaffolding, documentation, ignore rules, and package contents verification. The change should preserve coverage of the Claude Managed Agent reference path while making generated systems ephemeral or fixture-snapshot-only.
