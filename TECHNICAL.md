# Technical Notes

This document contains the implementation details behind the user-facing workflow in [README.md](README.md).

## Architecture

The repo keeps the GEPA boundary narrow:

- GEPA sees a candidate represented as `dict[str, str]`.
- The evaluator compiles that candidate into fresh Claude Managed Agents resources.
- Compilation uses structured outputs to turn raw text into typed internal models.
- The evaluator returns a numeric `score` plus structured `side_info`.

The reusable self-improvement core lives in `src/agent_gepa/self_improvement.py`. It provides portable eval cases, scorer schemas, direct evaluation, rollout artifact persistence, ASI construction, candidate comparison, and GEPA `optimize_anything(...)` wiring through a pluggable rollout executor.

## Candidate fields

The mutable candidate surface is:

- `system_prompt`
- `task_prompt`
- `outcome_rubric`
- `skills`
- `environment_spec`
- `subagent_specs`

`skills`, `environment_spec`, and `subagent_specs` are plain text at the GEPA boundary, but they compile through typed internal models before runtime execution. Compilation failures are scored evaluator failures, not crashes. Run artifacts preserve both raw candidate text and canonical compiled form.

## Managed Agents preview SDK

Live Claude Managed Agents runs require the Research Preview SDK:

```bash
uv pip install -r requirements-managed-agents-preview.txt
```

The runtime uses this beta header for Managed Agents SDK calls:

```text
managed-agents-2026-04-01-research-preview
```

The raw `define_outcome` HTTP fallback uses its dedicated beta:

```text
agent-api-2026-03-01
```

The runtime performs a preflight check for the preview SDK surfaces and reports the install command if they are missing.

## Hybrid skills

The `skills` field supports reusable refs:

```yaml
- type: anthropic
  skill_id: xlsx

- type: custom
  skill_id: skill_abc123
  version: latest
```

It also supports inline custom skill definitions:

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

The runtime resolves custom skill definitions with create-or-reuse semantics. Exact content matches reuse the same materialized skill/version from `.agent_gepa/skill_registry.json`; new content under an existing logical key creates a new skill version.

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

Multi-agent support is preview-gated. It is disabled by default and can be enabled with:

```bash
export AGENT_GEPA_ENABLE_MULTI_AGENT=1
```

If `subagent_specs` is non-empty while the flag is off, the runtime fails early with a scored runtime failure instead of calling the preview API path.

## Commands

Install:

```bash
uv venv
source .venv/bin/activate
uv pip install -e '.[dev]'
uv pip install -r requirements-managed-agents-preview.txt
```

Live direct eval:

```bash
export ANTHROPIC_API_KEY=...
agent-gepa eval-demo --max-runtime-seconds 300
```

Optimization:

```bash
agent-gepa optimize-demo --max-metric-calls 48
```

Comparison:

```bash
agent-gepa compare-demo --max-metric-calls 48
```

`compare-demo` is intentionally heavier than `eval-demo` or `optimize-demo`: it runs GEPA and then evaluates the baseline and optimized candidates across the demo suite. For a quick live smoke, prefer `optimize-demo --max-metric-calls 1`.

Deterministic self-improvement smoke commands:

```bash
agent-gepa self-show-candidate --candidate skills/gepa-evals-common/assets/templates/seed-candidate.yaml --pretty
agent-gepa self-eval \
  --cases skills/gepa-evals-common/assets/templates/eval-cases.yaml \
  --candidate skills/gepa-evals-common/assets/templates/seed-candidate.yaml \
  --run-dir runs/self-eval-smoke
agent-gepa self-compare \
  --cases skills/gepa-evals-common/assets/templates/eval-cases.yaml \
  --baseline skills/gepa-evals-common/assets/templates/seed-candidate.yaml \
  --candidate skills/gepa-evals-common/assets/templates/seed-candidate.yaml \
  --run-dir runs/self-compare-smoke
```

## GEPA eval skill workflow

The repo-local skill pack is:

- `skills/gepa-evals-new`
- `skills/gepa-evals-continue`
- `skills/gepa-evals-apply`
- `skills/gepa-evals-verify`
- `skills/gepa-evals-common`

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

## Eval workflow validation

The eval workflow validation harness checks whether the GEPA eval skill workflow can produce runnable evidence. It separates hard contracts from semantic artifact scoring:

- hard contracts: fixture metadata, eval cases, candidate fields, rollout results, score results, ASI, command evidence, summaries, and comparisons
- semantic contracts: proposal, design, spec, task, and apply-plan prose

Deterministic smoke commands:

```bash
python -m agent_gepa.eval_validation generate \
  --fixture agent-gepa-managed-agent \
  --run-dir runs/eval-validation/managed-agent
python -m agent_gepa.eval_validation eval \
  --fixture agent-gepa-managed-agent \
  --run-dir runs/eval-validation/managed-agent \
  --skip-system-loop
python -m agent_gepa.eval_validation compare \
  --fixture agent-gepa-managed-agent \
  --run-dir runs/eval-validation/managed-agent \
  --skip-system-loop
python -m agent_gepa.eval_validation optimize \
  --fixture agent-gepa-managed-agent \
  --run-dir runs/eval-validation/managed-agent \
  --max-metric-calls 1 \
  --skip-system-loop
python -m agent_gepa.eval_validation verify \
  --fixture agent-gepa-managed-agent \
  --run-dir runs/eval-validation/managed-agent
```

The full system-loop eval is stricter: it runs generate, direct eval, compare, and optimize as actual commands and returns 1.0 only when required command evidence and artifacts exist:

```bash
python -m agent_gepa.eval_validation eval \
  --fixture agent-gepa-managed-agent \
  --run-dir runs/eval-validation/system-loop
```

Optional live validation:

```bash
export AGENT_GEPA_EVAL_VALIDATION_LIVE=1
export ANTHROPIC_API_KEY=...
python -m agent_gepa.eval_validation eval \
  --fixture <live-fixture-id> \
  --run-dir runs/eval-validation/live
```

Live GEPA improvement sanity check:

```bash
export AGENT_GEPA_RUN_LIVE_IMPROVEMENT=1
export ANTHROPIC_API_KEY=...
pytest tests/test_gepa_improvement_live.py -q
```

This opt-in test starts with a deliberately weak `answer_template: wrong` candidate, runs GEPA with a small budget, and asserts that the optimized candidate changes and improves the direct eval score from 0.0 to 1.0.

Negative fixtures live under `gepa-evals/fixtures/agents/` and cover missing eval contracts, missing scoring guidance, unsupported runtimes, and missing invocation details.

## Runtime notes

- Fresh agents and environments are created for every evaluation.
- `compare-demo` prints the input candidate, final candidate, unified diffs, and per-task score deltas.
- Cleanup/archive warnings are reported separately as `cleanup_warnings`; eval failures remain in `errors`.
- If outcome grading is unavailable, the task can still score correctly while `outcome_success` is 0.0.
