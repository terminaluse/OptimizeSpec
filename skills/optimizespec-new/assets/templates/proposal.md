## Target Agent

- Name:
- Runtime: <inferred from repo inspection>
- Runtime evidence and confidence:
- Invocation:
- Constraints:

## Optimization System Location

- Decision: create new folder|use existing folder
- Path:
- Why this path fits the repo:
- Import/runtime access plan:
- Existing agent code to reuse:
- Existing tools, skills, MCP servers, env vars, or permissions to reuse:
- Run outputs path:

## Improvement Target

Describe the behavior GEPA should improve and why it matters.

## Success Criteria

- User outcome:
- Primary criterion:
- Secondary criteria:
- Guardrails:
- Acceptable threshold:
- Good threshold:
- Best-candidate threshold:
- Optional promotion threshold:
- Non-goals:
- Blind spots:

## Draft Eval Contract

I inferred this from the user request. The user should confirm or correct it.

- Primary success:
- Guardrails:
- Scoring:
- Grader:
- Open questions:

## Candidate Surface

List fields GEPA may mutate. Include only fields that can affect runtime behavior.

## Eval Examples

### Example: <id>

- Input:
- Expected:
- Output shape:
- Split: train|val|test

## Scoring

- Numeric score range:
- High score means:
- Partial score means:
- Failing score means:
- Deterministic scorer:
- Qualitative rubric:

## Grading Strategy

- Grader type: deterministic|code|llm|human|hybrid
- Why this grader is appropriate:
- Calibration examples:
- Reliability risks:
- Human review triggers:

## Optimizer Acceptance

- Optimized metric:
- Diagnostic metrics:
- Guardrail metrics:
- Best-candidate selection rule:
- Optional promotion or release rule:
- Regression tolerance:
- Required evidence:

## Evidence Model

- Run manifest:
- Candidate versions:
- Per-case scoring records:
- Judge records:
- ASI records:
- Rollout evidence:
- Optimizer lineage:
- Best-candidate evidence:
- Optional promotion evidence:
- Unknowns:

## Contract References

- Criteria-first:
- Candidate surface:
- Grader:
- Evidence:

## ASI Contract

List top-level ASI fields and field-specific ASI needs.

## Unknowns

List missing agent, scorer, example, or runtime details to resolve in design. If runtime cannot be inferred from repo inspection, record the evidence gap for design follow-up.
