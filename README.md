# agent-gepa

Create a self-improvement system for your agent.

`agent-gepa` helps you take an existing agent, define evals for it, and run GEPA to improve it with evidence instead of guesswork. You decide what good behavior looks like. The system runs the agent, scores the results, proposes intelligent improvements, and tests whether those changes actually help.

## Why This Exists

Most agent improvement is still manual:

- make a prompt change
- run a few examples
- hope the change generalizes

That breaks down quickly. It is hard to tell whether the agent really improved, what got worse, or which changes are worth keeping.

`agent-gepa` gives you a repeatable loop:

1. Define evals for your agent.
2. Run the current agent on them.
3. Score the outputs with numbers and qualitative feedback.
4. Let GEPA propose changes.
5. Keep the changes that perform better.

> qualitative feedback

You can define a LLM as judge that's able to give detailed qualitative feedback such as:
```
The agent wasn't able to identify the close button to close the page
```


Define a small component that you put in prod

then define the output you're storing


Then 





What's difficult?
Coming up with the rubric







## What You Get

- A way to define evals for an existing agent
- A runner for executing those evals and storing rollout artifacts
- A GEPA optimization loop that proposes and tests improvements
- A working example for Claude Managed Agents
- Skills that help a coding agent create evals and apply the system to another project

## Who This Is For

This repo is for you if:

- you already have an agent
- you want to improve it systematically
- you can describe what "better" means with an eval
- you want to start with Claude Managed Agents

## Quickstart

Create a virtual environment and install the project:

```bash
uv venv
source .venv/bin/activate
uv pip install -e '.[dev]'
```

Run the local test suite:

```bash
pytest -q
```

Run the deterministic local eval example:

```bash
agent-gepa self-eval \
  --cases skills/gepa-evals-common/assets/templates/eval-cases.yaml \
  --candidate skills/gepa-evals-common/assets/templates/seed-candidate.yaml \
  --run-dir runs/self-eval-smoke
```

This does not call the live API. It proves the eval runner can load cases, run rollouts, score them, and write artifacts.

## Run The Live Example

Live runs require Anthropic Research Preview access for Claude Managed Agents.

Install the preview SDK:

```bash
uv pip install -r requirements-managed-agents-preview.txt
```

Set your API key:

```bash
export ANTHROPIC_API_KEY=...
```

Run one live evaluation:

```bash
agent-gepa eval-demo --max-runtime-seconds 300
```

Run a small optimization loop:

```bash
agent-gepa optimize-demo --max-metric-calls 1 --max-runtime-seconds 300
```

What those commands do:

- `eval-demo`: runs the example Claude Managed Agent once and scores it
- `optimize-demo`: runs a small GEPA loop and tests candidate improvements

`--max-metric-calls` is the eval budget for GEPA. A higher value gives it more chances to test improvements, but also means more live rollouts.

## What Happens When You Run It

1. You define eval cases for your agent.
2. The system runs your agent on those cases.
3. Each rollout gets scored.
4. GEPA uses the results and feedback to propose changes.
5. New candidates are evaluated against the same cases.
6. You can compare the baseline and improved versions directly.

## Start With The Example

The fastest path is to use the included Claude Managed Agent example first. Once that works, adapt the eval cases, scoring logic, and candidate fields to match your own agent.

## Use The Skills

The repo includes a `skills/` folder for coding agents that can use repo-local skills:

```text
skills/
  gepa-evals-new/
  gepa-evals-continue/
  gepa-evals-apply/
  gepa-evals-verify/
  gepa-evals-common/
```

Use them in this order:

1. `gepa-evals-new`: define the eval and what improvement means
2. `gepa-evals-continue`: create the design, specs, and tasks
3. `gepa-evals-apply`: implement the eval runner and optimizer
4. `gepa-evals-verify`: check that eval, compare, and optimize flows are ready

## Learn More

- [TECHNICAL.md](TECHNICAL.md) for architecture, runtime details, candidate fields, and command reference
- [skills/gepa-evals-new/SKILL.md](skills/gepa-evals-new/SKILL.md) for creating a new GEPA eval workflow
- [skills/gepa-evals-apply/SKILL.md](skills/gepa-evals-apply/SKILL.md) for implementing the resulting system

## License

MIT
