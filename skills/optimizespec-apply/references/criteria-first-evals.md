# Criteria-First Evals

Criteria-first does not mean more user-facing steps. It means the agent does more eval-design work inside the proposal and design stages.

## Lightweight Intake

Ask for plain-language intent and examples. If details are missing, ask at most 3-5 focused questions before drafting:

- What agent should improve?
- What behavior should get better?
- What are 2-3 representative tasks?
- What would make an answer clearly bad?
- Which concerns matter most: correctness, formatting, safety, cost, speed, or tool use?

Then draft the eval contract and ask the user to confirm or correct it. Do not make the user fill out primary metrics, diagnostics, guardrails, task distribution, grader calibration, and promotion rules from scratch.

Keep the first proposal concise. Use short bullets, include only the examples needed to confirm the eval direction, and defer deeper runner mechanics, calibration details, and implementation design to `design.md`. The proposal is a confirmation artifact, not the full technical plan.

## Success Criteria

Every proposal should identify:

- user outcome
- primary criterion
- secondary criteria or diagnostic metrics
- guardrails that must not regress
- acceptable, good, and promotion thresholds
- non-goals
- blind spots

If the user has not supplied these, infer a draft and list unknowns. Do not silently turn vague intent into a runnable optimization plan.

## Eval Categories

Separate three kinds of evidence:

- System evals prove the runner, compare path, optimizer loop, persistence, and evidence artifacts work.
- Agent quality evals measure whether the agent improved on meaningful behavior.
- Optimizer acceptance criteria decide whether a GEPA candidate should be promoted.

`system_loop_success == 1.0` proves the machinery ran. It is not, by itself, proof that the agent got better.

## Grader Trust

Prefer the fastest reliable grader:

- Use deterministic or code-based grading when exact output, schema validity, file existence, or programmatic checks are enough.
- Use LLM or human grading when judgement is required.
- For LLM grading, require a tight rubric, constrained score output, calibration examples, reliability risks, and human review triggers.

GEPA can optimize against weak graders, so grader trust is part of the eval contract.

## Optimizer Acceptance

Before applying GEPA output, define:

- optimized metric
- diagnostic metrics
- guardrail metrics
- promotion rule
- regression tolerance
- required evidence
- manual review triggers

A candidate can improve the primary score and still be unacceptable if it violates a guardrail or lacks evidence.

Source motivation: Anthropic's evaluation guidance recommends defining success criteria before building evals and using task-specific, representative tests with reliable grading: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
