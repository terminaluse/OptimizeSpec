from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from optimizespec import eval_validation
from optimizespec.self_improvement import EvalCase, RolloutResult, ScorerSpec


def test_fixture_metadata_contract_loads_positive_fixture() -> None:
    fixture = eval_validation.load_fixture("optimizespec-managed-agent")

    assert fixture.runtime == "Claude Managed Agents"
    assert fixture.is_positive
    assert "direct_eval" in fixture.existing_commands
    assert "proposal" in eval_validation.semantic_checks(fixture)


def test_fixture_metadata_contract_rejects_missing_required_fields() -> None:
    with pytest.raises(eval_validation.ContractValidationError, match="description"):
        eval_validation.validate_fixture_metadata(
            {
                "id": "bad",
                "name": "bad",
                "runtime": "Claude Managed Agents",
                "source_files": {"runtime": "runtime.py"},
                "existing_commands": {"direct_eval": "eval", "optimize": "opt", "compare": "cmp", "show_candidate": "show"},
                "candidate_fields": ["system_prompt"],
                "expected_behavior": {},
            }
        )


def test_eval_case_contract_rejects_unknown_custom_scorer(tmp_path: Path) -> None:
    cases = tmp_path / "cases.yaml"
    cases.write_text(
        """
cases:
  - id: bad-custom
    split: train
    input: hello
    expected: world
    scorer:
      type: custom
      expected: does_not_exist
""",
        encoding="utf-8",
    )

    with pytest.raises(eval_validation.ContractValidationError, match="unknown custom scorer"):
        eval_validation.load_eval_cases_strict(cases, eval_validation.custom_scorers())


def test_semantic_prose_scoring_allows_different_wording() -> None:
    case = EvalCase(
        case_id="proposal",
        input="score proposal",
        expected="target agent, eval objective, numeric scoring",
        scorer=ScorerSpec(type="custom", expected="semantic_required_concepts"),
        metadata={"required_terms": ["target agent", "eval objective", "numeric scoring"]},
    )
    rollout = RolloutResult(
        case_id="proposal",
        actual="This artifact names the target agent, explains the eval objective, and defines numeric scoring.",
    )

    score = eval_validation.semantic_required_concepts_scorer(case, rollout)

    assert score.score == 1.0


def test_semantic_prose_scoring_catches_critical_omission() -> None:
    case = EvalCase(
        case_id="design",
        input="score design",
        expected="direct eval, GEPA",
        scorer=ScorerSpec(type="custom", expected="semantic_required_concepts"),
        metadata={"required_terms": ["direct eval", "GEPA"]},
    )
    rollout = RolloutResult(case_id="design", actual="This only mentions direct eval.")

    score = eval_validation.semantic_required_concepts_scorer(case, rollout)

    assert score.score == 0.5
    assert score.subscores["missing_concepts"] == 1.0


def test_legacy_eval_cases_still_load_without_criteria_metadata(tmp_path: Path) -> None:
    cases = tmp_path / "legacy.yaml"
    cases.write_text(
        """
cases:
  - id: legacy
    split: train
    input: hello
    expected: hello
    scorer:
      type: exact_match
      expected: hello
""",
        encoding="utf-8",
    )

    loaded = eval_validation.load_eval_cases_strict(cases, eval_validation.custom_scorers())

    assert loaded[0].case_id == "legacy"
    assert loaded[0].metadata == {}


def test_eval_case_top_level_criteria_metadata_is_preserved(tmp_path: Path) -> None:
    cases = tmp_path / "criteria.yaml"
    cases.write_text(
        """
cases:
  - id: criteria-case
    split: train
    input: hello
    expected: hello
    scorer:
      type: exact_match
      expected: hello
    criteria:
      category: agent-quality
      primary: exact output
      secondary:
        - no extra text
      guardrails:
        - no unrelated output
    grader:
      type: deterministic
      rationale: exact match is reliable
      calibration: []
      reliability_risks: []
      human_review_triggers: []
    acceptance:
      optimized_metric: correctness
      diagnostic_metrics: []
      guardrail_metrics: []
      promotion_rule: promote on correctness
""",
        encoding="utf-8",
    )

    loaded = eval_validation.load_eval_cases_strict(cases, eval_validation.custom_scorers())

    assert loaded[0].metadata["criteria"]["category"] == "agent-quality"
    assert loaded[0].metadata["grader"]["type"] == "deterministic"
    assert loaded[0].metadata["acceptance"]["optimized_metric"] == "correctness"


def test_eval_case_metadata_rejects_uncalibrated_grader_shape(tmp_path: Path) -> None:
    cases = tmp_path / "bad-grader.yaml"
    cases.write_text(
        """
cases:
  - id: bad-grader
    split: train
    input: hello
    expected: hello
    scorer:
      type: exact_match
      expected: hello
    metadata:
      grader:
        type: llm
        calibration: missing-list
""",
        encoding="utf-8",
    )

    with pytest.raises(eval_validation.ContractValidationError, match="calibration"):
        eval_validation.load_eval_cases_strict(cases, eval_validation.custom_scorers())


def test_artifact_quality_scoring_penalizes_missing_criteria_terms() -> None:
    fixture = eval_validation.load_fixture("optimizespec-managed-agent")
    case = next(case for case in eval_validation.default_eval_cases(fixture) if case.metadata.get("artifact_type") == "proposal")
    rollout = RolloutResult(
        case_id=case.case_id,
        actual="Target agent and eval objective are present, with numeric scoring and qualitative rubric.",
    )

    score = eval_validation.semantic_required_concepts_scorer(case, rollout)

    assert score.score < 0.5
    assert score.subscores["missing_concepts"] > 0.0


def test_lightweight_user_flow_penalizes_long_questionnaire() -> None:
    fixture = eval_validation.load_fixture("optimizespec-managed-agent")
    case = next(case for case in eval_validation.default_eval_cases(fixture) if case.metadata.get("artifact_type") == "proposal")
    rollout = RolloutResult(
        case_id=case.case_id,
        actual=(
            "target agent Claude Managed Agents eval objective input expected output numeric scoring qualitative rubric ASI "
            "primary criterion secondary criteria guardrails thresholds non-goals blind spots "
            "evidence model candidate versions scoring records judge records ASI records promotion evidence contract references "
            "draft eval contract confirm or correct focused open questions "
            "What is metric one? What is metric two? What is metric three? "
            "What is metric four? What is metric five? What is metric six?"
        ),
    )

    score = eval_validation.semantic_required_concepts_scorer(case, rollout)

    assert score.subscores["semantic_concept_coverage"] == 1.0
    assert score.subscores["lightweight_user_flow"] == 0.0
    assert score.score < 1.0


def test_design_evidence_contract_penalizes_aggregate_only_design() -> None:
    fixture = eval_validation.load_fixture("optimizespec-managed-agent")
    case = next(case for case in eval_validation.default_eval_cases(fixture) if case.metadata.get("artifact_type") == "design")
    rollout = RolloutResult(
        case_id=case.case_id,
        actual=(
            "direct eval rollout lifecycle scorer ASI GEPA compare credentials eval category real task distribution "
            "edge cases failure modes split strategy what this eval does not measure grading strategy grader type "
            "calibration examples reliability risks optimizer acceptance optimized metric diagnostic metrics guardrail metrics "
            "promotion rule regression tolerance aggregate score"
        ),
    )

    score = eval_validation.semantic_required_concepts_scorer(case, rollout)

    assert score.subscores["evidence_contract_coverage"] < 0.5
    assert score.score < 1.0


def test_partial_intent_fixture_drafts_eval_contract() -> None:
    fixture = eval_validation.load_fixture("partial-intent-examples")
    case = next(case for case in eval_validation.default_eval_cases(fixture) if case.metadata.get("artifact_type") == "proposal")
    rollout = eval_validation.EvalValidationExecutor(fixture=fixture, run_dir=Path("runs/test")).run(
        eval_validation.default_seed_candidate(fixture),
        case,
        timeout_seconds=1.0,
    )
    score = eval_validation.semantic_required_concepts_scorer(case, rollout)

    assert score.score == 1.0
    assert score.subscores["semantic_concept_coverage"] == 1.0
    assert score.subscores["lightweight_user_flow"] == 1.0


def test_negative_fixture_scores_useful_failure() -> None:
    fixture = eval_validation.load_fixture("unsupported-runtime")
    case = eval_validation.default_eval_cases(fixture)[0]
    rollout = eval_validation.EvalValidationExecutor(fixture=fixture, run_dir=Path("runs/test")).run(
        eval_validation.default_seed_candidate(fixture),
        case,
        timeout_seconds=1.0,
    )

    score = eval_validation.negative_fixture_useful_failure_scorer(case, rollout)

    assert score.score == 1.0
    assert not rollout.errors


def test_negative_evidence_gap_fixtures_load() -> None:
    fixture_ids = [
        "aggregate-only-scoring",
        "missing-judge-records",
        "missing-asi-records",
        "missing-optimizer-lineage",
        "missing-promotion-evidence",
    ]

    for fixture_id in fixture_ids:
        fixture = eval_validation.load_fixture(fixture_id)
        case = eval_validation.default_eval_cases(fixture)[0]
        assert not fixture.is_positive
        assert fixture.expected_failure
        assert fixture.expected_failure in str(case.expected)


def test_evidence_ledger_validation_detects_missing_records(tmp_path: Path) -> None:
    errors = eval_validation.validate_evidence_ledger(tmp_path)

    assert "evidence/manifest.json: missing" in errors
    assert "evidence/promotion.json: missing" in errors


def test_generate_eval_compare_optimize_verify_smoke(tmp_path: Path) -> None:
    run_dir = tmp_path / "eval-validation"
    fixture = "optimizespec-managed-agent"

    assert eval_validation.cmd_generate(fixture, str(run_dir), None, live=False) == 0
    assert eval_validation.cmd_eval(fixture, str(run_dir), None, None, 60.0, True, live=False) == 0
    assert eval_validation.cmd_compare(fixture, str(run_dir), None, None, None, 60.0, True, live=False) == 0
    assert eval_validation.cmd_optimize(fixture, str(run_dir), None, None, 1, "anthropic/claude-opus-4-7", 60.0, True, live=False, release_budget=False) == 0
    assert eval_validation.cmd_verify(fixture, str(run_dir), live=False) == 0

    assert (run_dir / "generated" / "proposal.md").exists()
    assert (run_dir / "eval" / "summary.json").exists()
    assert (run_dir / "compare" / "comparison.json").exists()
    assert (run_dir / "optimize" / "candidates.json").exists()
    assert (run_dir / "command-logs" / "generate.json").exists()
    assert (run_dir / "evidence" / "manifest.json").exists()
    assert (run_dir / "evidence" / "candidate-registry.json").exists()
    assert (run_dir / "evidence" / "evaluations" / "candidate" / "summary.json").exists()
    assert (run_dir / "evidence" / "optimizer" / "lineage.json").exists()
    assert (run_dir / "evidence" / "promotion.json").exists()
    verification = json.loads((run_dir / "verification" / "verification.json").read_text(encoding="utf-8"))
    assert verification["success"] is True


def test_documented_module_commands_execute(tmp_path: Path) -> None:
    run_dir = tmp_path / "documented"
    commands = [
        ["generate", "--fixture", "optimizespec-package-guidance", "--run-dir", str(run_dir)],
        ["eval", "--fixture", "optimizespec-package-guidance", "--run-dir", str(run_dir), "--skip-system-loop"],
        ["compare", "--fixture", "optimizespec-package-guidance", "--run-dir", str(run_dir), "--skip-system-loop"],
        [
            "optimize",
            "--fixture",
            "optimizespec-package-guidance",
            "--run-dir",
            str(run_dir),
            "--max-metric-calls",
            "1",
            "--skip-system-loop",
        ],
        ["verify", "--fixture", "optimizespec-package-guidance", "--run-dir", str(run_dir)],
    ]

    for args in commands:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "examples" / "python-managed-agent" / "src")
        completed = subprocess.run(
            [sys.executable, "-m", "optimizespec.eval_validation", *args],
            cwd=Path.cwd(),
            text=True,
            capture_output=True,
            timeout=90,
            env=env,
        )
        assert completed.returncode == 0, completed.stderr

    assert (run_dir / "verification" / "verification.json").exists()


def test_system_loop_eval_scores_one(tmp_path: Path) -> None:
    fixture = eval_validation.load_fixture("optimizespec-managed-agent")
    cases = [case for case in eval_validation.default_eval_cases(fixture) if case.metadata.get("artifact_type") == "system_loop"]
    summary = eval_validation.evaluate_candidate(
        candidate=eval_validation.default_seed_candidate(fixture),
        cases=cases,
        executor=eval_validation.EvalValidationExecutor(fixture=fixture, run_dir=tmp_path),
        run_dir=tmp_path / "eval",
        mutable_fields=eval_validation.MUTABLE_FIELDS,
        custom_scorers=eval_validation.custom_scorers(),
        timeout_seconds=90.0,
    )

    assert summary["mean_test_score"] == 1.0
    side_info = json.loads(
        (tmp_path / "eval" / "rollouts" / "candidate" / f"{fixture.fixture_id}-system-loop" / "side_info.json").read_text(
            encoding="utf-8"
        )
    )
    assert side_info["scores"]["system_loop_success"] == 1.0
