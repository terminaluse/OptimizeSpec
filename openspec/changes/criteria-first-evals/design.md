## Context

The current OptimizeSpec workflow asks for target agent context, input/output examples, numeric scoring, qualitative rubric, and ASI. That is necessary, but it does not force enough evaluation design discipline. A user or coding agent can still create an eval with unclear criteria, unrepresentative examples, no edge cases, and a grader that is easy for GEPA to overfit.

Anthropic's test-and-evaluate guidance emphasizes that evals should start from success criteria, then use task-specific cases, automation where possible, enough volume, and the fastest reliable grader. It also calls out that most real use cases need multidimensional criteria rather than one vague score. `optimizespec` should encode that into the skills because GEPA optimizes whatever feedback it receives.

Constraints:

- Keep runtime scope focused on Claude Managed Agents.
- Keep OpenSpec and OptimizeSpec artifacts readable Markdown/YAML.
- Do not require users to know all answers up front; unknowns should become explicit discovery questions.
- Do not add more user-facing stages for criteria work; fold criteria thinking into proposal and design.
- Ask at most 3-5 plain-language questions before drafting when the user has not provided a complete eval contract.
- Keep the first proposal concise; defer runner mechanics, calibration depth, and implementation design to the design artifact.
- Do not over-schema prose artifacts; use structured fields only where validation or runtime behavior consumes them.
- Preserve deterministic local validation as the default path.

## Goals / Non-Goals

**Goals:**

- Require every new OptimizeSpec workflow to define criteria before eval cases and scoring mechanics.
- Separate product-quality evals from system-loop evals.
- Make primary metrics, secondary diagnostics, guardrails, thresholds, and non-goals visible in proposal and design artifacts.
- Require eval cases to reflect real task distribution, edge cases, failure modes, and split intent.
- Require every grader to state its method, reason for trust, calibration needs, and reliability risks.
- Give GEPA a clear optimizer objective and promotion rule instead of a loose numeric score.
- Update validation so low-quality eval design is caught before implementation is considered ready.
- Keep the workflow approachable by having the agent draft criteria and ask the user to confirm or correct the draft.

**Non-Goals:**

- Replace GEPA or change its optimizer API.
- Build a hosted eval authoring UI.
- Add runtime support beyond Claude Managed Agents.
- Require live API calls for criteria validation.
- Force a single universal metric schema for every future agent runtime.
- Turn the proposal step into a long intake form or eval theory lesson.

## Decisions

### Add a criteria-first proposal section

The proposal template should add a required section before examples:

- User outcome
- Primary success criterion
- Secondary criteria or diagnostic metrics
- Guardrail criteria that must not regress
- Acceptable threshold, good threshold, and promotion threshold
- Known non-goals
- Known blind spots

Rationale: GEPA should optimize against an explicit success definition. Examples and rubrics are downstream of that definition, not a substitute for it.

Alternative considered: keep criteria inside the existing scoring section. That is simpler, but it makes criteria feel like implementation detail instead of the core product decision.

### Keep criteria-first lightweight for users

The workflow should not add new user-facing phases for primary metrics, diagnostics, guardrails, task distribution, grading, and promotion. Instead, the skill should collect a small amount of plain-language input:

- What agent should improve?
- What behavior should get better?
- What are 2-3 representative tasks?
- What would make an answer clearly bad?
- Which concerns matter most, such as correctness, formatting, safety, cost, speed, or tool use?

The skill should then draft the success criteria, scoring plan, grader strategy, and optimizer acceptance rules. The user should be asked to confirm or correct the draft, not to fill out every field from scratch. If more information is still needed, the proposal should record explicit unknowns and discovery questions rather than blocking on a long questionnaire.

The first proposal should be a concise confirmation artifact. It should use short bullets, include only the examples needed to confirm the direction, and leave detailed runner mechanics, scorer calibration, rollout lifecycle, and implementation planning for `design.md`.

Rationale: criteria-first rigor is valuable only if users can start quickly. The agent should carry the eval-design burden and use the user's feedback to refine the draft.

Alternative considered: ask the user every criteria and grading question up front. That would produce complete inputs when answered, but it would make the skill feel too heavy and discourage adoption.

### Require eval design reasoning before implementation design

The design template should add a section explaining:

- Real-world task distribution
- Edge cases and adversarial or ambiguous inputs
- Train/validation/test split intent
- Expected failure modes
- Whether the eval measures product quality, system-loop readiness, or both
- What the eval intentionally does not measure

Rationale: A small toy eval can prove wiring, but GEPA needs representative feedback to improve real behavior. The design must make the eval's validity visible before runner mechanics are implemented.

Alternative considered: only encode this in `eval-cases.yaml`. That would help parsing, but humans need to review the reasoning before cases are finalized.

### Make grader trust explicit

Every scorer should state:

- Grader type: deterministic, code-based, LLM-based, human, or hybrid
- Why that grader is appropriate for the criterion
- Whether the grader is higher-is-better
- Calibration examples or checks
- Known failure modes
- When human review is needed

LLM-based graders should require a tight rubric, constrained score output, and grader reliability checks before they are trusted for optimization.

Rationale: GEPA can exploit weak graders. Grader trust has to be part of the workflow, not an afterthought.

Alternative considered: tell users to prefer deterministic graders in prose only. That is good advice, but the artifacts need fields and validation hooks so the advice is enforced.

### Separate three eval categories

The workflow should distinguish:

- System evals: prove the eval runner, compare path, optimizer loop, persistence, and evidence artifacts work.
- Agent quality evals: measure whether the target agent improved on meaningful behavior.
- Optimizer acceptance criteria: decide whether a GEPA candidate should be promoted.

Rationale: The current binary system-loop success check is valuable, but it is not an agent-quality claim. Users need to see which kind of evidence they have.

Alternative considered: keep one aggregate score. That hides the difference between "the loop ran" and "the agent got better."

### Add optimizer acceptance rules

Each workflow should define:

- The objective metric GEPA optimizes
- Metrics that GEPA sees as diagnostics
- Guardrail metrics that block promotion
- Minimum validation improvement
- Regression tolerance
- Required evidence files for acceptance
- Manual review triggers

Rationale: A candidate can improve the primary score while becoming worse in a way users care about. Promotion should be gated by explicit acceptance rules.

Alternative considered: let users inspect compare output manually. That is useful, but it is too easy to accept candidates based on a single score.

### Update validation to score eval-design quality

`src/optimizespec/eval_validation.py` and fixtures should add scoring checks for:

- Criteria specificity and measurability
- Relevance to the target agent and user outcome
- Achievable thresholds
- Task distribution and edge cases
- Grader appropriateness and calibration
- Separation of system evals and agent quality evals
- Optimizer objective and guardrails

Rationale: The skill workflow will not reliably improve unless generated artifacts are held to the eval-quality bar, not just artifact-completeness checks.

Alternative considered: update only docs and templates. That would improve examples but would not catch regressions in agent-generated artifacts.

## Artifact Shape

Proposal artifacts should add:

```markdown
## Success Criteria

- User outcome:
- Primary criterion:
- Secondary criteria:
- Guardrails:
- Acceptable threshold:
- Good threshold:
- Promotion threshold:
- Non-goals:
- Blind spots:
```

The proposal step should also include a short confirmation surface:

```markdown
## Draft Eval Contract

I inferred this from your request:

- Primary success:
- Guardrails:
- Scoring:
- Grader:
- Open questions:
```

The skill should only ask focused follow-up questions when the missing answer materially affects eval validity or implementation.

Design artifacts should add:

```markdown
## Eval Design

- Eval category: system|agent-quality|optimizer-acceptance
- Real task distribution:
- Edge cases:
- Failure modes:
- Split strategy:
- What this eval does not measure:

## Grading Strategy

- Grader type:
- Why this grader is appropriate:
- Calibration examples:
- Reliability risks:
- Human review triggers:

## Optimizer Acceptance

- Optimized metric:
- Diagnostic metrics:
- Guardrail metrics:
- Promotion rule:
- Regression tolerance:
- Required evidence:
```

Eval cases should support optional metadata for criteria and grader trust without breaking existing simple cases:

```yaml
criteria:
  primary: ...
  secondary: []
  guardrails: []
  category: agent-quality
grader:
  type: deterministic
  rationale: ...
  calibration: []
acceptance:
  optimized_metric: ...
  promotion_rule: ...
```

The exact field names can be finalized during implementation. The important contract is that proposal, design, and eval cases all preserve the criteria-to-grader-to-optimizer chain.

## Validation Strategy

The change should add deterministic tests around:

- Proposal template contains success criteria and trust sections.
- `optimizespec-new` requires criteria-first content and records unknowns when criteria are missing.
- `optimizespec-new` does not require a long questionnaire before drafting a proposal.
- `optimizespec-new` keeps first proposals concise and defers implementation depth to design.
- Artifact quality scoring fails or lowers score when proposals omit primary metric, thresholds, guardrails, task distribution, or grader trust.
- Negative fixtures with vague "make it better" requests are treated as clarification-needed, not as ready eval specs.
- System-loop validation remains separate from agent-quality validation.

The default test suite should not require live Anthropic calls. Live Managed Agent validation can remain opt-in.

## Risks / Trade-offs

- [Risk] More proposal fields can make the workflow feel heavier. -> Mitigation: allow unknowns and discovery questions, but do not let missing criteria silently become a runnable optimization plan.
- [Risk] Criteria-first guidance becomes a long form. -> Mitigation: cap initial user-facing questions, draft inferred criteria, and ask for correction instead of requiring complete authoring.
- [Risk] Users may overfit to one primary metric. -> Mitigation: require diagnostics and guardrails even when GEPA optimizes a single objective.
- [Risk] Criteria scoring can become subjective. -> Mitigation: score for explicitness, relevance, thresholds, and grader trust rather than perfect wording.
- [Risk] Extra metadata can complicate simple deterministic evals. -> Mitigation: keep metadata optional at the runtime boundary while making it required in planning artifacts.
- [Risk] LLM graders can be unreliable. -> Mitigation: require constrained outputs, calibration examples, and reliability checks before use in optimization.

## Migration Plan

1. Update skill instructions and templates with criteria-first sections.
2. Update references to explain success criteria, eval categories, grader trust, and optimizer acceptance.
3. Update validation scoring to catch missing criteria and grader trust.
4. Update fixtures and existing generated examples as needed.
5. Run deterministic tests and one local eval validation smoke.
6. Keep existing simple `self-eval` cases working; metadata additions should be backward compatible.

Rollback is simple because this change mainly adds planning and validation requirements. If the new validation is too strict, loosen scorers while keeping the criteria-first templates.

## Open Questions

- Should criteria metadata be required in `eval-cases.yaml`, or only in proposal/design artifacts for the first iteration?
- Should optimizer acceptance rules be enforced by code immediately, or initially documented and scored in artifact validation?
- What is the minimum calibration evidence for an LLM grader before it can be used for GEPA optimization?
- Should `README.md` mention criteria-first eval design, or should that stay in technical and skill docs?
- What exact question budget should the skill use before drafting: three questions, five questions, or a soft maximum based on ambiguity?
