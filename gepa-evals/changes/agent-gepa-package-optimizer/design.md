## Context

This change applies the GEPA eval skills to this package itself. The repo already provides `agent_gepa.self_improvement`, which includes eval case loading, deterministic scorers, ASI construction, rollout persistence, direct eval, compare, and GEPA optimize wiring.

The target is a package-guidance candidate: a `dict[str, str]` containing text fields a coding or Managed Agent can use to explain and operate this package. The local executor is deterministic and credential-free so direct eval and compare can run in CI. GEPA optimization still requires a reflection model and provider credentials.

## Runner Invocation

The new folder exposes:

```bash
python gepa-evals/changes/agent-gepa-package-optimizer/package_optimizer.py show-candidate
python gepa-evals/changes/agent-gepa-package-optimizer/package_optimizer.py eval --run-dir runs/package-optimizer/eval
python gepa-evals/changes/agent-gepa-package-optimizer/package_optimizer.py compare --candidate gepa-evals/changes/agent-gepa-package-optimizer/seed-candidate.yaml --run-dir runs/package-optimizer/compare
python gepa-evals/changes/agent-gepa-package-optimizer/package_optimizer.py optimize --max-metric-calls 12 --run-dir runs/package-optimizer/optimize
```

## Candidate Surface

- `package_summary`: Included for package purpose questions.
- `eval_workflow`: Included for command and operator workflow questions.
- `rollout_lifecycle`: Included for rollout and runtime questions.
- `asi_guidance`: Included for ASI and reflection questions.
- `verification_guidance`: Included for testing and validation questions.
- `v1_limitations`: Included for limitation, credential, and runtime scope questions.

## Rollout Lifecycle

1. Load `eval-cases.yaml` and candidate YAML.
2. Select candidate fields relevant to the eval input.
3. Compose a package-guidance answer.
4. Score the answer using required-term coverage.
5. Build ASI with missing terms, score, trajectory, and field-specific feedback.
6. Persist rollout artifacts under the requested run directory.

## Trace Capture

The local fixture captures selected fields, input text, output text, required terms, generated answer, simple usage estimates, and deterministic runtime IDs. A live Managed Agent replacement should additionally capture Agent ID/version, Environment ID, Session ID, event types, tool summaries, generated files, API usage, errors, and cleanup status.

## Scoring and ASI

The scorer computes required-term coverage. ASI includes required terms and missing terms in `Feedback`, plus field-specific diagnostics for every mutable package-guidance field.

## GEPA Configuration

The optimizer uses:

- seed candidate: `seed-candidate.yaml`
- train and validation examples: `eval-cases.yaml`
- evaluator: package-guidance executor plus required-term scorer
- objective: improve package guidance so required concepts are present and accurate
- background: describe this package, candidate fields, and ASI contract
- reflection selector: round-robin by default
- run dir and metric-call budget from CLI args

## Risks and Blockers

- Local fixture evals optimize package guidance, not live code-editing behavior.
- Live Managed Agent rollouts require replacing the fixture executor with real session execution.
- GEPA optimization requires a configured reflection model and credentials.
