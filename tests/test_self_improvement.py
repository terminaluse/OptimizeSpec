from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from optimizespec import eval_validation
from optimizespec.self_improvement import (
    EvalCase,
    GEPAEvaluator,
    RolloutResult,
    ScorerSpec,
    ScoreResult,
    TemplateEchoExecutor,
    build_asi,
    compare_candidates,
    evaluate_candidate,
    load_candidate,
    load_eval_cases,
    score_rollout,
)


def test_load_eval_cases_and_candidate(tmp_path: Path) -> None:
    cases_path = tmp_path / "cases.yaml"
    candidate_path = tmp_path / "candidate.yaml"
    cases_path.write_text(
        """
cases:
  - id: upper
    split: train
    input: hello
    expected: hello
    scorer:
      type: exact_match
""",
        encoding="utf-8",
    )
    candidate_path.write_text("answer_template: '{input}'\n", encoding="utf-8")

    cases = load_eval_cases(cases_path)
    candidate = load_candidate(candidate_path)

    assert cases[0].case_id == "upper"
    assert cases[0].split == "train"
    assert candidate == {"answer_template": "{input}"}


def test_direct_eval_persists_summary_and_asi(tmp_path: Path) -> None:
    cases = [
        EvalCase(
            case_id="echo",
            input="hello",
            expected="hello",
            scorer=ScorerSpec(type="exact_match", expected="hello"),
        )
    ]

    summary = evaluate_candidate(
        candidate={"answer_template": "{input}"},
        cases=cases,
        executor=TemplateEchoExecutor(),
        run_dir=tmp_path,
        mutable_fields=["answer_template"],
    )

    assert summary["mean_score"] == 1.0
    side_info = json.loads((tmp_path / "rollouts" / "candidate" / "echo" / "side_info.json").read_text())
    assert side_info["Input"] == "hello"
    assert side_info["Expected"] == "hello"
    assert side_info["Actual"] == "hello"
    assert "answer_template_specific_info" in side_info
    assert side_info["scores"]["correctness"] == 1.0


def test_failed_rollout_becomes_actionable_asi() -> None:
    case = EvalCase(
        case_id="bad-template",
        input="hello",
        expected="hello",
        scorer=ScorerSpec(type="exact_match", expected="hello"),
    )
    rollout = TemplateEchoExecutor().run({"answer_template": "{missing}"}, case, timeout_seconds=1.0)
    score = score_rollout(case, rollout)
    side_info = build_asi(
        case=case,
        candidate={"answer_template": "{missing}"},
        rollout=rollout,
        score=score,
        mutable_fields=["answer_template"],
    )

    assert score.score == 0.0
    assert side_info["Error"]
    assert "answer_template_specific_info" in side_info
    assert "failure" in side_info["answer_template_specific_info"]["Feedback"].lower()


def test_compare_candidates_reports_deltas(tmp_path: Path) -> None:
    cases = [
        EvalCase(
            case_id="echo",
            input="hello",
            expected="hello",
            scorer=ScorerSpec(type="exact_match", expected="hello"),
        )
    ]

    comparison = compare_candidates(
        baseline={"answer_template": "wrong"},
        candidate={"answer_template": "{input}"},
        cases=cases,
        executor=TemplateEchoExecutor(),
        run_dir=tmp_path,
    )

    assert comparison["deltas"][0]["delta"] == 1.0
    assert "answer_template" in comparison["candidate_diff"]
    assert (tmp_path / "comparison.json").exists()


def test_gepa_evaluator_supports_custom_scorers(tmp_path: Path) -> None:
    def contains_expected(case: EvalCase, rollout: RolloutResult) -> ScoreResult:
        actual = str(rollout.actual or "")
        expected = str(case.expected or "")
        score = 1.0 if expected in actual else 0.0
        return ScoreResult(score=score, feedback="custom scorer ran")

    evaluator = GEPAEvaluator(
        executor=TemplateEchoExecutor(),
        run_dir=tmp_path,
        custom_scorers={"contains_expected": contains_expected},
    )
    case = EvalCase(
        case_id="custom",
        input="hello",
        expected="hello",
        scorer=ScorerSpec(type="custom", expected="contains_expected"),
    )

    score, side_info = evaluator({"answer_template": "{input}"}, example=case)

    assert score == 1.0
    assert side_info["Feedback"] == "custom scorer ran"


def test_package_guidance_reference_fixture_scores_required_terms(tmp_path: Path) -> None:
    fixture = eval_validation.load_fixture("optimizespec-package-guidance")
    cases = [
        case
        for case in eval_validation.default_eval_cases(fixture, include_system_loop=False)
        if case.metadata.get("artifact_type") == "proposal"
    ]

    payload = evaluate_candidate(
        candidate=eval_validation.default_seed_candidate(fixture),
        cases=cases,
        executor=eval_validation.EvalValidationExecutor(fixture=fixture, run_dir=tmp_path),
        run_dir=tmp_path,
        mutable_fields=eval_validation.MUTABLE_FIELDS,
        custom_scorers=eval_validation.custom_scorers(),
    )

    assert payload["mean_score"] == 1.0
    side_info = json.loads(
        (tmp_path / "rollouts" / "candidate" / "optimizespec-package-guidance-proposal" / "side_info.json").read_text()
    )
    assert "proposal_generation_guidance_specific_info" in side_info
    assert side_info["scores"]["semantic_concept_coverage"] == 1.0


def test_reference_agent_generated_artifacts_score_cleanly(tmp_path: Path) -> None:
    fixture = eval_validation.load_fixture("optimizespec-managed-agent")
    cases = [
        case
        for case in eval_validation.default_eval_cases(fixture, include_system_loop=False)
        if case.metadata.get("artifact_type") in {"design", "apply_plan"}
    ]

    payload = evaluate_candidate(
        candidate=eval_validation.default_seed_candidate(fixture),
        cases=cases,
        executor=eval_validation.EvalValidationExecutor(fixture=fixture, run_dir=tmp_path),
        run_dir=tmp_path,
        mutable_fields=eval_validation.MUTABLE_FIELDS,
        custom_scorers=eval_validation.custom_scorers(),
    )

    assert payload["mean_score"] == 1.0
    assert payload["mean_val_score"] == 1.0
    side_info = json.loads((tmp_path / "rollouts" / "candidate" / "optimizespec-managed-agent-design" / "side_info.json").read_text())
    assert "design_generation_guidance_specific_info" in side_info
    assert side_info["scores"]["semantic_concept_coverage"] == 1.0


def test_reference_agent_generation_writes_temp_artifacts(tmp_path: Path) -> None:
    fixture = eval_validation.load_fixture("optimizespec-managed-agent")

    rendered = eval_validation.generate_artifacts(
        fixture,
        tmp_path,
        eval_validation.default_seed_candidate(fixture),
    )

    assert "proposal.md" in rendered
    assert (tmp_path / "generated" / "proposal.md").exists()
    assert (tmp_path / "generated" / "design.md").exists()
    assert (tmp_path / "generated" / "specs" / "eval-validation-spec.md").exists()


@pytest.mark.parametrize(
    "skill_name",
    [
        "optimizespec-common",
        "optimizespec-new",
        "optimizespec-continue",
        "optimizespec-apply",
        "optimizespec-verify",
    ],
)
def test_gepa_eval_skill_frontmatter(skill_name: str) -> None:
    skill_path = Path("skills") / skill_name / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    metadata = yaml.safe_load(text.split("---", 2)[1])
    assert metadata["name"] == skill_name
    assert isinstance(metadata["description"], str)
    assert metadata["description"].strip()


def test_common_skill_reference_paths_exist() -> None:
    base = Path("skills") / "optimizespec-common"
    required = [
        "references/workflow.md",
        "references/reference-contracts.md",
        "references/gepa-reflection.md",
        "references/managed-agents-runner.md",
        "references/scorers-and-asi.md",
        "references/repo-patterns.md",
        "references/eval-system-evidence.md",
        "references/runner-contract.md",
        "references/grader-contract.md",
        "references/asi-contract.md",
        "references/candidate-surface.md",
        "references/optimizer-contract.md",
        "references/managed-agents-runtime-contract.md",
        "references/verification-contract.md",
        "assets/templates/proposal.md",
        "assets/templates/design.md",
        "assets/templates/eval-cases.yaml",
        "assets/templates/seed-candidate.yaml",
        "assets/python_runner/agent_self_improve.py",
    ]

    for relative in required:
        assert (base / relative).exists(), relative
