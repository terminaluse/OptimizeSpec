## Why

The OptimizeSpec skill workflow is promising, but it is not ready until it can prove that real agents can use the skills to create runnable evals, execute an optimization loop, and produce inspectable evidence of improvement or failure. This change adds the validation layer needed to turn the current prototype into a reliable workflow with clear pass/fail confidence.

## What Changes

- Add validation fixture coverage with example Claude Managed Agents that exercise the full new, continue, apply, eval, compare, and optimize flow.
- Add a true skill execution harness that validates whether the OptimizeSpec skills can create the expected artifacts from realistic agent inputs, not just whether static files exist.
- Add artifact quality scorers for proposals, designs, specs, tasks, eval cases, ASI, and runner outputs so generated work is assessed semantically and structurally.
- Add applied system scorers that run the generated eval runner and optimizer and assign 1.0 only when the system completes an optimization loop with expected outputs.
- Add negative fixtures that should fail or ask for clarification, covering missing eval contracts, ambiguous scoring, impossible runtime assumptions, and broken agent setup.
- Add validation documentation that explains the validation workflow, fixture expectations, known limitations, and the evidence required before broader release.
- Keep the scope focused on Claude Managed Agents and repo-local skill workflows; other runtimes remain out of scope for this eval workflow validation pass.

## Capabilities

### New Capabilities

- `fixture-agent-validation`: Define representative Claude Managed Agent fixtures and expected end-to-end behavior for validating the OptimizeSpec skill workflow.
- `skill-execution-harness`: Run the OptimizeSpec skills against fixture agents and capture whether the skills create complete, coherent artifacts and runnable implementations.
- `artifact-quality-scoring`: Score generated proposals, designs, specs, tasks, eval cases, ASI, and runner artifacts for required content, semantic fit, and critical omissions.
- `optimization-loop-validation`: Verify that applied eval systems can run direct evals, perform GEPA optimization rollouts, emit optimizer evidence, and score successful loops as 1.0.
- `negative-fixture-validation`: Validate that the workflow fails usefully or asks for clarification when inputs are incomplete, ambiguous, or incompatible with Claude Managed Agent assumptions.
- `validation-documentation`: Document the eval validation workflow, validation commands, evidence artifacts, current limitations, and release criteria.

### Modified Capabilities

None.

## Impact

This affects the repo-local OptimizeSpec skill pack under `skills/optimizespec-*`, validation fixtures under `optimizespec/`, the self-improvement runner and optimizer code under `src/optimizespec/`, CLI smoke paths, tests, and validation documentation. The change does not introduce a new agent runtime abstraction; it strengthens the existing Claude Managed Agent path and makes validation readiness measurable.
