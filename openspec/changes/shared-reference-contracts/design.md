## Context

The OptimizeSpec skills now need to do more than draft eval examples. They need to guide a coding agent through building a self-improvement system for an existing Claude Managed Agent, including runner invocation, rollouts, scoring, qualitative judgment, actionable side information, optimizer loops, candidate promotion, and verification.

Those expectations cut across multiple phases. If each phase embeds its own prose, the system will drift and the instructions will become too heavy. A reference-contract layer gives us a stable source of truth while preserving a light UX: the user sees a simple flow, and the agent loads the deeper contracts only when relevant.

Constraints:

- Keep skills readable and short enough to use directly.
- Keep contracts markdown-first so they are easy to review and evolve.
- Do not introduce a complex schema system until runtime code consumes one.
- Avoid tests that merely assert exact wording in markdown files.
- Keep Claude Managed Agents as the only supported runtime for now.
- Preserve the distinction between system-loop evidence and agent-quality evidence.

## Goals / Non-Goals

**Goals:**

- Make evidence persistence a first-class requirement for every eval and optimization run.
- Give skills a reusable contract library for shared concepts such as runners, graders, ASI, candidates, optimizer lineage, runtime invocation, and verification.
- Keep phase skills focused on what the user or coding agent needs to do at that phase.
- Make generated eval designs auditable: a reviewer can find the run manifest, candidate history, per-case scores, judge output, side information, rollout traces, comparison, and promotion decision.
- Validate behavior and artifact structure rather than exact markdown prose.

**Non-Goals:**

- Build a hosted experiment tracking service.
- Replace GEPA's optimizer APIs.
- Add support for non-Claude runtimes in this change.
- Require live Anthropic calls for deterministic validation.
- Turn markdown reference docs into a full typed schema registry immediately.

## Decisions

### Add markdown contracts under the shared skill references directory

Reference contracts should live in `skills/optimizespec-common/references/` because every phase skill can load that directory and because these expectations belong to the skill system rather than only the runtime package.

Initial contracts:

- `criteria-first-evals.md`: existing criteria-first eval-design guidance.
- `eval-system-evidence.md`: required evidence ledger and artifacts for eval and optimization runs.
- `runner-contract.md`: how direct eval, compare, and optimize commands are invoked and what they produce.
- `grader-contract.md`: how numeric scores, qualitative judgments, calibration, and grader reliability are represented.
- `asi-contract.md`: how actionable side information is captured and used.
- `candidate-surface.md`: what the optimizer is allowed to mutate and how candidate versions are identified.
- `optimizer-contract.md`: objective metrics, diagnostics, guardrails, selection, lineage, and promotion.
- `managed-agents-runtime-contract.md`: Claude Managed Agents invocation details and beta SDK/header requirements.
- `verification-contract.md`: deterministic and live checks required before a generated eval system is considered ready.

Rationale: This gives the skills named references to cite without making every skill a long implementation manual.

Alternative considered: keep all details in `TECHNICAL.md`. That helps humans, but skills need smaller phase-relevant contracts that can be loaded selectively.

### Make the evidence ledger the highest-priority contract

The evidence contract should require a run ledger that can answer:

- Which run happened?
- Which candidate version was evaluated?
- Which eval cases ran?
- What score did each case produce?
- What qualitative judge output was produced?
- What ASI was captured?
- What rollout artifacts or transcripts support the score?
- What comparison or optimizer decision was made?
- Which candidate, if any, was promoted and why?

A recommended layout can be markdown-documented without becoming mandatory runtime schema too early:

```text
runs/<run-id>/
  manifest.json
  candidates/<candidate-id>.json
  evaluations/<candidate-id>/summary.json
  evaluations/<candidate-id>/cases/<case-id>/score.json
  evaluations/<candidate-id>/cases/<case-id>/judge.json
  evaluations/<candidate-id>/cases/<case-id>/side_info.json
  evaluations/<candidate-id>/cases/<case-id>/rollout.json
  comparisons/<comparison-id>.json
  optimizer/lineage.json
  optimizer/leaderboard.json
  optimizer/events.jsonl
  promotion.json
```

Rationale: GEPA improvement claims are not trustworthy if users cannot inspect the evidence behind each candidate and score.

Alternative considered: store only aggregate compare output. That is too thin for debugging, grader trust, or optimizer auditability.

### Keep phase skills small and reference-driven

The phase skills should load references progressively:

- New/proposal work loads criteria-first, candidate surface, grader, and evidence contracts enough to draft the eval contract.
- Continue/design work loads runner, optimizer, runtime, grader, ASI, and evidence contracts to specify how the system will run.
- Apply work loads runner, evidence, grader, ASI, optimizer, runtime, and verification contracts to implement the system.
- Verify work loads evidence, grader, ASI, optimizer, and verification contracts to inspect outputs and decide readiness.

Rationale: This keeps the user-facing flow light while giving the agent the right level of detail when implementation starts.

Alternative considered: put every contract in the common skill and tell all phase skills to read it. That wastes context and makes skills harder to follow.

### Validate structure and behavior instead of exact prose

Validation should avoid brittle tests that assert exact text in markdown files. It should instead check that generated artifacts and runnable systems demonstrate the expected concepts:

- Proposal/design artifacts identify required evidence and runner decisions.
- Eval designs name candidate versions, run outputs, scoring records, judge records, ASI records, and promotion evidence.
- Fixture-based validation penalizes missing evidence ledger, missing judge persistence, missing optimizer lineage, or missing verification plan.
- Runtime tests, where available, inspect actual emitted files or structured summaries.

Rationale: Exact wording tests make the repo annoying to change and do not prove the skill creates better eval systems.

Alternative considered: simple substring checks. They are cheap, but the user has explicitly rejected that style because it encourages shallow tests.

## Contract Responsibilities

The contracts should divide responsibility clearly:

- `eval-system-evidence.md` defines what must be persisted for auditability.
- `runner-contract.md` defines command surfaces and rollout lifecycle.
- `grader-contract.md` defines numeric and qualitative scoring, calibration, and grader-risk handling.
- `asi-contract.md` defines how reflective feedback becomes optimizer input.
- `candidate-surface.md` defines mutable files, identifiers, diffs, and rollback expectations.
- `optimizer-contract.md` defines objective metrics, guardrails, selection, and promotion.
- `managed-agents-runtime-contract.md` defines Claude Managed Agents SDK/header setup and invocation assumptions.
- `verification-contract.md` defines readiness checks and failure reporting.

The common skill should include a short reference index that explains when to load each document. Phase skills should cite that index instead of duplicating long descriptions.

## Validation Strategy

The implementation should add deterministic validation around:

- Reference contracts exist and are discoverable through the common skill reference index.
- Phase skills instruct agents to load the relevant contracts for their phase.
- Proposal and design templates include a place to specify the evidence model and contract references.
- Artifact-quality scoring detects missing evidence ledger, runner invocation, judge output persistence, ASI persistence, optimizer lineage, and promotion decision.
- Negative fixtures fail or score lower when an eval design only reports aggregate scores and omits per-case evidence.
- Tests avoid exact markdown prose assertions; they inspect structured fixture outputs, parsed sections, or validator behavior.

Live Managed Agent validation remains opt-in because deterministic local validation should be enough to check the contract layer.

## Risks / Trade-offs

- [Risk] Too many reference docs make the skill system feel fragmented. -> Mitigation: keep docs short, add a common reference index, and load only phase-relevant docs.
- [Risk] Contracts drift from runtime behavior. -> Mitigation: validation should inspect generated artifact structure and emitted run evidence, not just docs.
- [Risk] Markdown contracts are less enforceable than typed schemas. -> Mitigation: start markdown-first for skill clarity, then extract typed schemas only when runtime code needs them.
- [Risk] The evidence ledger can feel heavy for simple smoke evals. -> Mitigation: allow minimal records for smoke runs, but still persist run id, candidate id, aggregate score, case results, and promotion decision.
- [Risk] Claude Managed Agents runtime details change while the feature is in preview. -> Mitigation: isolate those details in `managed-agents-runtime-contract.md` so one document can be updated.

## Migration Plan

1. Add the reference-contract markdown documents and common reference index.
2. Update phase skill instructions to cite and load the relevant contracts.
3. Update proposal and design templates with evidence-model and contract-reference sections.
4. Update validation scoring to detect missing evidence, runner, grader, ASI, optimizer, and verification details through artifact behavior.
5. Add or update fixtures that exercise missing evidence ledger, aggregate-only scoring, missing judge output, missing optimizer lineage, and missing promotion evidence.
6. Run deterministic tests and OpenSpec validation.
