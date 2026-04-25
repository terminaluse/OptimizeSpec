from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Sequence

import yaml


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from optimizespec.self_improvement import (  # noqa: E402
    EvalCase,
    TemplateEchoExecutor,
    compare_candidates,
    evaluate_candidate,
    load_candidate,
    load_eval_cases,
    optimize_candidate,
    stable_candidate_id,
)


CHANGE_DIR = Path(__file__).resolve().parent
DEFAULT_CASES = CHANGE_DIR / "eval-cases.yaml"
DEFAULT_SEED = CHANGE_DIR / "seed-candidate.yaml"
DEFAULT_IMPROVED = CHANGE_DIR / "improved-candidate.yaml"
MUTABLE_FIELDS = ["answer_template", "reflection_guidance"]
RUNTIME_NAME = "TemplateEchoExecutor"


def load_dotenv_key() -> None:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped.removeprefix("export ").strip()
        key, separator, value = stripped.partition("=")
        if key == "ANTHROPIC_API_KEY" and separator:
            os.environ[key] = value.strip().strip("'\"")
            return


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases(path: str | Path = DEFAULT_CASES) -> list[EvalCase]:
    return load_eval_cases(Path(path))


def load_yaml_candidate(path: str | Path) -> dict[str, str]:
    return load_candidate(Path(path))


def evidence_root(run_dir: Path) -> Path:
    return run_dir / "evidence"


def existing_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = read_json(path)
    return payload if isinstance(payload, dict) else {}


def unique(items: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        value = str(item)
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def update_manifest(run_dir: Path, *, command: str, candidate_ids: Sequence[str], case_ids: Sequence[str]) -> None:
    path = evidence_root(run_dir) / "manifest.json"
    previous = existing_manifest(path)
    commands = list(previous.get("commands", [])) if isinstance(previous.get("commands"), list) else []
    commands.append({"name": command, "recorded_at": time.time()})
    payload = {
        "run_id": previous.get("run_id") or run_dir.name,
        "target": "manual-self-improvement-system",
        "runtime": RUNTIME_NAME,
        "commands": commands,
        "candidate_ids": unique([*(previous.get("candidate_ids") or []), *candidate_ids]),
        "case_ids": unique([*(previous.get("case_ids") or []), *case_ids]),
        "evidence_root": "evidence",
        "ledger_contract": "eval-system-evidence",
    }
    write_json(path, payload)


def update_candidate_registry(
    run_dir: Path,
    candidates: dict[str, dict[str, str]],
    *,
    parent_ids: dict[str, str | None] | None = None,
    reason: str,
) -> None:
    path = evidence_root(run_dir) / "candidate-registry.json"
    previous = existing_manifest(path)
    records = {
        str(item.get("candidate_id")): item
        for item in previous.get("candidates", [])
        if isinstance(item, dict) and item.get("candidate_id")
    }
    for candidate_id, candidate in candidates.items():
        records[candidate_id] = {
            "candidate_id": candidate_id,
            "stable_content_id": stable_candidate_id(candidate),
            "parent_candidate_id": (parent_ids or {}).get(candidate_id),
            "mutable_fields": sorted(candidate),
            "fields": candidate,
            "creation_reason": reason,
            "rollback_target": (parent_ids or {}).get(candidate_id),
        }
    write_json(path, {"candidates": [records[key] for key in sorted(records)]})


def copy_json_or_write(source: Path, target: Path, fallback: dict[str, Any]) -> None:
    payload = read_json(source) if source.exists() else fallback
    write_json(target, payload)


def write_evaluation_evidence(
    run_dir: Path,
    *,
    evidence_candidate_id: str,
    source_candidate_id: str,
    source_dir: Path,
    summary: dict[str, Any],
    asi_passed_to_optimizer: bool,
) -> None:
    eval_root = evidence_root(run_dir) / "evaluations" / evidence_candidate_id
    write_json(eval_root / "summary.json", summary)
    for item in summary.get("cases", []):
        if not isinstance(item, dict):
            continue
        case_id = str(item.get("case_id") or "").strip()
        if not case_id:
            continue
        source_case = source_dir / "rollouts" / source_candidate_id / case_id
        target_case = eval_root / "cases" / case_id
        score_payload = {
            "candidate_id": evidence_candidate_id,
            "case_id": case_id,
            "score": item.get("score"),
            "feedback": item.get("feedback"),
            "criterion": "exact_match",
            "scorer_identity": "exact_match",
            "higher_is_better": True,
            "errors": item.get("errors", []),
        }
        copy_json_or_write(source_case / "score.json", target_case / "score.json", score_payload)
        judge_payload = {
            "candidate_id": evidence_candidate_id,
            "case_id": case_id,
            "grader_type": "deterministic",
            "rubric_or_criterion": "exact_match",
            "structured_output": {
                "score": item.get("score"),
                "feedback": item.get("feedback"),
            },
            "rationale_summary": item.get("feedback"),
            "calibration_status": "not_applicable",
            "reliability_warnings": [],
            "human_review_trigger": None,
        }
        write_json(target_case / "judge.json", judge_payload)
        side_info = read_json(source_case / "side_info.json") if (source_case / "side_info.json").exists() else {}
        if isinstance(side_info, dict):
            side_info["candidate_id"] = evidence_candidate_id
            side_info["case_id"] = case_id
            side_info["asi_passed_to_optimizer"] = asi_passed_to_optimizer
        write_json(target_case / "side_info.json", side_info)
        copy_json_or_write(
            source_case / "rollout.json",
            target_case / "rollout.json",
            {"candidate_id": evidence_candidate_id, "case_id": case_id, "errors": item.get("errors", [])},
        )


def write_comparison_evidence(run_dir: Path, comparison: dict[str, Any]) -> None:
    write_json(evidence_root(run_dir) / "comparisons" / "comparison.json", comparison)


def write_optimizer_evidence(
    run_dir: Path,
    *,
    mode: str,
    seed: dict[str, str],
    selected: dict[str, str],
    comparison: dict[str, Any],
    max_metric_calls: int,
) -> None:
    baseline_score = float(comparison.get("baseline", {}).get("mean_score", 0.0) or 0.0)
    selected_score = float(comparison.get("candidate", {}).get("mean_score", 0.0) or 0.0)
    candidate_errors = [
        error
        for item in comparison.get("candidate", {}).get("cases", [])
        if isinstance(item, dict)
        for error in item.get("errors", [])
    ]
    promoted = selected_score > baseline_score and not candidate_errors
    lineage = {
        "mode": mode,
        "seed_candidate_id": "seed",
        "selected_candidate_id": "selected",
        "max_metric_calls": max_metric_calls,
        "seed_stable_content_id": stable_candidate_id(seed),
        "selected_stable_content_id": stable_candidate_id(selected),
        "mutation_summary": comparison.get("candidate_diff", {}),
    }
    leaderboard = {
        "objective_metric": "mean_score",
        "candidates": [
            {"candidate_id": "seed", "score": baseline_score, "selected": False},
            {"candidate_id": "selected", "score": selected_score, "selected": True},
        ],
    }
    promotion = {
        "decision": "promoted" if promoted else "not_promoted",
        "promoted_candidate_id": "selected" if promoted else None,
        "selected_candidate_id": "selected",
        "compared_candidates": ["seed", "selected"],
        "objective_metric_result": {"baseline": baseline_score, "selected": selected_score},
        "guardrail_result": "passed" if promoted else "not_passed",
        "manual_review_required": mode == "gepa",
        "rollback_path": "seed",
        "reason": "Selected candidate improved mean_score." if promoted else "Selected candidate did not improve mean_score.",
    }
    root = evidence_root(run_dir)
    write_json(root / "optimizer" / "lineage.json", lineage)
    write_json(root / "optimizer" / "leaderboard.json", leaderboard)
    events_path = root / "optimizer" / "events.jsonl"
    events_path.parent.mkdir(parents=True, exist_ok=True)
    events_path.write_text(
        json.dumps({"event": "optimizer_completed", "mode": mode, "selected_candidate_id": "selected"}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_json(root / "promotion.json", promotion)


def run_direct_eval(run_dir: Path, candidate: dict[str, str], cases: list[EvalCase], *, candidate_id: str) -> dict[str, Any]:
    return evaluate_candidate(
        candidate=candidate,
        cases=cases,
        executor=TemplateEchoExecutor(),
        run_dir=run_dir,
        candidate_id=candidate_id,
        mutable_fields=MUTABLE_FIELDS,
    )


def cmd_show_candidate(candidate_path: str, pretty: bool) -> int:
    candidate = load_yaml_candidate(candidate_path)
    print(json.dumps(candidate, indent=2 if pretty else None, sort_keys=pretty))
    return 0


def cmd_eval(cases_path: str, candidate_path: str, run_dir: str) -> int:
    run_path = Path(run_dir)
    cases = load_cases(cases_path)
    candidate = load_yaml_candidate(candidate_path)
    summary = run_direct_eval(run_path / "eval", candidate, cases, candidate_id="candidate")
    update_manifest(run_path, command="eval", candidate_ids=["candidate"], case_ids=[case.case_id for case in cases])
    update_candidate_registry(run_path, {"candidate": candidate}, reason="direct eval")
    write_evaluation_evidence(
        run_path,
        evidence_candidate_id="candidate",
        source_candidate_id="candidate",
        source_dir=run_path / "eval",
        summary=summary,
        asi_passed_to_optimizer=False,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def cmd_compare(cases_path: str, baseline_path: str, candidate_path: str, run_dir: str) -> int:
    run_path = Path(run_dir)
    cases = load_cases(cases_path)
    baseline = load_yaml_candidate(baseline_path)
    candidate = load_yaml_candidate(candidate_path)
    comparison = compare_candidates(
        baseline=baseline,
        candidate=candidate,
        cases=cases,
        executor=TemplateEchoExecutor(),
        run_dir=run_path / "compare",
    )
    update_manifest(run_path, command="compare", candidate_ids=["baseline", "candidate"], case_ids=[case.case_id for case in cases])
    update_candidate_registry(run_path, {"baseline": baseline, "candidate": candidate}, reason="comparison")
    write_evaluation_evidence(
        run_path,
        evidence_candidate_id="baseline",
        source_candidate_id="baseline",
        source_dir=run_path / "compare" / "baseline",
        summary=comparison["baseline"],
        asi_passed_to_optimizer=False,
    )
    write_evaluation_evidence(
        run_path,
        evidence_candidate_id="candidate",
        source_candidate_id="candidate",
        source_dir=run_path / "compare" / "candidate",
        summary=comparison["candidate"],
        asi_passed_to_optimizer=False,
    )
    write_comparison_evidence(run_path, comparison)
    print(json.dumps(comparison, indent=2, sort_keys=True))
    return 0


def selected_candidate_for_mode(
    *,
    mode: str,
    seed: dict[str, str],
    cases: list[EvalCase],
    run_path: Path,
    max_metric_calls: int,
    reflection_model: str,
    reference_candidate_path: str,
) -> dict[str, str]:
    if mode == "reference":
        return load_yaml_candidate(reference_candidate_path)
    load_dotenv_key()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is required for --mode gepa")
    result = optimize_candidate(
        seed_candidate=seed,
        cases=cases,
        executor=TemplateEchoExecutor(),
        run_dir=run_path / "optimize" / "gepa",
        objective="Improve answer_template so every eval case echoes its input exactly.",
        background=(
            "The candidate has mutable fields answer_template and reflection_guidance. "
            "The executor renders answer_template with {input} and {expected}; a perfect answer_template is {input}."
        ),
        reflection_model=reflection_model,
        max_metric_calls=max_metric_calls,
        timeout_seconds=5.0,
        mutable_fields=MUTABLE_FIELDS,
        module_selector="round_robin",
    )
    return dict(result.best_candidate)


def cmd_optimize(
    cases_path: str,
    seed_path: str,
    reference_candidate_path: str,
    run_dir: str,
    mode: str,
    max_metric_calls: int,
    reflection_model: str,
) -> int:
    run_path = Path(run_dir)
    cases = load_cases(cases_path)
    seed = load_yaml_candidate(seed_path)
    selected = selected_candidate_for_mode(
        mode=mode,
        seed=seed,
        cases=cases,
        run_path=run_path,
        max_metric_calls=max_metric_calls,
        reflection_model=reflection_model,
        reference_candidate_path=reference_candidate_path,
    )
    write_json(run_path / "optimize" / "best-candidate.json", selected)
    (run_path / "optimize" / "best-candidate.yaml").write_text(yaml.safe_dump(selected, sort_keys=False), encoding="utf-8")
    comparison = compare_candidates(
        baseline=seed,
        candidate=selected,
        cases=cases,
        executor=TemplateEchoExecutor(),
        run_dir=run_path / "optimize" / "comparison",
    )
    update_manifest(run_path, command=f"optimize:{mode}", candidate_ids=["seed", "selected"], case_ids=[case.case_id for case in cases])
    update_candidate_registry(
        run_path,
        {"seed": seed, "selected": selected},
        parent_ids={"selected": "seed"},
        reason=f"{mode} optimization",
    )
    write_evaluation_evidence(
        run_path,
        evidence_candidate_id="seed",
        source_candidate_id="baseline",
        source_dir=run_path / "optimize" / "comparison" / "baseline",
        summary=comparison["baseline"],
        asi_passed_to_optimizer=True,
    )
    write_evaluation_evidence(
        run_path,
        evidence_candidate_id="selected",
        source_candidate_id="candidate",
        source_dir=run_path / "optimize" / "comparison" / "candidate",
        summary=comparison["candidate"],
        asi_passed_to_optimizer=True,
    )
    write_comparison_evidence(run_path, comparison)
    write_optimizer_evidence(run_path, mode=mode, seed=seed, selected=selected, comparison=comparison, max_metric_calls=max_metric_calls)
    payload = {
        "mode": mode,
        "best_candidate": selected,
        "baseline_score": comparison["baseline"]["mean_score"],
        "selected_score": comparison["candidate"]["mean_score"],
        "promotion": read_json(evidence_root(run_path) / "promotion.json"),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def validate_evidence(run_dir: Path, *, require_optimizer: bool) -> list[str]:
    errors: list[str] = []
    required = [
        "evidence/manifest.json",
        "evidence/candidate-registry.json",
    ]
    if require_optimizer:
        required.extend(
            [
                "evidence/comparisons/comparison.json",
                "evidence/optimizer/lineage.json",
                "evidence/optimizer/leaderboard.json",
                "evidence/optimizer/events.jsonl",
                "evidence/promotion.json",
            ]
        )
    for relative in required:
        if not (run_dir / relative).exists():
            errors.append(f"{relative}: missing")
    eval_root = evidence_root(run_dir) / "evaluations"
    case_dirs = sorted(eval_root.glob("*/cases/*")) if eval_root.exists() else []
    if not case_dirs:
        errors.append("evidence/evaluations/*/cases/*: missing")
    for case_dir in case_dirs:
        for name in ("score.json", "judge.json", "side_info.json", "rollout.json"):
            if not (case_dir / name).exists():
                errors.append(f"{case_dir.relative_to(run_dir)}/{name}: missing")
    if (evidence_root(run_dir) / "promotion.json").exists():
        promotion = read_json(evidence_root(run_dir) / "promotion.json")
        if promotion.get("decision") not in {"promoted", "not_promoted"}:
            errors.append("evidence/promotion.json: invalid decision")
    return errors


def cmd_verify(run_dir: str, require_optimizer: bool) -> int:
    run_path = Path(run_dir)
    errors = validate_evidence(run_path, require_optimizer=require_optimizer)
    payload = {
        "run_dir": str(run_path),
        "require_optimizer": require_optimizer,
        "errors": errors,
        "success": not errors,
    }
    write_json(run_path / "verification" / "verification.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="manual_self_improve.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show = subparsers.add_parser("show-candidate")
    show.add_argument("--candidate", default=str(DEFAULT_SEED))
    show.add_argument("--pretty", action="store_true")

    direct_eval = subparsers.add_parser("eval")
    direct_eval.add_argument("--cases", default=str(DEFAULT_CASES))
    direct_eval.add_argument("--candidate", default=str(DEFAULT_SEED))
    direct_eval.add_argument("--run-dir", default="runs/manual-self-improvement/eval")

    compare = subparsers.add_parser("compare")
    compare.add_argument("--cases", default=str(DEFAULT_CASES))
    compare.add_argument("--baseline", default=str(DEFAULT_SEED))
    compare.add_argument("--candidate", default=str(DEFAULT_IMPROVED))
    compare.add_argument("--run-dir", default="runs/manual-self-improvement/compare")

    optimize = subparsers.add_parser("optimize")
    optimize.add_argument("--cases", default=str(DEFAULT_CASES))
    optimize.add_argument("--seed", default=str(DEFAULT_SEED))
    optimize.add_argument("--reference-candidate", default=str(DEFAULT_IMPROVED))
    optimize.add_argument("--run-dir", default="runs/manual-self-improvement/optimize")
    optimize.add_argument("--mode", choices=["reference", "gepa"], default="gepa")
    optimize.add_argument("--max-metric-calls", type=int, default=8)
    optimize.add_argument("--reflection-model", default="anthropic/claude-opus-4-7")

    verify = subparsers.add_parser("verify")
    verify.add_argument("--run-dir", default="runs/manual-self-improvement/optimize")
    verify.add_argument("--require-optimizer", action="store_true")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-candidate":
        return cmd_show_candidate(args.candidate, args.pretty)
    if args.command == "eval":
        return cmd_eval(args.cases, args.candidate, args.run_dir)
    if args.command == "compare":
        return cmd_compare(args.cases, args.baseline, args.candidate, args.run_dir)
    if args.command == "optimize":
        return cmd_optimize(
            args.cases,
            args.seed,
            args.reference_candidate,
            args.run_dir,
            args.mode,
            args.max_metric_calls,
            args.reflection_model,
        )
    if args.command == "verify":
        return cmd_verify(args.run_dir, args.require_optimizer)
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
