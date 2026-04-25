## Why

OptimizeSpec should be positioned as a general spec-driven workflow for building optimization systems for agents, but the current skill references blur that boundary. `optimizespec-common` sounds runtime-neutral, while several of its root-level references and templates are explicitly Claude Managed Agent specific. That makes the product harder to explain: users may think the whole workflow only applies to Claude Managed Agents, even though many contracts such as criteria, evidence, graders, ASI, candidate surfaces, optimizer acceptance, and verification are broadly useful.

The cleaner structure is to keep `optimizespec-common` as the shared skill, but separate core contracts from runtime-specific contracts inside it. Claude Managed Agent support can remain the only v1 implementation target, while its Agent, Environment, Session, resource-mounting, event-streaming, tools, skills, MCP, permissions, and preview-SDK assumptions live under a clearly named runtime folder.

## What Changes

- Reorganize `skills/optimizespec-common/references/` into generic `core/` references and runtime-specific `runtimes/claude-managed-agent/` references.
- Move Claude Managed Agent-specific contracts, runner details, and scorer/ASI runtime notes out of the root common reference namespace.
- Update phase skills to load core references for every OptimizeSpec workflow and load `runtimes/claude-managed-agent/` only when repo inspection identifies the target runtime as Claude Managed Agents.
- Update templates so proposals/designs record the runtime inferred from repo inspection without hardcoding Claude Managed Agents as the only possible value in generic sections.
- Preserve v1 behavior: apply still blocks non-Claude Managed Agent implementation unless another runtime adapter is added later.
- Update tests and package checks so installed skills remain self-contained after references move.

## Capabilities

### New Capabilities

- `runtime-scoped-reference-layout`: Common skill references are organized into core contracts and runtime-specific contracts.
- `claude-managed-agent-runtime-references`: Claude Managed Agent contracts live under a dedicated runtime subtree and are loaded only when applicable.

### Modified Capabilities

- `reference-contract-library`: The shared contract library distinguishes generic OptimizeSpec concepts from runtime-specific implementation details.
- `skill-contract-integration`: Phase skills choose references based on target runtime instead of treating Managed Agents references as universal common context.
- `self-improvement-apply-workflow`: Apply remains Claude Managed Agent-only for v1, but that limitation is expressed as a runtime adapter boundary rather than a common-library assumption.

## Impact

Affected areas include:

- `skills/optimizespec-common/references/`
- `skills/optimizespec-new/references/`
- `skills/optimizespec-continue/references/`
- `skills/optimizespec-apply/references/`
- `skills/optimizespec-verify/references/`
- Phase `SKILL.md` files that name specific reference paths
- Proposal and design templates
- Tests that verify skill self-containment and reference paths
- README or TECHNICAL wording that describes v1 runtime support

This change should not add a new skill package or change the user-facing workflow. It should make the internal reference layout honest: common stays common, and Claude Managed Agent-specific guidance remains available as the first runtime adapter.
