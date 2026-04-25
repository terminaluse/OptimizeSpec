## Why

`agent-gepa` can run evals and optimization loops, but the workflow needs stronger critical thinking before GEPA optimizes against a metric. A runnable eval is not automatically a useful eval. If the success criteria are vague, the task distribution is unrealistic, or the grader is unreliable, GEPA can improve the wrong thing while still producing convincing artifacts.

Anthropic's evaluation guidance starts with defining specific, measurable, achievable, and relevant success criteria, then building task-specific evals that mirror real-world distributions, include edge cases, and use the fastest reliable grading method. This change brings that discipline into the GEPA eval workflow so users do not jump from "I want evals" directly to "run the optimizer" without first defining what "better" means and why the measurement is trustworthy.

## What Changes

- Add criteria-first guidance to the GEPA eval proposal flow so every new eval workflow separates user outcome, primary metric, secondary diagnostics, guardrails, thresholds, and known non-goals.
- Expand the proposal and design templates to require real task distribution, edge cases, train/validation/test intent, failure modes, and grader reliability before implementation begins.
- Add grading strategy guidance that distinguishes deterministic, code-based, LLM-based, and human grading, including when each method is appropriate and how LLM graders must be calibrated.
- Separate system-loop success from agent-quality success so `system_loop_success == 1.0` proves the machinery ran, not that the target agent improved on a meaningful product eval.
- Add optimizer acceptance criteria that define the metric GEPA optimizes, diagnostic metrics it observes, guardrail metrics that block promotion, and evidence required before accepting a candidate.
- Update validation expectations so generated proposals, designs, and eval cases are scored for criteria quality, dataset fit, grading trust, and optimization target clarity.
- Keep the user-facing workflow lightweight: criteria-first rigor should happen inside the proposal and design stages, not as extra phases or a long questionnaire.
- Guide the skill to ask a small number of plain-language questions, draft the eval contract from the user's intent and examples, and ask the user to correct or confirm instead of forcing them to author eval theory from scratch.
- Keep the first proposal concise: short bullets, only the examples needed to confirm direction, and deeper runner mechanics or grader calibration deferred to design.

## Capabilities

### New Capabilities

- `criteria-first-eval-workflow`: Require success criteria and eval design reasoning before examples, scoring, design, and apply artifacts are created.
- `eval-dataset-and-grader-trust`: Require eval cases and graders to document task distribution, edge cases, grader type, grader reliability, and calibration evidence.
- `optimizer-acceptance-criteria`: Require each GEPA workflow to state what the optimizer is allowed to improve, what metrics are diagnostic, and what guardrails prevent bad promotion.

### Modified Capabilities

- `agent-eval-definition-workflow`: Proposal artifacts should now include criteria-first sections instead of only target agent, examples, numeric scoring, qualitative rubric, ASI, and unknowns.
- `artifact-quality-scoring`: Artifact quality scorers should now check criteria quality, real-world task fit, grader trust, and optimizer acceptance details.
- `validation-documentation`: Documentation should explain the difference between system evals, agent quality evals, and optimizer acceptance criteria.

## Impact

This change primarily affects repo-local skills and validation artifacts:

- `skills/gepa-evals-new/SKILL.md`
- `skills/gepa-evals-common/assets/templates/proposal.md`
- `skills/gepa-evals-common/assets/templates/design.md`
- `skills/gepa-evals-common/assets/templates/eval-cases.yaml`
- `skills/gepa-evals-common/references/*.md`
- `src/agent_gepa/eval_validation.py`
- `gepa-evals/fixtures/agents/*`
- `TECHNICAL.md`
- `README.md` if the public explanation needs to mention criteria-first eval design

The runtime and optimizer code should only change if validation requires new structured fields for metrics, guardrails, or grader metadata. The default scope is to improve the workflow contracts first and keep the Claude Managed Agents runtime behavior stable.

The change should not add more required user-facing steps. It should make the existing proposal and design steps smarter: the user provides the agent, desired behavior, examples, and obvious failure modes; the skill drafts criteria, scoring, grader trust, and optimizer acceptance; then the user confirms or corrects the draft.

The proposal should remain a confirmation artifact rather than the full technical plan. It should be detailed enough to make the eval contract reviewable, but not so long that a new user feels they are reviewing an implementation design before agreeing on the eval.

## Source Motivation

- Anthropic: "Define success criteria and build evaluations" - https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
