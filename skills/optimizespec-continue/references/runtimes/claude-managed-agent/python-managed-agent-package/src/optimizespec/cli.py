from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Sequence

from .candidate import DEFAULT_SEED_CANDIDATE, CandidateBundle, CandidateCompilationError
from .evaluator import ManagedAgentEvaluator
from .optimizer import DEMO_SEED_CANDIDATE, diff_candidates, evaluate_candidate_suite, optimize_demo
from .tasks import TRAIN_TASKS, VAL_TASKS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="optimizespec")
    subparsers = parser.add_subparsers(dest="command", required=True)

    eval_demo = subparsers.add_parser("eval-demo", help="Run one direct evaluation on the first validation task.")
    eval_demo.add_argument("--run-dir", default="runs/eval-demo")
    eval_demo.add_argument("--max-runtime-seconds", type=float, default=300.0)

    live_eval = subparsers.add_parser(
        "live-eval",
        help="Run one live Managed Agents rollout against a packaged eval case.",
    )
    live_eval.add_argument("--run-dir", default="runs/live-eval")
    live_eval.add_argument("--max-runtime-seconds", type=float, default=300.0)

    optimize = subparsers.add_parser("optimize-demo", help="Run a GEPA optimization job from the weak demo seed.")
    optimize.add_argument("--max-metric-calls", type=int, default=48)
    optimize.add_argument("--reflection-model", default="anthropic/claude-opus-4-7")
    optimize.add_argument("--run-dir", default="runs/gepa-demo")
    optimize.add_argument("--max-runtime-seconds", type=float, default=120.0)

    live_optimize = subparsers.add_parser(
        "live-optimize",
        help="Run the live Managed Agents optimizer loop against packaged eval cases.",
    )
    live_optimize.add_argument("--max-metric-calls", type=int, default=48)
    live_optimize.add_argument("--reflection-model", default="anthropic/claude-opus-4-7")
    live_optimize.add_argument("--run-dir", default="runs/live-optimize")
    live_optimize.add_argument("--max-runtime-seconds", type=float, default=120.0)

    compare = subparsers.add_parser(
        "compare-demo",
        help="Show the input candidate, optimized candidate, and eval deltas on the widened benchmark.",
    )
    compare.add_argument("--max-metric-calls", type=int, default=48)
    compare.add_argument("--reflection-model", default="anthropic/claude-opus-4-7")
    compare.add_argument("--run-dir", default="runs/compare-demo")
    compare.add_argument("--max-runtime-seconds", type=float, default=120.0)

    show = subparsers.add_parser("show-seed", help="Print the default strong seed candidate.")
    show.add_argument("--pretty", action="store_true")

    return parser


def require_api_key() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is required")


def progress(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def cmd_eval_demo(run_dir: str, max_runtime_seconds: float) -> int:
    require_api_key()
    progress(f"Running live Managed Agents eval: run_dir={run_dir} max_runtime_seconds={max_runtime_seconds}")
    evaluator = ManagedAgentEvaluator(run_dir=Path(run_dir), max_runtime_seconds=max_runtime_seconds)
    score, side_info = evaluator(dict(DEFAULT_SEED_CANDIDATE), example=VAL_TASKS[0])
    print(json.dumps({"score": score, "side_info": side_info}, indent=2, sort_keys=True))
    return 0


def cmd_optimize_demo(
    max_metric_calls: int,
    reflection_model: str,
    run_dir: str,
    max_runtime_seconds: float,
) -> int:
    require_api_key()
    progress(
        "Running live Managed Agents optimizer: "
        f"run_dir={run_dir} max_metric_calls={max_metric_calls} max_runtime_seconds={max_runtime_seconds}"
    )
    result = optimize_demo(
        max_metric_calls=max_metric_calls,
        reflection_model=reflection_model,
        run_dir=run_dir,
        max_runtime_seconds=max_runtime_seconds,
    )
    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)
    candidate_manifest = annotate_candidates_file(run_path)
    best_candidate = dict(result.best_candidate)
    best_candidate_id = find_candidate_id_in_manifest(best_candidate, candidate_manifest) or candidate_id_for(best_candidate)
    per_case_live_scores = collect_score_manifest(run_path)
    summary = {
        "best_candidate_id": best_candidate_id,
        "best_candidate": result.best_candidate,
        "candidate_manifest_path": "candidates.json" if candidate_manifest else None,
        "score_summary": summarize_live_scores(per_case_live_scores, best_candidate_id),
        "per_case_live_scores": per_case_live_scores,
        "budgets": {
            "max_metric_calls": max_metric_calls,
            "eval_case_count": len(TRAIN_TASKS) + len(VAL_TASKS),
            "train_case_count": len(TRAIN_TASKS),
            "val_case_count": len(VAL_TASKS),
            "per_rollout_timeout_seconds": max_runtime_seconds,
            "usage_or_cost_limits": None,
        },
        "lineage": {
            "gepa_run_dir": str(run_path),
            "rollout_evidence_root": str(run_path),
            "reflection_model": reflection_model,
        },
    }
    (run_path / "optimizer-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    progress(f"Wrote live optimizer summary: {run_path / 'optimizer-summary.json'}")
    print(json.dumps(result.best_candidate, indent=2, sort_keys=True))
    return 0


def annotate_candidates_file(run_path: Path) -> list[dict[str, object]]:
    candidates_path = run_path / "candidates.json"
    if not candidates_path.exists():
        return []
    try:
        raw_candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(raw_candidates, list):
        return []

    id_lookup = build_candidate_id_lookup(run_path)
    annotated: list[dict[str, object]] = []
    for index, item in enumerate(raw_candidates):
        if isinstance(item, dict) and "candidate" in item and "candidate_id" in item:
            annotated.append(dict(item))
            continue
        if not isinstance(item, dict):
            annotated.append(
                {
                    "candidate_id": None,
                    "candidate_index": index,
                    "candidate": item,
                }
            )
            continue
        candidate = {str(key): str(value) for key, value in item.items()}
        candidate_id = id_lookup.get(candidate_fingerprint(candidate)) or offline_candidate_id(candidate)
        annotated.append(
            {
                "candidate_id": candidate_id,
                "candidate_index": index,
                "candidate": candidate,
            }
        )
    candidates_path.write_text(json.dumps(annotated, indent=2, sort_keys=True), encoding="utf-8")
    return annotated


def find_candidate_id_in_manifest(candidate: dict[str, str], manifest: list[dict[str, object]]) -> str | None:
    target = candidate_fingerprint(candidate)
    for entry in manifest:
        if not isinstance(entry, dict):
            continue
        entry_candidate = entry.get("candidate")
        if not isinstance(entry_candidate, dict):
            continue
        entry_candidate_text = {str(key): str(value) for key, value in entry_candidate.items()}
        if candidate_fingerprint(entry_candidate_text) == target:
            candidate_id = entry.get("candidate_id")
            return candidate_id if isinstance(candidate_id, str) else None
    return None


def build_candidate_id_lookup(run_path: Path) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for candidate_path in sorted(run_path.rglob("candidate.json")):
        candidate_id = infer_candidate_id_from_evidence_path(candidate_path.relative_to(run_path))
        if candidate_id is None:
            continue
        try:
            payload = json.loads(candidate_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for candidate in candidate_payloads(payload):
            lookup[candidate_fingerprint(candidate)] = candidate_id
    return lookup


def candidate_payloads(payload: object) -> list[dict[str, str]]:
    if not isinstance(payload, dict):
        return []
    candidates: list[dict[str, str]] = []
    for key in ("raw_fields", "canonical_fields"):
        value = payload.get(key)
        if isinstance(value, dict):
            candidates.append({str(field): str(field_value) for field, field_value in value.items()})
    if not candidates:
        candidates.append({str(field): str(field_value) for field, field_value in payload.items()})
    return candidates


def infer_candidate_id_from_evidence_path(relative_path: Path) -> str | None:
    parts = relative_path.parts
    if len(parts) >= 4 and parts[0] == "rollouts":
        return parts[1]
    if len(parts) >= 3:
        return parts[0]
    return None


def candidate_fingerprint(candidate: dict[str, str]) -> str:
    return json.dumps(candidate, sort_keys=True, separators=(",", ":"))


def offline_candidate_id(candidate: dict[str, str]) -> str:
    return hashlib.sha256(candidate_fingerprint(candidate).encode("utf-8")).hexdigest()[:12]


def candidate_id_for(candidate: dict[str, str]) -> str | None:
    try:
        return CandidateBundle.from_candidate(candidate).candidate_id
    except CandidateCompilationError:
        return None


def collect_score_manifest(run_path: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for score_path in sorted(run_path.rglob("score.json")):
        try:
            score_record = json.loads(score_path.read_text(encoding="utf-8"))
        except Exception as exc:
            entries.append(
                {
                    "score_path": str(score_path.relative_to(run_path)),
                    "parse_error": str(exc),
                }
            )
            continue

        relative_score_path = score_path.relative_to(run_path)
        path_candidate_id, path_eval_case_id = infer_ids_from_score_path(relative_score_path)
        candidate_id = score_record.get("candidate_id") or path_candidate_id
        eval_case_id = score_record.get("eval_case_id") or path_eval_case_id
        rollout_evidence_path = resolve_relative_evidence_path(
            run_path,
            score_path,
            score_record.get("rollout_evidence_path"),
        )
        side_info_path = resolve_relative_evidence_path(run_path, score_path, score_record.get("side_info_path"))
        result_path = resolve_relative_evidence_path(run_path, score_path, score_record.get("result_path"))
        entries.append(
            {
                "candidate_id": candidate_id,
                "eval_case_id": eval_case_id,
                "score": score_record.get("score"),
                "scores": score_record.get("scores") or score_record.get("subscores") or {},
                "feedback": score_record.get("feedback"),
                "outcome_result": score_record.get("outcome_result"),
                "errors": score_record.get("errors", []),
                "score_path": str(relative_score_path),
                "rollout_evidence_path": rollout_evidence_path,
                "side_info_path": side_info_path,
                "result_path": result_path,
            }
        )
    return entries


def infer_ids_from_score_path(relative_score_path: Path) -> tuple[str | None, str | None]:
    parts = relative_score_path.parts
    if len(parts) >= 4 and parts[0] == "rollouts":
        return parts[1], parts[2]
    if len(parts) >= 3:
        return parts[0], parts[1]
    return None, None


def resolve_relative_evidence_path(run_path: Path, score_path: Path, evidence_path: object) -> str | None:
    if not isinstance(evidence_path, str) or not evidence_path:
        return None
    candidate = score_path.parent / evidence_path
    try:
        return str(candidate.relative_to(run_path))
    except ValueError:
        return str(candidate)


def summarize_live_scores(entries: list[dict[str, object]], best_candidate_id: str | None) -> dict[str, object]:
    scored_entries = [entry for entry in entries if isinstance(entry.get("score"), (int, float))]
    best_entries = [
        entry for entry in scored_entries if best_candidate_id is not None and entry.get("candidate_id") == best_candidate_id
    ]
    summary_entries = best_entries or scored_entries
    scores = [float(entry["score"]) for entry in summary_entries]
    return {
        "best_candidate_score_count": len(best_entries),
        "all_live_score_count": len(scored_entries),
        "mean_score": sum(scores) / len(scores) if scores else 0.0,
        "min_score": min(scores) if scores else 0.0,
        "max_score": max(scores) if scores else 0.0,
    }


def cmd_compare_demo(
    max_metric_calls: int,
    reflection_model: str,
    run_dir: str,
    max_runtime_seconds: float,
) -> int:
    require_api_key()
    run_path = Path(run_dir)
    input_candidate = dict(DEMO_SEED_CANDIDATE)
    result = optimize_demo(
        max_metric_calls=max_metric_calls,
        reflection_model=reflection_model,
        run_dir=str(run_path / "optimize"),
        seed_candidate=input_candidate,
        max_runtime_seconds=max_runtime_seconds,
    )
    final_candidate = dict(result.best_candidate)

    baseline_eval = evaluate_candidate_suite(
        input_candidate,
        run_dir=str(run_path / "baseline-eval"),
        use_outcomes=True,
        max_runtime_seconds=max_runtime_seconds,
    )
    final_eval = evaluate_candidate_suite(
        final_candidate,
        run_dir=str(run_path / "final-eval"),
        use_outcomes=True,
        max_runtime_seconds=max_runtime_seconds,
    )

    baseline_by_task = {item["task_id"]: item for item in baseline_eval["tasks"]}
    final_by_task = {item["task_id"]: item for item in final_eval["tasks"]}
    task_deltas = []
    for task_id in sorted(set(baseline_by_task) | set(final_by_task)):
        before = baseline_by_task.get(task_id, {})
        after = final_by_task.get(task_id, {})
        baseline_score = float(before.get("score", 0.0) or 0.0)
        final_score = float(after.get("score", 0.0) or 0.0)
        task_deltas.append(
            {
                "task_id": task_id,
                "split": after.get("split") or before.get("split"),
                "baseline_score": baseline_score,
                "final_score": final_score,
                "delta": final_score - baseline_score,
                "expected_output": after.get("expected_output") or before.get("expected_output"),
                "baseline_actual_output": before.get("actual_output"),
                "final_actual_output": after.get("actual_output"),
            }
        )

    payload = {
        "input_candidate": input_candidate,
        "final_candidate": final_candidate,
        "candidate_diff": diff_candidates(input_candidate, final_candidate),
        "baseline_eval": baseline_eval,
        "final_eval": final_eval,
        "eval_deltas": {
            "mean_train_score_delta": final_eval["mean_train_score"] - baseline_eval["mean_train_score"],
            "mean_val_score_delta": final_eval["mean_val_score"] - baseline_eval["mean_val_score"],
            "mean_score_delta": final_eval["mean_score"] - baseline_eval["mean_score"],
            "task_deltas": task_deltas,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_show_seed(pretty: bool) -> int:
    if pretty:
        print(json.dumps(DEFAULT_SEED_CANDIDATE, indent=2, sort_keys=True))
    else:
        print(json.dumps(DEFAULT_SEED_CANDIDATE))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in {"eval-demo", "live-eval"}:
        return cmd_eval_demo(args.run_dir, args.max_runtime_seconds)
    if args.command in {"optimize-demo", "live-optimize"}:
        return cmd_optimize_demo(
            args.max_metric_calls,
            args.reflection_model,
            args.run_dir,
            args.max_runtime_seconds,
        )
    if args.command == "compare-demo":
        return cmd_compare_demo(
            args.max_metric_calls,
            args.reflection_model,
            args.run_dir,
            args.max_runtime_seconds,
        )
    if args.command == "show-seed":
        return cmd_show_seed(args.pretty)

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
