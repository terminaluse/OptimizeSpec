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

2. Export your Anthropic key:

```bash
export ANTHROPIC_API_KEY=...
```

3. Run one direct evaluation:

```bash
claude-gepa eval-demo
```

4. Run a GEPA optimization job:

```bash
claude-gepa optimize-demo --max-metric-calls 48
```

5. Compare the seed candidate against the accepted best candidate:

```bash
claude-gepa compare-demo --max-metric-calls 48
```

## Notes

- Fresh agents and environments are created for every evaluation.
- The benchmark now includes both simple regression tasks and richer structured transforms.
- `compare-demo` prints the input candidate, final candidate, unified diffs, and per-task score deltas.
- The runtime sends the initial outcome event with a narrow raw-HTTP fallback because the installed Anthropic Python SDK still does not expose a typed `define_outcome` event helper.
- If your account does not have outcome-grader access, the agent run can still succeed while the outcome status reports `"failed"` with an explanation like `"Outcome evaluation is unavailable for this session."`
