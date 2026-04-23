# Claude GEPA

End-to-end prototype for optimizing Claude Managed Agents with GEPA's `optimize_anything(...)` API.

The repo keeps the GEPA boundary narrow:

- GEPA sees a text candidate, represented as `dict[str, str]`
- the evaluator compiles that candidate into fresh Anthropic Managed Agents resources
- compilation uses Anthropic structured outputs to turn raw text into typed internal models
- the evaluator returns `score` plus structured `side_info`

## Candidate fields

The mutable candidate surface is:

- `system_prompt`
- `task_prompt`
- `outcome_rubric`
- `skills`
- `environment_spec`
- `subagent_specs`

`skills`, `environment_spec`, and `subagent_specs` are still plain text at the GEPA boundary, but they compile through a typed internal compiler before runtime execution.

## Structured compiler path

The compiler uses Anthropic structured outputs to parse the raw candidate into typed internal models:

- prompt text is preserved exactly
- `skills` becomes a list of hybrid skill specs
- `environment_spec` becomes a typed cloud environment config
- `subagent_specs` becomes a list of callable subagent definitions

Compilation failures are scored evaluator failures, not crashes. The run artifacts keep both the raw candidate text and the canonical compiled form.

## Hybrid skills

The `skills` field is hybrid:

1. Reusable refs:

```yaml
- type: anthropic
  skill_id: xlsx

- type: custom
  skill_id: skill_abc123
  version: latest
```

2. Inline custom skill definitions:

```yaml
- type: custom
  display_title: Exact Output Checklist
  files:
    - path: exact-output-checklist/SKILL.md
      content: |
        ---
        name: exact-output-checklist
        description: Verification checklist for deterministic file-output tasks.
        ---
        Use this skill for exact file-output work.
```

For custom skill definitions:

- all files must share one top-level directory
- that directory must contain `SKILL.md`
- `SKILL.md` must include valid YAML frontmatter with `name` and `description`

The runtime resolves custom skill definitions with create-or-reuse semantics:

- exact content matches reuse the same materialized skill/version from a local registry
- new content under an existing logical skill key creates a new skill version
- otherwise the runtime creates a new custom skill through the Anthropic Skills API

The local registry lives at `.claude_gepa/skill_registry.json`.

## Environment schema

`environment_spec` uses the Claude Managed Agents cloud environment shape:

```yaml
type: cloud
networking:
  type: limited
  allowed_hosts: []
  allow_mcp_servers: false
  allow_package_managers: false
packages:
  type: packages
  apt: []
  cargo: []
  gem: []
  go: []
  npm: []
  pip: []
```

## Subagents

`subagent_specs` is a YAML list of callable subagent definitions:

```yaml
- name: verifier
  description: Reviews exact output files.
  system_prompt: |
    You independently verify output-file exactness.
  skills: []
```

The runtime now creates subagents as real Anthropic agents and wires them into the coordinator through `callable_agents`.

Important constraint:

- multi-agent is still a research-preview Anthropic feature
- multi-agent is disabled by default in this repo
- enable it with `CLAUDE_GEPA_ENABLE_MULTI_AGENT=1` once your Anthropic account has access
- the installed Python SDK does not type `callable_agents`, so the runtime sends that field through `extra_body`
- if `subagent_specs` is non-empty while the flag is off, the runtime fails early with a clear message instead of calling the preview API path
- if the flag is on but your account still does not have multi-agent access, those evaluations fail as scored runtime failures rather than crashing the loop

## Quick start

1. Create a virtual environment and install dependencies:

```bash
uv venv
source .venv/bin/activate
uv pip install -e '.[dev]'
```

2. Install the Managed Agents Research Preview SDK for live Managed Agent runs:

```bash
uv pip install -r requirements-managed-agents-preview.txt
```

Deterministic tests and fixture validation do not require this preview wheel, but live Managed Agents API calls do. The runtime uses the `managed-agents-2026-04-01-research-preview` beta header and will print this install command if the installed SDK is missing the required preview surfaces.

3. Export your Anthropic key:

```bash
export ANTHROPIC_API_KEY=...
```

4. Run one direct evaluation:

```bash
claude-gepa eval-demo
```

For live Managed Agent runs, allow enough time for the session to settle and cleanup:

```bash
claude-gepa eval-demo --max-runtime-seconds 300
```

5. Run a GEPA optimization job:

```bash
claude-gepa optimize-demo --max-metric-calls 48
```

6. Compare the seed candidate against the accepted best candidate:

```bash
claude-gepa compare-demo --max-metric-calls 48
```

## GEPA eval self-improvement workflow

This repo includes a repo-local skill pack for designing eval-driven self-improvement loops inspired by OpenSpec:

- `.codex/skills/gepa-evals-new`
- `.codex/skills/gepa-evals-continue`
- `.codex/skills/gepa-evals-apply`
- `.codex/skills/gepa-evals-verify`
- `.codex/skills/gepa-evals-common`

The default artifact layout for target projects is:

```text
gepa-evals/changes/<change-name>/
  proposal.md
  design.md
  specs/
  tasks.md
  eval-cases.yaml
  seed-candidate.yaml
```

The workflow works backward from GEPA reflection:

1. Define the behavior to improve and mutable candidate fields.
2. Define the Actionable Side Information GEPA needs after each rollout.
3. Define eval cases and scorers.
4. Design Claude Managed Agents rollouts and trace capture.
5. Apply the design by adding direct eval, optimize, compare, and candidate-inspection operations.

The reusable core lives in `src/claude_gepa/self_improvement.py`. It provides:

- portable eval case and scorer schemas
- direct candidate evaluation
- rollout artifact persistence
- ASI construction with field-specific feedback
- candidate comparison
- GEPA `optimize_anything(...)` wiring through a pluggable rollout executor

Fixture commands use a local template executor so the mechanics can be tested without live Anthropic credentials:

```bash
claude-gepa self-show-candidate --candidate .codex/skills/gepa-evals-common/assets/templates/seed-candidate.yaml --pretty
claude-gepa self-eval \
  --cases .codex/skills/gepa-evals-common/assets/templates/eval-cases.yaml \
  --candidate .codex/skills/gepa-evals-common/assets/templates/seed-candidate.yaml \
  --run-dir runs/self-eval-smoke
claude-gepa self-compare \
  --cases .codex/skills/gepa-evals-common/assets/templates/eval-cases.yaml \
  --baseline .codex/skills/gepa-evals-common/assets/templates/seed-candidate.yaml \
  --candidate .codex/skills/gepa-evals-common/assets/templates/seed-candidate.yaml \
  --run-dir runs/self-compare-smoke
```

For real Claude Managed Agent targets, replace the fixture executor with a rollout executor that reuses the target repo's existing Agent, Environment, Session, resource, event-stream, and cleanup code. Required live environment variables depend on that target repo, but `ANTHROPIC_API_KEY` is required for Managed Agents API calls.

Known v1 limits:

- only Claude Managed Agents are supported
- other agent runtimes such as Codex are intentionally out of scope
- qualitative rubric scoring needs a target-repo scorer implementation
- live optimize runs can be expensive; start with direct eval and small budgets

## Eval workflow validation

The eval workflow validation harness checks whether the GEPA eval skill workflow is ready to share beyond this repo. It deliberately separates hard contracts from semantic artifact scoring:

- hard contracts: fixture metadata, eval cases, candidate fields, rollout results, score results, ASI, command evidence, summaries, and comparisons
- semantic contracts: proposal, design, spec, task, and apply-plan prose

Validation readiness means deterministic fixtures can generate artifacts, run direct eval, run compare, invoke GEPA with a small budget, verify required evidence files, and show useful failure behavior for negative fixtures.

Deterministic smoke commands:

```bash
python -m claude_gepa.eval_validation generate \
  --fixture claude-gepa-managed-agent \
  --run-dir runs/eval-validation/managed-agent
python -m claude_gepa.eval_validation eval \
  --fixture claude-gepa-managed-agent \
  --run-dir runs/eval-validation/managed-agent \
  --skip-system-loop
python -m claude_gepa.eval_validation compare \
  --fixture claude-gepa-managed-agent \
  --run-dir runs/eval-validation/managed-agent \
  --skip-system-loop
python -m claude_gepa.eval_validation optimize \
  --fixture claude-gepa-managed-agent \
  --run-dir runs/eval-validation/managed-agent \
  --max-metric-calls 1 \
  --skip-system-loop
python -m claude_gepa.eval_validation verify \
  --fixture claude-gepa-managed-agent \
  --run-dir runs/eval-validation/managed-agent
```

The full system-loop eval is stricter: it runs generate, direct eval, compare, and optimize as actual commands and returns 1.0 only when required command evidence and artifacts exist:

```bash
python -m claude_gepa.eval_validation eval \
  --fixture claude-gepa-managed-agent \
  --run-dir runs/eval-validation/system-loop
```

Negative fixtures are available under `gepa-evals/fixtures/agents/` for missing eval contracts, missing scoring guidance, unsupported runtimes, and missing invocation details. A useful negative result is a blocked or clarification state with actionable diagnostics, not an invented apply plan.

Optional live validation is opt-in:

```bash
export CLAUDE_GEPA_EVAL_VALIDATION_LIVE=1
export ANTHROPIC_API_KEY=...
python -m claude_gepa.eval_validation eval \
  --fixture <live-fixture-id> \
  --run-dir runs/eval-validation/live
```

Live validation can incur API cost and is not required for the deterministic test suite. Current validation limits remain Claude Managed Agent-only runtime support, deterministic fixture coverage by default, and semantic scoring that catches critical omissions without requiring exact golden-file prose.

## Notes

- Fresh agents and environments are created for every evaluation.
- The benchmark now includes both simple regression tasks and richer structured transforms.
- `compare-demo` prints the input candidate, final candidate, unified diffs, and per-task score deltas.
- The runtime sends the initial outcome event with a narrow raw-HTTP fallback because the installed Anthropic Python SDK still does not expose a typed `define_outcome` event helper.
- If your account does not have outcome-grader access, the agent run can still succeed while the outcome status reports `"failed"` with an explanation like `"Outcome evaluation is unavailable for this session."`
