## Why

`optimizespec` is starting to encode serious eval-design judgment in its skills, but several important system expectations still live in scattered prose across skill instructions, templates, technical docs, and validation code. That makes the workflow harder to maintain and easier for skills to drift: a new skill may ask for criteria, but forget evidence persistence; an apply skill may implement a runner, but fail to record judge output, candidate lineage, or optimizer decisions in a durable way.

The most urgent gap is evidence. Users should be able to inspect every optimization run and answer: which candidate was tested, which eval cases ran, what each score was, what the judge said, what actionable side information was produced, why the optimizer chose the next candidate, and why a candidate was or was not promoted. Today that expectation is not captured as a first-class contract that every skill can reuse.

We should move these cross-cutting expectations into markdown reference contracts under the shared skills directory. The skills can stay lightweight and phase-specific, while the durable requirements for evidence, runners, graders, ASI, candidates, optimizer behavior, runtime invocation, and verification live in one place.

## What Changes

- Add a shared reference-contract library under `skills/optimizespec-common/references/`.
- Add `eval-system-evidence.md` as the primary contract for recording run manifests, candidate versions, per-case scores, judge outputs, ASI, rollout artifacts, optimizer lineage, comparison results, and promotion decisions.
- Add runner, grader, ASI, candidate surface, optimizer, runtime, and verification reference contracts so skills share the same implementation expectations.
- Update phase skills to load only the reference contracts needed for that phase instead of duplicating long requirements in each `SKILL.md`.
- Update templates so proposal and design artifacts explicitly call out the evidence model and the contract documents that apply to the eval system.
- Update validation so generated artifacts are evaluated against the evidence and runner contracts through artifact structure and behavior, not brittle assertions against exact markdown prose.

## Capabilities

### New Capabilities

- `reference-contract-library`: A shared library of markdown contracts for cross-skill OptimizeSpec system expectations.
- `eval-system-evidence-contract`: A required evidence model for optimization runs, candidate lineage, scores, judge outputs, ASI, rollouts, comparisons, and promotion decisions.
- `skill-contract-integration`: Skill instructions and templates that progressively load the relevant contracts for proposal, design, apply, and verify work.

### Modified Capabilities

- `criteria-first-eval-workflow`: Criteria-first eval design should reference the grader, evidence, and verification contracts rather than restating every detail inline.
- `self-improvement-apply-workflow`: Apply work should implement the evidence ledger, runner contract, optimizer contract, and runtime contract before claiming the system is ready.
- `artifact-quality-scoring`: Validation should score whether artifacts define enough evidence, runner, grader, and optimizer detail to make eval results auditable.

## Impact

This change affects repo-local skills, reference docs, templates, validation, and documentation:

- `skills/optimizespec-common/references/*.md`
- `skills/optimizespec-common/SKILL.md`
- `skills/optimizespec-new/SKILL.md`
- Future apply, continue, and verify skill files if present in this repo
- `skills/optimizespec-common/assets/templates/proposal.md`
- `skills/optimizespec-common/assets/templates/design.md`
- `src/optimizespec/eval_validation.py`
- `tests/*`
- `TECHNICAL.md`

The change should not add a new user-facing phase. The user should still experience a concise proposal and design flow. The difference is that the agent has stronger reusable contracts behind the scenes, so it remembers to specify where evidence is persisted, how rollouts are invoked, how judge output is stored, and how optimizer decisions can be audited.

The first implementation priority should be the evidence contract, runner contract, and grader contract. The remaining contracts can be smaller documents initially, but they should still make the expected system behavior explicit enough for skills to reference them.
