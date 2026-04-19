# Manual Test Findings

Date: 2026-04-18

This note captures the concrete errors, fixes, and remaining follow-up from the real-API manual behavior pass on `gepa-v2`.

## Scope

The goal of this pass was not to validate Anthropic's platform behavior. The goal was to validate:

- our request shapes
- our local validation and fallback behavior
- our runtime feature-flag behavior
- our GEPA wiring

## Behaviors Manually Verified

- Prompt-only candidate path works end to end.
- Fresh custom skill creation works end to end.
- Same-title custom skill versioning works when the `SKILL.md` `name` is unchanged.
- Anthropic-managed skill refs attach correctly.
- Limited environment config is accepted and reflected in runtime artifacts.
- Unrestricted environment config is accepted and reflected in runtime artifacts.
- Invalid custom skill metadata fails early with field-specific diagnostics.
- Invalid environment metadata fails early with field-specific diagnostics.
- Skill-count limit fails early with a local runtime error.
- Non-empty `subagent_specs` with multi-agent flag off fails early with a local runtime error.

## Errors Found

### 1. Custom skill create with an already-used `display_title` returned a 400

Observed error:

```text
Skill cannot reuse an existing display_title: Exact Output Checklist
```

Context:

- The initial create-or-reuse implementation tried `skills.create(...)`.
- Anthropic rejects creating a new skill when the `display_title` already exists.

Fix:

- Added fallback logic in [src/claude_gepa/runtime.py](/Users/vraja/Desktop/cc/sb0/claude-gepa/src/claude_gepa/runtime.py) to:
  - list existing custom skills by `display_title`
  - reuse the existing skill lineage
  - create a new version on that lineage instead of trying to create a duplicate skill

Status: fixed and manually verified.

### 2. Same-title custom skill fallback failed when `SKILL.md` `name` changed

Observed error from Anthropic before local fix:

```text
Skill name 'manual-behavior-skill-collision-3ef00f40' in SKILL.md must be consistent across all versions for a given `skill_id`. Expected 'manual-behavior-skill-3ef00f40'.
```

Context:

- Anthropic requires the `name` in `SKILL.md` to stay consistent across versions of the same skill lineage.
- Our fallback only keyed off `display_title`, which was insufficient.

Fix:

- Added `_validate_existing_skill_lineage(...)` in [src/claude_gepa/runtime.py](/Users/vraja/Desktop/cc/sb0/claude-gepa/src/claude_gepa/runtime.py).
- Before versioning onto an existing lineage, we now retrieve the latest version and compare its `name` with the candidate's `SKILL.md` `name`.
- If the names differ, we fail locally with a clear error instead of relying on Anthropic to reject the request.

Status: fixed and manually verified.

### 3. `optimize_anything()` config conflict with field-specific reflection templates

Observed error:

```text
Cannot specify both 'objective'/'background' parameters and a custom 'config.reflection.reflection_prompt_template'
```

Context:

- `optimize_demo()` had both:
  - `objective` / `background`
  - field-specific `reflection_prompt_template`
- GEPA treats those as mutually exclusive.

Fix:

- Removed `objective` and `background` from the `optimize_anything(...)` call path in [src/claude_gepa/optimizer.py](/Users/vraja/Desktop/cc/sb0/claude-gepa/src/claude_gepa/optimizer.py).

Status: fixed locally. Long end-to-end optimize workflow still needs a full manual completion run.

## Remaining Local Fixes / Polish

### 4. Session archive cleanup still logs noisy warnings on successful runs

Observed message on otherwise successful runs:

```text
skipped session archive because session status was running
```

Context:

- Some successful runs later show `session_status = idle` in the final runtime metadata.
- Archive cleanup still sometimes emits the earlier `running` warning.

Impact:

- Does not break evaluation.
- Makes successful runs look noisier than they should.

Likely fix direction:

- tighten the settle/archive ordering
- avoid recording the warning if the session later settles to `idle`

Status: not fixed yet.

## Non-Local / Access-Gated Findings

These are useful context, but they are not currently treated as local implementation bugs.

### 5. Multi-agent `callable_agents` is still preview-gated on this account / request path

Observed error from Anthropic:

```text
v1_create_agent_params.callable_agents: Extra inputs are not permitted
```

Context:

- The local implementation path exists.
- Multi-agent is now behind `CLAUDE_GEPA_ENABLE_MULTI_AGENT`.
- The current account/request path still rejects the preview field.

What we changed:

- Added `CLAUDE_GEPA_ENABLE_MULTI_AGENT` in [src/claude_gepa/runtime.py](/Users/vraja/Desktop/cc/sb0/claude-gepa/src/claude_gepa/runtime.py).
- When the flag is off, we fail early locally instead of calling the preview API path.

Status: intentionally gated behind a feature flag; not a local blocker for non-multi-agent work.

### 6. Outcome evaluation is unavailable on this account

Observed message:

```text
Outcome evaluation is unavailable for this session.
```

Context:

- We send the outcome definition correctly.
- The account/session still does not receive a real outcome grader result.

Status: treated as Anthropic feature availability, not a local implementation bug.

## Things Still Not Fully Manually Completed

These are not known bugs. They are incomplete manual verification items.

### 7. `optimize-demo` has not been manually waited through to a final completed payload after the latest fixes

Context:

- Real runs show progress and artifact creation under `runs/manual-live/optimize-demo`.
- A full completed end-to-end result was not yet captured during the manual pass.

What remains:

- run `claude-gepa optimize-demo` to completion
- inspect `candidates.json`, `run_log*`, and final best-candidate output

### 8. `compare-demo` has not yet been manually run to completion with the real API

Context:

- The reporting path exists.
- It has not yet been manually exercised to completion against the real API after the latest fixes.

What remains:

- run `claude-gepa compare-demo`
- inspect:
  - `input_candidate`
  - `final_candidate`
  - `candidate_diff`
  - per-task deltas

## Current Assessment

The direct schema/API contract surfaces we own are in better shape now:

- custom skills
- skill lineage/versioning
- environment config
- feature-flag gating
- early local validation

The main remaining local cleanup item is archive warning noise.

The remaining heavy manual work is operational verification of:

- `optimize-demo`
- `compare-demo`
