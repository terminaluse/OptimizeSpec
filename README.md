# Agent GEPA

Agent GEPA helps you create a self-improvement system for your agent.

Most agents fail in ways that are hard to reproduce: a prompt works on one task, misses an edge case on another, and gets worse when you try to fix it manually. This project gives you a practical eval and optimization loop around your Claude Managed Agent:

1. Define what good behavior looks like with evals.
2. Run the agent against those evals.
3. Capture scores and useful feedback from each rollout.
4. Let GEPA propose better agent instructions, skills, environment settings, and related configuration.
5. Compare the improved candidate against the baseline.

The goal is not just to run a benchmark. The goal is to build a repeatable improvement workflow that produces evidence: what changed, why it changed, which evals improved, and which failures still need work.

## Why care?

Use this when you have an agent that is important enough to improve systematically.

Agent GEPA can help you:

- create evals for a Claude Managed Agent
- optimize prompts and agent configuration with GEPA
- compare baseline and improved candidates on the same tasks
- capture Actionable Side Information so failures can guide the next candidate
- validate that an eval and optimization loop actually runs end to end
- avoid guessing whether an agent got better

This repo also includes a skill workflow for helping a coding agent create evals and apply the GEPA optimization loop to an existing Claude Managed Agents project.

## What is in this repo?

- A working Claude Managed Agents runtime wired to GEPA.
- A candidate model where GEPA can mutate prompts, skills, environment configuration, rubrics, and subagent specs.
- Direct eval, optimize, and compare commands.
- A repo-local skill pack under `skills/` for designing eval-driven self-improvement workflows.
- Fixture-based validation that checks whether the eval workflow can generate artifacts, run evals, run optimization, and fail usefully when inputs are incomplete.

## Quick start

Create an environment and install the package:

```bash
uv venv
source .venv/bin/activate
uv pip install -e '.[dev]'
```

For live Claude Managed Agents runs, install the Research Preview SDK:

```bash
uv pip install -r requirements-managed-agents-preview.txt
```

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=...
```

Run one direct live evaluation:

```bash
agent-gepa eval-demo --max-runtime-seconds 300
```

Run a GEPA optimization job:

```bash
agent-gepa optimize-demo --max-metric-calls 48
```

Compare the starting candidate against the optimized candidate:

```bash
agent-gepa compare-demo --max-metric-calls 48
```

## Eval self-improvement workflow

The repo includes skills under `skills/` that guide a coding agent through creating and applying a GEPA eval workflow:

- start a change
- define eval inputs, outputs, numeric scores, and qualitative rubrics
- design the eval runner and optimizer
- create specs and tasks
- apply the resulting eval and optimization system
- verify the implementation

The workflow is inspired by OpenSpec, but focused on agent self-improvement: the artifacts are not just documentation, they become the plan for a runnable eval and GEPA loop.

## Current scope

The current implementation focuses on Claude Managed Agents. Other agent runtimes can be added later, but the first version intentionally keeps the runtime surface narrow so the eval and optimization loop can be validated end to end.

For implementation details, command references, candidate fields, preview SDK notes, and validation internals, see [TECHNICAL.md](TECHNICAL.md).
