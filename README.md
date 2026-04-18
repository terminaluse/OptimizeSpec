# Claude GEPA

Minimal end-to-end prototype for optimizing Claude Managed Agents with GEPA's `optimize_anything(...)` API.

This project keeps the GEPA boundary narrow:

- GEPA sees a text candidate, represented as `dict[str, str]`
- the evaluator compiles that candidate into fresh Anthropic Managed Agents resources
- benchmark tasks are simple dummy file-processing jobs
- the evaluator returns `score` plus structured `side_info`

## Candidate fields

The default seed candidate uses these mutable text fields:

- `system_prompt`
- `task_prompt`
- `outcome_rubric`
- `skills`
- `environment_spec`
- `subagent_specs`

`skills`, `environment_spec`, and `subagent_specs` are encoded as YAML text so GEPA can edit them directly.

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

3. Run one direct evaluation against the dummy benchmark:

```bash
claude-gepa eval-demo
```

4. Run a tiny GEPA optimization job:

```bash
claude-gepa optimize-demo --max-metric-calls 3
```

## Notes

- This prototype creates fresh agent and environment resources for every candidate evaluation, as requested.
- Dummy tasks are intentionally simple so the end-to-end loop is easy to validate before widening the search space.
- `subagent_specs` are parsed at the candidate surface, but the current Anthropic Python SDK does not expose typed `callable_agents` support yet. Leave this field empty unless you are ready to extend the runtime against the research-preview multi-agent API manually.
- The runtime sends the initial outcome event with a narrow raw-HTTP fallback because the installed Anthropic Python SDK does not currently ship `define_outcome` event types. The rest of the runtime stays on the official SDK.
- If your account does not have outcome-grader access, the agent run can still succeed while the outcome status reports `"failed"` with an explanation like `"Outcome evaluation is unavailable for this session."`
