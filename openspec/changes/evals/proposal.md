## Why

Agent teams need a repeatable way to turn real agent behavior into evaluations and then use GEPA to improve the agent from those evaluations. OpenSpec's repository and artifact-guided development flow are the motivating reference for how this should feel: lightweight, iterative, repo-local, and friendly to existing coding agents. This project already proves GEPA can optimize Claude Managed Agents, but it needs an OpenSpec-style skill workflow that helps users define evals, design a runnable evaluation system, and apply the resulting optimization plan.

## What Changes

- Add an artifact-driven skill workflow for creating eval specifications for a target agent, modeled on OpenSpec's proposal, design, specs, tasks, and apply flow.
- Use the OpenSpec repo as the primary product and workflow reference for developing this system, adapting its artifact structure and agent-facing skill ergonomics to the eval and GEPA optimization domain.
- Make the first workflow stage center on the eval contract: input examples, expected output examples, numeric scoring, qualitative scoring, and cases where the user needs the agent to help discover those details.
- Add a design workflow that instructs the coding agent to inspect how the target Claude Managed Agent is currently run, then propose how to evaluate it with GEPA-compatible runs, scores, and side information.
- Add subsystem specs for the eval definition workflow, Claude Managed Agent evaluation runtime, GEPA optimization wiring, and skill/apply workflow.
- Add an apply skill that implements the approved eval and GEPA optimization plan against the user's agent repository.
- Scope initial runtime support to Claude Managed Agents only; other runtimes such as Codex can be added later as new runtime capabilities.
- Package reference material from this repo's GEPA plus Claude Managed Agents prototype so generated skills can guide agents with concrete local patterns.

## Capabilities

### New Capabilities

- `agent-eval-definition-workflow`: Guide users and coding agents through defining eval input/output pairs, numeric scores, qualitative rubrics, and unresolved eval-discovery questions for a particular agent.
- `claude-managed-agent-eval-design`: Require the design phase to inspect the existing Claude Managed Agent setup and produce a concrete evaluation architecture for running sessions, collecting outputs, scoring outcomes, and surfacing side information.
- `gepa-agent-optimization-workflow`: Define how approved evals become GEPA datasets, evaluators, objectives, and optimization runs for improving a Claude Managed Agent.
- `self-improvement-skill-packaging`: Package the proposal/design/spec/tasks/apply workflow as concise skills with progressive disclosure, bundled references, templates, and validation guidance.
- `self-improvement-apply-workflow`: Implement an apply skill that reads completed artifacts and makes the code changes needed to add the eval runner and GEPA optimization loop to the target agent repo.

### Modified Capabilities

- None.

## Impact

Affected systems include the OpenSpec-style skill set, bundled reference materials, eval artifact templates, Claude Managed Agent runtime guidance, GEPA dataset/evaluator wiring, apply automation, and validation tests for the skills. The implementation should use this repo's existing GEPA and Claude Managed Agents code as reference material, while keeping the first version focused on Claude Managed Agents rather than a generalized multi-runtime abstraction.
