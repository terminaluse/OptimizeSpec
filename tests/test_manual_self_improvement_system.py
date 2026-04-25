from __future__ import annotations

import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path("examples/python-managed-agent/optimizespec/changes/manual-self-improvement-system/manual_self_improve.py")
CHANGE_DIR = MODULE_PATH.parent


def load_manual_runner():
    spec = importlib.util.spec_from_file_location("manual_self_improve", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manual_self_improvement_runner_reference_end_to_end(tmp_path: Path) -> None:
    module = load_manual_runner()
    run_dir = tmp_path / "manual-run"
    cases = str(CHANGE_DIR / "eval-cases.yaml")
    seed = str(CHANGE_DIR / "seed-candidate.yaml")
    improved = str(CHANGE_DIR / "improved-candidate.yaml")

    assert module.cmd_eval(cases, seed, str(run_dir)) == 0
    assert module.cmd_compare(cases, seed, improved, str(run_dir)) == 0
    assert module.cmd_optimize(cases, seed, improved, str(run_dir), "reference", 0, "anthropic/claude-opus-4-7") == 0
    assert module.cmd_verify(str(run_dir), require_optimizer=True) == 0

    required_files = [
        "evidence/manifest.json",
        "evidence/candidate-registry.json",
        "evidence/evaluations/seed/summary.json",
        "evidence/evaluations/seed/cases/echo-alpha/score.json",
        "evidence/evaluations/seed/cases/echo-alpha/judge.json",
        "evidence/evaluations/seed/cases/echo-alpha/side_info.json",
        "evidence/evaluations/seed/cases/echo-alpha/rollout.json",
        "evidence/evaluations/selected/summary.json",
        "evidence/evaluations/selected/cases/echo-gamma/score.json",
        "evidence/comparisons/comparison.json",
        "evidence/optimizer/lineage.json",
        "evidence/optimizer/leaderboard.json",
        "evidence/optimizer/events.jsonl",
        "evidence/promotion.json",
        "verification/verification.json",
    ]
    for relative in required_files:
        assert (run_dir / relative).exists(), relative

    promotion = json.loads((run_dir / "evidence" / "promotion.json").read_text(encoding="utf-8"))
    assert promotion["decision"] == "promoted"
    assert promotion["promoted_candidate_id"] == "selected"

    selected = json.loads((run_dir / "evidence" / "evaluations" / "selected" / "summary.json").read_text(encoding="utf-8"))
    seed_summary = json.loads((run_dir / "evidence" / "evaluations" / "seed" / "summary.json").read_text(encoding="utf-8"))
    assert selected["mean_score"] == 1.0
    assert seed_summary["mean_score"] == 0.0

    side_info = json.loads(
        (run_dir / "evidence" / "evaluations" / "selected" / "cases" / "echo-gamma" / "side_info.json").read_text(
            encoding="utf-8"
        )
    )
    assert side_info["asi_passed_to_optimizer"] is True
    assert side_info["scores"]["correctness"] == 1.0
