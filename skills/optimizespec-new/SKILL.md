---
name: optimizespec-new
description: Start a repo-local OptimizeSpec self-improvement change. Use when the user wants to create evals, optimize an agent with GEPA, define an agent self-improvement loop, or begin an ASI-first evaluation workflow.
---

# OptimizeSpec New

Create the first artifact for an OptimizeSpec self-improvement change. The default workflow directory is:

```text
optimizespec/changes/<change-name>/
```

## Workflow

1. Derive or confirm a kebab-case change name.
2. Read `references/core/reference-contracts.md`, then load only the proposal-phase core references it names: criteria-first, candidate surface, grader, evidence, and live eval runner. Load runtime-specific references only when repo evidence identifies the target runtime.
3. Create `optimizespec/changes/<change-name>/proposal.md`.
4. Use `assets/templates/proposal.md` as the structure.
5. Inspect the repository enough to identify the target agent's likely runtime, code location, dependency boundary, import/package setup, existing eval/test folders, tool wiring, environment needs, and command conventions.
6. Keep all OptimizeSpec artifacts under the repo-root `optimizespec/changes/<change-name>/` tree. In the proposal, record where the durable optimization-system code should be created or which existing folder should be reused, and how code in that location will import or invoke the real agent modules.
7. Capture known details without inventing missing information.
8. Start from plain-language user intent and examples, then draft the eval design for review.
9. If the user has not provided enough information after repo inspection, ask at most 3-5 focused questions before drafting. Prefer questions like:
   - What agent should improve?
   - Where does that agent live in this repo?
   - Should the optimization code reuse an existing eval/test folder or create a new one?
   - What behavior should get better?
   - What are 2-3 representative tasks?
   - What would make an answer clearly bad?
   - Which concerns matter most: correctness, formatting, safety, cost, speed, or tool use?
10. Draft the inferred runtime, runtime evidence and confidence, success criteria, scoring plan, grader strategy, evidence model, optimizer acceptance rules, and optimization-system location decision from the user's input and repo inspection. For Claude Managed Agents, define live rollouts as the eval primitive: candidate, eval case, real Session execution, final report/output, trace evidence, grader, ASI, and live-score optimization.
11. Ask the user to confirm or correct the inferred eval contract and optimization-system location in the proposal so they can review primary metrics, diagnostics, guardrails, task distribution, grading, evidence persistence, promotion rules, and file layout from a concrete draft.
12. If the agent, inferred runtime, criteria, scorer, examples, grader trust, evidence model, optimizer acceptance, optimization-system path, or import/runtime access plan are incomplete, record explicit unknowns and candidate discovery questions. Ask about runtime only when repo evidence remains ambiguous and the answer affects the artifacts.
13. Keep `proposal.md` concise. Prefer short bullets and no more than 2-3 eval examples. Defer deeper runner mechanics, calibration details, ledger file layout, and implementation design to `design.md` unless they are required to confirm the eval contract or optimization-system location.
14. Stop after creating `proposal.md`.

## Required Proposal Content

- Agent and inferred runtime context, including evidence, confidence, and unknowns.
- Optimization-system location decision: create or reuse, path, rationale, import/runtime access plan, existing agent code to reuse, existing tools/skills/MCP/env/permissions to reuse, and run-output path.
- Behavior to improve.
- Candidate fields GEPA may mutate, if known.
- Success criteria: user outcome, primary criterion, secondary criteria, guardrails, thresholds, non-goals, and blind spots.
- Draft eval contract for user confirmation or correction.
- Input examples and expected outputs or output shapes.
- Numeric scoring intent, preferably `0.0` to `1.0`.
- Qualitative rubric.
- Grading strategy: deterministic, code-based, LLM-based, human, or hybrid, plus why the grader can be trusted.
- Optimizer acceptance: optimized live metric, diagnostic metrics, guardrails, selection rule, regression tolerance, and required evidence. Promotion or release decisions can be recorded separately, but they are not the Managed Agents core loop.
- Evidence model: run manifest, candidate versions, rollout records, scoring records, judge records, ASI records, optimizer lineage, best-candidate evidence, and any optional promotion evidence at a high level.
- Contract references that should guide design and apply work.
- ASI fields needed for reflection.
- Unknowns to resolve in design.

For workflow motivation, read `references/core/workflow.md`.
For criteria-first eval design, read `references/core/criteria-first-evals.md`.
For evidence expectations, read `references/core/eval-system-evidence.md`.
For grader expectations, read `references/core/grader-contract.md`.
For candidate boundaries, read `references/core/candidate-surface.md`.
For ASI-first framing, read `references/core/gepa-reflection.md`.
Name `references/core/live-eval-runner-contract.md` as the contract source of truth for live optimization. When the proposal identifies Claude Managed Agents as the likely runtime, also name `references/runtimes/claude-managed-agent/python-managed-agent-package/` as the concrete live Python runner implementation reference for later design and apply work. For other runtimes, record the missing runtime-specific reference coverage and the production adapter assumptions. The primary optimizer objective should be live rollout scoring.
