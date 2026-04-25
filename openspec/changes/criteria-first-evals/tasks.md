## 1. Skill Guidance

- [x] 1.1 Update `skills/gepa-evals-new/SKILL.md` so new changes must start with criteria-first eval thinking before examples and scoring.
- [x] 1.2 Update `skills/gepa-evals-common/assets/templates/proposal.md` with success criteria, thresholds, guardrails, non-goals, blind spots, and criteria unknowns.
- [x] 1.3 Update `skills/gepa-evals-common/assets/templates/design.md` with eval design, grading strategy, and optimizer acceptance sections.
- [x] 1.4 Update `skills/gepa-evals-common/assets/templates/eval-cases.yaml` to show optional criteria, grader trust, and acceptance metadata.
- [x] 1.5 Add or update reference docs explaining system evals, agent quality evals, optimizer acceptance criteria, and grader trust.
- [x] 1.6 Update `gepa-evals-new` guidance so the skill asks at most 3-5 plain-language questions before drafting, then asks the user to confirm or correct the inferred eval contract.
- [x] 1.7 Update `gepa-evals-new` guidance so first proposals stay concise and defer implementation depth to design.

## 2. Validation Scoring

- [x] 2.1 Update proposal artifact scoring to check primary criterion, secondary criteria, guardrails, thresholds, non-goals, and blind spots.
- [x] 2.2 Update design artifact scoring to check task distribution, edge cases, split strategy, failure modes, and what the eval does not measure.
- [x] 2.3 Update scorer/eval-case validation to check grader type, grader rationale, calibration evidence, reliability risks, and human review triggers when present.
- [x] 2.4 Update optimizer validation to check optimized metric, diagnostic metrics, guardrail metrics, promotion rule, regression tolerance, and required evidence.
- [x] 2.5 Add validation feedback that clearly distinguishes missing system-loop details from missing agent-quality criteria.
- [x] 2.6 Add validation feedback that penalizes exhaustive-questionnaire behavior when a useful draft proposal could be produced from partial user input.
- [x] 2.7 Add validation feedback that discourages first proposals from becoming full technical designs.

## 3. Fixtures and Negative Cases

- [x] 3.1 Update positive fixtures so expected generated artifacts include criteria-first sections.
- [x] 3.2 Add or update a negative fixture for vague "make it better" requests that lack success criteria.
- [x] 3.3 Add or update a negative fixture for evals with examples but no real task distribution or edge cases.
- [x] 3.4 Add or update a negative fixture for LLM grading without rubric, constrained output, or calibration.
- [x] 3.5 Add or update a negative fixture for optimization plans that improve one metric without guardrail or promotion rules.
- [x] 3.6 Add or update a fixture where the user provides partial intent and examples, and the expected behavior is to draft criteria plus focused open questions.

## 4. Documentation

- [x] 4.1 Update `TECHNICAL.md` with criteria-first eval workflow details and the distinction between system evals, agent quality evals, and optimizer acceptance.
- [x] 4.2 Update `README.md` only if needed to briefly state that good eval criteria come before optimization.
- [x] 4.3 Include Anthropic's eval guidance as source motivation in reference docs without copying vendor text.
- [x] 4.4 Document the lightweight UX rule: the user gives intent and examples, the agent drafts criteria, and the user confirms or corrects.

## 5. Verification

- [x] 5.1 Add tests for updated proposal and design templates.
- [x] 5.2 Add tests that artifact quality scoring penalizes missing criteria, task distribution, grader trust, and optimizer acceptance details.
- [x] 5.3 Add tests that legacy simple eval cases still load when criteria metadata is absent.
- [x] 5.4 Add tests or fixture checks that partial user input leads to a draft eval contract rather than a long blocking questionnaire.
- [x] 5.5 Add tests or fixture checks that first proposal guidance stays concise.
- [x] 5.6 Run the deterministic test suite.
- [x] 5.7 Run a local eval validation smoke that does not require live Anthropic credentials.
