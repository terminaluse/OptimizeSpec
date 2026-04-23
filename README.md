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

Run the local validation suite first. This does not call the live API:

```bash
pytest -q
```

Run the deterministic self-improvement smoke commands:

```bash
agent-gepa self-show-candidate --candidate skills/gepa-evals-common/assets/templates/seed-candidate.yaml --pretty
agent-gepa self-eval \
  --cases skills/gepa-evals-common/assets/templates/eval-cases.yaml \
  --candidate skills/gepa-evals-common/assets/templates/seed-candidate.yaml \
  --run-dir runs/self-eval-smoke
```

## Live API setup

Live Claude Managed Agents runs require Anthropic Research Preview access, the dedicated Research Preview SDK, and the Managed Agents beta header used by the package.

Install the preview SDK:

```bash
uv pip install -r requirements-managed-agents-preview.txt
```

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=...
```

Run one direct live evaluation. This is the cheapest useful live check:

```bash
agent-gepa eval-demo --max-runtime-seconds 300
```

Run the opt-in GEPA improvement sanity check. This starts with a deliberately weak candidate and asserts GEPA improves it from `0.0` to `1.0`:

```bash
AGENT_GEPA_RUN_LIVE_IMPROVEMENT=1 pytest tests/test_gepa_improvement_live.py -q
```

Run a small live GEPA optimization smoke:

```bash
agent-gepa optimize-demo --max-metric-calls 1 --max-runtime-seconds 300
```

`compare-demo` runs optimize plus before/after live evaluations across the demo suite. It is intentionally heavier and is documented in [TECHNICAL.md](TECHNICAL.md).

## Eval self-improvement workflow

The repo includes skills under `skills/` that guide a coding agent through creating and applying a GEPA eval workflow.

The skill folders follow the standard root-level convention:

```text
skills/
  gepa-evals-new/
    SKILL.md
  gepa-evals-continue/
    SKILL.md
  gepa-evals-apply/
    SKILL.md
  gepa-evals-verify/
    SKILL.md
  gepa-evals-common/
    SKILL.md
```

Use them in this order:

1. `gepa-evals-new`: start a change and define the eval objective, input/output examples, scoring, qualitative rubric, and ASI needs.
2. `gepa-evals-continue`: create the design, specs, and task artifacts.
3. `gepa-evals-apply`: implement the eval runner, scorers, compare path, and GEPA optimizer from the artifacts.
4. `gepa-evals-verify`: check artifact completeness, ASI quality, direct eval, compare, and optimize readiness.

If your coding agent automatically loads repo-local skills, point it at this repository and ask it to use the relevant `gepa-evals-*` skill. If it expects skills in a global directory, copy the needed `skills/gepa-evals-*` folders there.

The workflow is inspired by OpenSpec, but focused on agent self-improvement: the artifacts are not just documentation, they become the plan for a runnable eval and GEPA loop.

## License

MIT

## Current scope

The current implementation focuses on Claude Managed Agents. Other agent runtimes can be added later, but the first version intentionally keeps the runtime surface narrow so the eval and optimization loop can be validated end to end.

For implementation details, command references, candidate fields, preview SDK notes, and validation internals, see [TECHNICAL.md](TECHNICAL.md).
