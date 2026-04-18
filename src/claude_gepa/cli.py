from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from .candidate import DEFAULT_SEED_CANDIDATE
from .evaluator import ManagedAgentEvaluator
from .optimizer import DEMO_SEED_CANDIDATE, diff_candidates, evaluate_candidate_suite, optimize_demo
from .tasks import VAL_TASKS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="claude-gepa")
    subparsers = parser.add_subparsers(dest="command", required=True)

    eval_demo = subparsers.add_parser("eval-demo", help="Run one direct evaluation on the first validation task.")
    eval_demo.add_argument("--run-dir", default="runs/eval-demo")

    optimize = subparsers.add_parser("optimize-demo", help="Run a GEPA optimization job from the weak demo seed.")
    optimize.add_argument("--max-metric-calls", type=int, default=3)
    optimize.add_argument("--reflection-model", default="anthropic/claude-opus-4-7")
    optimize.add_argument("--run-dir", default="runs/gepa-demo")

    compare = subparsers.add_parser(
        "compare-demo",
        help="Show the input candidate, optimized candidate, and eval deltas on the widened benchmark.",
    )
    compare.add_argument("--max-metric-calls", type=int, default=4)
    compare.add_argument("--reflection-model", default="anthropic/claude-opus-4-7")
    compare.add_argument("--run-dir", default="runs/compare-demo")

    show = subparsers.add_parser("show-seed", help="Print the default strong seed candidate.")
    show.add_argument("--pretty", action="store_true")

    return parser


def require_api_key() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is required")


def cmd_eval_demo(run_dir: str) -> int:
    require_api_key()
    evaluator = ManagedAgentEvaluator(run_dir=Path(run_dir))
    score, side_info = evaluator(dict(DEFAULT_SEED_CANDIDATE), example=VAL_TASKS[0])
    print(json.dumps({"score": score, "side_info": side_info}, indent=2, sort_keys=True))
    return 0


def cmd_optimize_demo(max_metric_calls: int, reflection_model: str, run_dir: str) -> int:
    require_api_key()
    result = optimize_demo(
        max_metric_calls=max_metric_calls,
        reflection_model=reflection_model,
        run_dir=run_dir,
    )
    print(json.dumps(result.best_candidate, indent=2, sort_keys=True))
    return 0


def cmd_compare_demo(max_metric_calls: int, reflection_model: str, run_dir: str) -> int:
    require_api_key()
    run_path = Path(run_dir)
    input_candidate = dict(DEMO_SEED_CANDIDATE)
    result = optimize_demo(
        max_metric_calls=max_metric_calls,
        reflection_model=reflection_model,
        run_dir=str(run_path / "optimize"),
        seed_candidate=input_candidate,
    )
    final_candidate = dict(result.best_candidate)

    baseline_eval = evaluate_candidate_suite(input_candidate, run_dir=str(run_path / "baseline-eval"), use_outcomes=False)
    final_eval = evaluate_candidate_suite(final_candidate, run_dir=str(run_path / "final-eval"), use_outcomes=False)

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

    if args.command == "eval-demo":
        return cmd_eval_demo(args.run_dir)
    if args.command == "optimize-demo":
        return cmd_optimize_demo(args.max_metric_calls, args.reflection_model, args.run_dir)
    if args.command == "compare-demo":
        return cmd_compare_demo(args.max_metric_calls, args.reflection_model, args.run_dir)
    if args.command == "show-seed":
        return cmd_show_seed(args.pretty)

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
