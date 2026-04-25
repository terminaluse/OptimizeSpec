---
name: gepa-evals-new
description: Start a repo-local GEPA eval self-improvement change for Claude Managed Agents. Use when the user wants to create evals, optimize an agent with GEPA, define an agent self-improvement loop, or begin an ASI-first evaluation workflow.
---

# GEPA Evals New

Create the first artifact for a GEPA eval self-improvement change. The default workflow directory is:

```text
gepa-evals/changes/<change-name>/
```

## Workflow

1. Derive or confirm a kebab-case change name.
2. Create `gepa-evals/changes/<change-name>/proposal.md`.
3. Use `../gepa-evals-common/assets/templates/proposal.md` as the structure.
4. Capture known details without inventing missing information.
5. Start from plain-language user intent and examples. Do not make the user fill out a long eval-design form.
6. If the user has not provided enough information, ask at most 3-5 focused questions before drafting. Prefer questions like:
   - What agent should improve?
   - What behavior should get better?
   - What are 2-3 representative tasks?
   - What would make an answer clearly bad?
   - Which concerns matter most: correctness, formatting, safety, cost, speed, or tool use?
7. Draft the success criteria, scoring plan, grader strategy, and optimizer acceptance rules from the user's input.
8. Ask the user to confirm or correct the inferred eval contract in the proposal rather than requiring them to author primary metrics, diagnostics, guardrails, task distribution, grading, and promotion rules from scratch.
9. If target agent, criteria, scorer, examples, grader trust, or optimizer acceptance are incomplete, record explicit unknowns and candidate discovery questions.
10. Keep `proposal.md` concise. Prefer short bullets and no more than 2-3 eval examples. Defer deeper runner mechanics, calibration details, and implementation design to `design.md` unless they are required to confirm the eval contract.
11. Stop after creating `proposal.md`.

## Required Proposal Content

- Target agent and runtime context.
- Behavior to improve.
- Candidate fields GEPA may mutate, if known.
- Success criteria: user outcome, primary criterion, secondary criteria, guardrails, thresholds, non-goals, and blind spots.
- Draft eval contract for user confirmation or correction.
- Input examples and expected outputs or output shapes.
- Numeric scoring intent, preferably `0.0` to `1.0`.
- Qualitative rubric.
- Grading strategy: deterministic, code-based, LLM-based, human, or hybrid, plus why the grader can be trusted.
- Optimizer acceptance: optimized metric, diagnostic metrics, guardrails, promotion rule, regression tolerance, and required evidence.
- ASI fields needed for reflection.
- Unknowns to resolve in design.

For workflow motivation, read `../gepa-evals-common/references/workflow.md`.
For criteria-first eval design, read `../gepa-evals-common/references/criteria-first-evals.md`.
For ASI-first framing, read `../gepa-evals-common/references/gepa-reflection.md`.
