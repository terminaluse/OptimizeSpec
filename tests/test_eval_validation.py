from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from claude_gepa import eval_validation
from claude_gepa.self_improvement import EvalCase, RolloutResult, ScorerSpec


def test_fixture_metadata_contract_loads_positive_fixture() -> None:
    fixture = eval_validation.load_fixture("claude-gepa-managed-agent")

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
    assert "GEPA" in score.feedback


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
    assert "unsupported runtime" in str(rollout.actual).lower()


def test_generate_eval_compare_optimize_verify_smoke(tmp_path: Path) -> None:
    run_dir = tmp_path / "eval-validation"
    fixture = "claude-gepa-managed-agent"

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
    verification = json.loads((run_dir / "verification" / "verification.json").read_text(encoding="utf-8"))
    assert verification["success"] is True


def test_documented_module_commands_execute(tmp_path: Path) -> None:
    run_dir = tmp_path / "documented"
    commands = [
        ["generate", "--fixture", "claude-gepa-package-guidance", "--run-dir", str(run_dir)],
        ["eval", "--fixture", "claude-gepa-package-guidance", "--run-dir", str(run_dir), "--skip-system-loop"],
        ["compare", "--fixture", "claude-gepa-package-guidance", "--run-dir", str(run_dir), "--skip-system-loop"],
        [
            "optimize",
            "--fixture",
            "claude-gepa-package-guidance",
            "--run-dir",
            str(run_dir),
            "--max-metric-calls",
            "1",
            "--skip-system-loop",
        ],
        ["verify", "--fixture", "claude-gepa-package-guidance", "--run-dir", str(run_dir)],
    ]

    for args in commands:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")
        completed = subprocess.run(
            [sys.executable, "-m", "claude_gepa.eval_validation", *args],
            cwd=Path.cwd(),
            text=True,
            capture_output=True,
            timeout=90,
            env=env,
        )
        assert completed.returncode == 0, completed.stderr

    assert (run_dir / "verification" / "verification.json").exists()


def test_system_loop_eval_scores_one(tmp_path: Path) -> None:
    fixture = eval_validation.load_fixture("claude-gepa-managed-agent")
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
