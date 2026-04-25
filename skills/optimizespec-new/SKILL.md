---
name: optimizespec-new
description: Start a repo-local OptimizeSpec self-improvement change for Claude Managed Agents. Use when the user wants to create evals, optimize an agent with GEPA, define an agent self-improvement loop, or begin an ASI-first evaluation workflow.
---

# OptimizeSpec New

Create the first artifact for an OptimizeSpec self-improvement change. The default workflow directory is:

```text
optimizespec/changes/<change-name>/
```

## Workflow

1. Derive or confirm a kebab-case change name.
2. Read `references/reference-contracts.md`, then load only the proposal-phase references it names: criteria-first, candidate surface, grader, and evidence.
3. Create `optimizespec/changes/<change-name>/proposal.md`.
4. Use `assets/templates/proposal.md` as the structure.
5. Capture known details without inventing missing information.
6. Start from plain-language user intent and examples. Do not make the user fill out a long eval-design form.
7. If the user has not provided enough information, ask at most 3-5 focused questions before drafting. Prefer questions like:
   - What agent should improve?
   - What behavior should get better?
   - What are 2-3 representative tasks?
   - What would make an answer clearly bad?
   - Which concerns matter most: correctness, formatting, safety, cost, speed, or tool use?
8. Draft the success criteria, scoring plan, grader strategy, evidence model, and optimizer acceptance rules from the user's input.
9. Ask the user to confirm or correct the inferred eval contract in the proposal rather than requiring them to author primary metrics, diagnostics, guardrails, task distribution, grading, evidence persistence, and promotion rules from scratch.
10. If the agent, criteria, scorer, examples, grader trust, evidence model, or optimizer acceptance are incomplete, record explicit unknowns and candidate discovery questions.
11. Keep `proposal.md` concise. Prefer short bullets and no more than 2-3 eval examples. Defer deeper runner mechanics, calibration details, ledger file layout, and implementation design to `design.md` unless they are required to confirm the eval contract.
12. Stop after creating `proposal.md`.

## Required Proposal Content

- Agent and runtime context.
- Behavior to improve.
- Candidate fields GEPA may mutate, if known.
- Success criteria: user outcome, primary criterion, secondary criteria, guardrails, thresholds, non-goals, and blind spots.
- Draft eval contract for user confirmation or correction.
- Input examples and expected outputs or output shapes.
- Numeric scoring intent, preferably `0.0` to `1.0`.
- Qualitative rubric.
- Grading strategy: deterministic, code-based, LLM-based, human, or hybrid, plus why the grader can be trusted.
- Optimizer acceptance: optimized metric, diagnostic metrics, guardrails, promotion rule, regression tolerance, and required evidence.
- Evidence model: run manifest, candidate versions, scoring records, judge records, ASI records, rollout evidence, optimizer lineage, and promotion evidence at a high level.
- Contract references that should guide design and apply work.
- ASI fields needed for reflection.
- Unknowns to resolve in design.

For workflow motivation, read `references/workflow.md`.
For criteria-first eval design, read `references/criteria-first-evals.md`.
For evidence expectations, read `references/eval-system-evidence.md`.
For grader expectations, read `references/grader-contract.md`.
For candidate boundaries, read `references/candidate-surface.md`.
For ASI-first framing, read `references/gepa-reflection.md`.
