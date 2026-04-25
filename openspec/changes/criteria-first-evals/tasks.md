## 1. Skill Guidance

- [ ] 1.1 Update `skills/gepa-evals-new/SKILL.md` so new changes must start with criteria-first eval thinking before examples and scoring.
- [ ] 1.2 Update `skills/gepa-evals-common/assets/templates/proposal.md` with success criteria, thresholds, guardrails, non-goals, blind spots, and criteria unknowns.
- [ ] 1.3 Update `skills/gepa-evals-common/assets/templates/design.md` with eval design, grading strategy, and optimizer acceptance sections.
- [ ] 1.4 Update `skills/gepa-evals-common/assets/templates/eval-cases.yaml` to show optional criteria, grader trust, and acceptance metadata.
- [ ] 1.5 Add or update reference docs explaining system evals, agent quality evals, optimizer acceptance criteria, and grader trust.

## 2. Validation Scoring

- [ ] 2.1 Update proposal artifact scoring to check primary criterion, secondary criteria, guardrails, thresholds, non-goals, and blind spots.
- [ ] 2.2 Update design artifact scoring to check task distribution, edge cases, split strategy, failure modes, and what the eval does not measure.
- [ ] 2.3 Update scorer/eval-case validation to check grader type, grader rationale, calibration evidence, reliability risks, and human review triggers when present.
- [ ] 2.4 Update optimizer validation to check optimized metric, diagnostic metrics, guardrail metrics, promotion rule, regression tolerance, and required evidence.
- [ ] 2.5 Add validation feedback that clearly distinguishes missing system-loop details from missing agent-quality criteria.

## 3. Fixtures and Negative Cases

- [ ] 3.1 Update positive fixtures so expected generated artifacts include criteria-first sections.
- [ ] 3.2 Add or update a negative fixture for vague "make it better" requests that lack success criteria.
- [ ] 3.3 Add or update a negative fixture for evals with examples but no real task distribution or edge cases.
- [ ] 3.4 Add or update a negative fixture for LLM grading without rubric, constrained output, or calibration.
- [ ] 3.5 Add or update a negative fixture for optimization plans that improve one metric without guardrail or promotion rules.

## 4. Documentation

- [ ] 4.1 Update `TECHNICAL.md` with criteria-first eval workflow details and the distinction between system evals, agent quality evals, and optimizer acceptance.
- [ ] 4.2 Update `README.md` only if needed to briefly state that good eval criteria come before optimization.
- [ ] 4.3 Include Anthropic's eval guidance as source motivation in reference docs without copying vendor text.

## 5. Verification

- [ ] 5.1 Add tests for updated proposal and design templates.
- [ ] 5.2 Add tests that artifact quality scoring penalizes missing criteria, task distribution, grader trust, and optimizer acceptance details.
- [ ] 5.3 Add tests that legacy simple eval cases still load when criteria metadata is absent.
- [ ] 5.4 Run the deterministic test suite.
- [ ] 5.5 Run a local eval validation smoke that does not require live Anthropic credentials.
