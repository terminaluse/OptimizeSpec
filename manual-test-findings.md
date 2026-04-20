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

No known local correctness bug remains from the manual contract pass.

The previous archive-warning issue is now fixed.

### 4. Session archive cleanup warning noise

Previous observed message:

```text
skipped session archive because session status was running
```

Context:

- `_archive_session_if_idle(...)` was re-checking once and recording a warning too eagerly.
- Some runs later settled to `idle`, so the warning was stale noise rather than a real failure.

Fix:

- Updated [src/claude_gepa/runtime.py](/Users/vraja/Desktop/cc/sb0/claude-gepa/src/claude_gepa/runtime.py) so archive cleanup now polls briefly for `idle` before giving up.
- Added coverage for the “running then idle” case in [tests/test_runtime.py](/Users/vraja/Desktop/cc/sb0/claude-gepa/tests/test_runtime.py).
- Re-verified with a real successful run; the warning no longer appears.

Status: fixed and manually verified.

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

### 7. `optimize-demo` verification outcome

Context:

- A real run completed under `runs/manual-live/optimize-demo-final`.
- GEPA completed normally and proposed at least one new `system_prompt`.
- The base candidate remained the best candidate.

Observed result:

```text
Iteration 0: Base program full valset score: 1.0 over 5 / 5 examples
Iteration 1: Proposed new text for system_prompt ...
Iteration 1: New subsample score 3.0 is not better than old score 3.0, skipping
```

Implication:

- The optimizer path is functioning.
- The current `DEMO_SEED_CANDIDATE` plus current benchmark is already strong enough that the run did not accept a non-seed candidate.
- OpenSpec task `5.2` is therefore still open, but it is currently a benchmark/seed-pressure issue rather than a broken optimize workflow.

### 8. `compare-demo` has not yet been manually run to completion with the real API

Context:

- The reporting path exists.
- A real run is in progress under `runs/manual-live/compare-demo-final`.
- It has finished the optimize phase and has already produced baseline-eval artifacts, but a final completed compare payload has not yet been captured in this pass.

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
