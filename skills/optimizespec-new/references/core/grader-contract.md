# Grader Contract

Graders convert rollout evidence into numeric scores and qualitative judgment that GEPA can optimize. A weak or uncalibrated grader can produce false improvement, so every grader plan must document type, trust basis, calibration, reliability risks, and human review triggers.

## Numeric Scores

- Scores must have a known range and direction. Prefer `0.0` to `1.0`, higher-is-better.
- The optimized metric must be named separately from diagnostic and guardrail metrics.
- Latency, cost, and error rates must be inverted before they are used as higher-is-better metrics.
- Abstentions and scorer failures must be recorded instead of converted into unexplained zeros.

## Qualitative Judge Output

When an LLM, human, or hybrid judge is used, persist structured judge output with:

- grader type
- rubric or criterion version
- constrained score output
- rationale summary
- calibration status or examples
- reliability warnings
- human review trigger

## Grader Types

- Deterministic: exact match, schema validation, file existence, command status, or programmatic checks.
- Code: repo-owned scoring function that can inspect artifacts or outputs.
- LLM: rubric-driven judgment with constrained output and calibration examples.
- Human: manual review captured as structured evidence.
- Hybrid: deterministic checks plus LLM or human judgment.

## Promotion Guardrails

Promotion requires more than a better optimized metric. Guardrails can block promotion when evidence is missing, regressions exceed tolerance, reliability risks are unresolved, or manual review is required.
