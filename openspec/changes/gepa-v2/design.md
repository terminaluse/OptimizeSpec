## Context

The repo already has a working `optimize_anything()` integration, but the current loop is still biased toward prompt optimization and partial runtime support. The candidate surface includes `system_prompt`, `task_prompt`, `outcome_rubric`, `skills`, `environment_spec`, and `subagent_specs`, yet not every field is fully compiled into meaningful Claude Managed Agents behavior today. In particular, `skills` is still limited to direct refs instead of full custom-skill materialization, `subagent_specs` is still guarded at runtime, and the benchmark mainly rewards prompt-level correctness.

The design goal for `gepa-v2` is to keep the simpler `optimize_anything()` API while making the full Claude Managed Agents surface real, stable, and worth optimizing. That means every candidate field must map to concrete Anthropic resources, structured fields must be parsed into typed internal models through Anthropic structured outputs rather than only local ad hoc parsing, and evaluator feedback must help GEPA improve the whole candidate rather than only the prompt fields.

This is a cross-cutting change. It touches candidate modeling, runtime compilation, session orchestration, evaluator feedback, benchmarking, and optimization configuration. It also needs to remain compatible with the existing Anthropic Python SDK integration and current repo layout.

## Goals / Non-Goals

**Goals:**
- Preserve `optimize_anything()` as the public optimization API.
- Treat the full candidate surface as mutable and behaviorally meaningful: `system_prompt`, `task_prompt`, `outcome_rubric`, `skills`, `environment_spec`, and `subagent_specs`.
- Make `skills` a declarative hybrid surface that can either reuse existing Anthropic skills or create missing custom skills through the Skills API.
- Parse and canonicalize structured fields so GEPA mutates stable text formats instead of arbitrary free-form blobs.
- Compile every candidate field into fresh Claude Managed Agents resources during evaluation.
- Replace the current subagent guardrail with real subagent creation and wiring.
- Provide field-specific reflection guidance and side information so structured fields can improve coherently.
- Expand the benchmark and run defaults so full-surface search has enough signal and budget to succeed.

**Non-Goals:**
- Migrate the project from `optimize_anything()` to `gepa.optimize()` or a custom adapter in this change.
- Introduce nested Python objects as the GEPA-facing candidate type.
- Add arbitrary provider abstraction beyond Claude Managed Agents.
- Solve account-side Anthropic feature availability issues, such as outcomes research-preview gating.

## Decisions

### 1. Keep the GEPA boundary as `dict[str, str]`, but make the internal compiler typed via Anthropic structured outputs

The optimizable candidate remains a flat `dict[str, str]` so it fits `optimize_anything()` directly. Internally, the compiler will send the raw candidate text to Anthropic using structured outputs and parse the response into typed structures such as hybrid `SkillSpec`, `EnvironmentSpec`, and `SubagentSpec` before making Managed Agents and Skills API calls.

This preserves the simple GEPA integration while giving the runtime a strict compilation boundary. It also lets the same model family that will execute the agent normalize candidate text into a schema-constrained internal representation, reducing the need for brittle local parsing logic.

Alternatives considered:
- Switch to `gepa.optimize()` with a custom adapter.
  Rejected for now because it adds API and abstraction complexity without solving the immediate runtime gaps.
- Keep all fields as raw strings throughout runtime execution.
  Rejected because it makes validation, compilation, and error reporting too fragile for full-surface search.
- Parse structured fields only with local YAML/JSON loaders.
  Rejected because Anthropic structured outputs provide a cleaner typed compiler boundary and better align with the eventual Managed Agents execution surface.

### 2. Use Anthropic structured outputs as the candidate compiler boundary

The candidate compiler will use the Anthropic Python SDK structured-output path for Python, specifically the structured-output response shape backed by `output_config.format`, with `client.messages.parse()` as the preferred SDK helper where practical. The compiler schema will define the typed shape of the internal candidate object and reject invalid structures at the schema boundary.

This makes candidate parsing explicit, type-safe, and model-assisted. It also produces clearer failure modes than best-effort local parsing alone, because compile failures can be attributed to schema mismatch instead of ambiguous parser behavior.

Alternatives considered:
- Accept user or GEPA text verbatim and compile directly.
  Rejected because format drift and semantically identical variants would bloat the search space.
- Rely on one-off prompt instructions without structured-output enforcement.
  Rejected because the compiler needs a guaranteed typed output shape, not just a likely one.

### 3. Canonicalize structured fields after typed compilation

Structured text fields such as `skills`, `environment_spec`, and `subagent_specs` will be re-emitted in a stable canonical format after the Anthropic structured-output step. For `skills`, the canonical form will preserve whether each entry is an external reusable ref or a custom skill definition whose identity is based on canonicalized content. The canonical form becomes the effective compiled representation and the stable basis for identity, caching, resource reuse, and debugging.

This reduces search noise by ensuring semantically equivalent configs do not behave like distinct candidates merely because of formatting differences. It also makes experiment artifacts easier to compare.

Alternatives considered:
- Preserve the raw candidate text as the only compiled representation.
  Rejected because the structured-output compiler is meant to normalize candidate intent into stable internal structures.

### 4. Make every candidate field materially affect runtime behavior

`gepa-v2` will only consider the full-surface search valid if each field changes actual Managed Agents execution:
- `system_prompt` becomes the root agent system prompt
- `task_prompt` becomes the task instruction template
- `outcome_rubric` becomes the outcome definition rubric text
- `skills` becomes a declarative skill surface that resolves to existing reusable skills or newly created custom skill artifacts before attachment to the agent or subagents
- `environment_spec` becomes the created environment config
- `subagent_specs` becomes callable subagents created and wired into the primary agent

This prevents “fake optimization” where GEPA mutates fields that the runtime silently ignores.

Alternatives considered:
- Keep unsupported fields in the candidate and ignore them until later.
  Rejected because it misrepresents the actual optimization surface and wastes search budget.

### 4a. Resolve candidate-defined skills with create-or-reuse semantics

The compiler/runtime boundary will treat `skills` as hybrid declarative input rather than simple refs. A skill entry may reference an existing Anthropic skill artifact directly or describe a custom skill payload that must be materialized through the Skills API. The compiler will canonicalize the skill content, derive a deterministic identity from it, and reuse an existing matching skill when possible. If no matching skill exists, the runtime will create one, then attach the resulting `skill_id` and version to the managed agent or subagent.

This keeps the GEPA surface simple while making skill mutations real and reproducible. It also avoids creating duplicate custom skills for semantically identical candidates.

Alternatives considered:
- Keep `skills` as refs only and introduce a separate `custom_skills` field.
  Rejected because it splits one conceptual managed-agent surface into two optimization fields and makes reflection more awkward.
- Always create a new skill for every evaluation.
  Rejected because it produces duplicate resources and makes evaluation artifacts noisy and expensive.

### 5. Add field-specific reflection guidance without changing APIs

The optimization loop will use `ReflectionConfig(reflection_prompt_template=...)` with per-field templates. Prompt fields will receive behavior-oriented mutation guidance, while structured fields will receive schema-and-semantics guidance.

This is the lightest-weight way to make `optimize_anything()` behave more like a structured optimizer without adding adapter complexity. It also keeps control localized to repo-owned configuration.

Alternatives considered:
- Depend only on evaluator side information with no field-specific reflection prompts.
  Rejected because structured fields need stronger up-front mutation constraints than prompts.
- Use a fully custom proposer immediately.
  Deferred because prompt-template guidance plus runtime validation is sufficient for the first full-surface version.

### 6. Treat parser and compiler failures as informative evaluation results

Invalid candidate structures, failed structured-output parsing, failed subagent compilation, or unsupported environment configs will not crash the optimization loop. Instead, the evaluator will return a scored failure with field-specific diagnostics in `side_info`.

This is required for full-surface optimization because GEPA will inevitably explore invalid or low-quality structured candidates. The loop needs those failures to become learning signal instead of hard stops.

Alternatives considered:
- Raise exceptions on any invalid candidate.
  Rejected because it reduces search robustness and wastes expensive evaluations.

### 7. Expand the benchmark so non-prompt fields can earn signal

The benchmark will retain simple file-transformation tasks for regression checks but will add tasks that make environment, skills, or delegation meaningful. Examples include tasks that require preconfigured helper instructions, environment-specific tools/packages, or multi-step decomposition where a subagent can improve completion quality.

This is necessary because full-surface optimization only makes sense if the benchmark rewards more than prompt wording.

Alternatives considered:
- Reuse the current dummy benchmark unchanged.
  Rejected because it under-exercises the richer candidate surface.

### 8. Increase optimization and runtime budgets by default

The default optimization budget and per-session runtime ceiling will be higher than the current minimal prototype defaults. Full-surface search needs enough room to evaluate seed candidates, generate meaningful mutations, and validate improvements across train and validation tasks.

This follows what the live runs already showed: a too-small budget often only benchmarks the seed, while the corrected larger budget allows GEPA to discover and validate a better candidate.

Alternatives considered:
- Keep low defaults and require manual tuning for every run.
  Rejected because the default experience would underrepresent the system’s actual capabilities.

## Risks / Trade-offs

- [Structured-output compilation adds latency and a new model dependency] -> Keep the compiler schema small, reuse stable schemas to benefit from Anthropic schema caching, and isolate compile calls in one helper layer.
- [Structured fields still produce semantically weak mutations] -> Use canonicalization, field-specific reflection prompts, and field-specific side information to keep the search space coherent.
- [Hybrid skill materialization can create duplicate or drifting skill artifacts] -> Use canonical skill content, deterministic identity, and create-or-reuse lookup before calling the Skills API create path.
- [Subagent support may be constrained by Anthropic SDK surface or beta behavior] -> Keep subagent compilation isolated in the runtime layer and fall back to informative scored failures if the API path is unavailable.
- [Full-surface search is slower and more expensive] -> Raise defaults deliberately, keep early benchmarks small, and preserve artifact logging so expensive runs are inspectable and resumable.
- [Benchmark expansion can hide regressions on the simpler tasks] -> Keep the existing file-transform tasks in the suite as a stable regression subset.
- [Canonicalization may collapse some intentionally distinct text variants] -> Restrict canonicalization to structured config fields and leave prompt fields fully free-form.

## Migration Plan

1. Refactor candidate parsing so the raw GEPA candidate is compiled through Anthropic structured outputs into typed internal models and canonical text forms.
2. Implement a compiler layer that turns the typed parsed candidate into Anthropic skill, agent, environment, file, and subagent resources.
3. Replace the subagent runtime guard with real callable-agent creation and attachment.
4. Add field-specific reflection templates and richer `side_info` payloads.
5. Expand the benchmark and tune default run budgets around the larger candidate surface.
6. Re-run end-to-end comparisons and verify that GEPA can improve a full-surface candidate over the seed.

Rollback is straightforward because the public entrypoint remains `optimize_anything()`. If full-surface compilation proves unstable, the runtime can temporarily disable individual compile paths while preserving the candidate API and experiment artifacts.

## Open Questions

- Which benchmark tasks best expose skill and subagent quality without introducing too much unrelated complexity?
- How much environment variation should be allowed in v2 before search cost outweighs value?
- Should canonicalization rewrite candidate text before persistence, or only for compilation and identity?
- If Anthropic outcomes remain unavailable for some sessions, should the benchmark rely entirely on external grading for v2?
