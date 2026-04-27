from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from .candidate import DEFAULT_SEED_CANDIDATE
from .evaluator import ManagedAgentEvaluator
from . import eval_validation
from .optimizer import DEMO_SEED_CANDIDATE, diff_candidates, evaluate_candidate_suite, optimize_demo
from .self_improvement import (
    TemplateEchoExecutor,
    compare_candidates,
    evaluate_candidate,
    load_candidate,
    load_eval_cases,
    optimize_candidate,
)
from .tasks import VAL_TASKS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="optimizespec")
    subparsers = parser.add_subparsers(dest="command", required=True)

    eval_demo = subparsers.add_parser("eval-demo", help="Run one direct evaluation on the first validation task.")
    eval_demo.add_argument("--run-dir", default="runs/eval-demo")
    eval_demo.add_argument("--max-runtime-seconds", type=float, default=300.0)

    optimize = subparsers.add_parser("optimize-demo", help="Run a GEPA optimization job from the weak demo seed.")
    optimize.add_argument("--max-metric-calls", type=int, default=48)
    optimize.add_argument("--reflection-model", default="anthropic/claude-opus-4-7")
    optimize.add_argument("--run-dir", default="runs/gepa-demo")
    optimize.add_argument("--max-runtime-seconds", type=float, default=120.0)

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

    self_eval = subparsers.add_parser("self-eval", help="Run direct self-improvement eval cases without GEPA search.")
    self_eval.add_argument("--cases", required=True, help="YAML file containing eval cases.")
    self_eval.add_argument("--candidate", required=True, help="YAML or JSON candidate file.")
    self_eval.add_argument("--run-dir", default="runs/self-eval")
    self_eval.add_argument("--timeout-seconds", type=float, default=120.0)

    self_optimize = subparsers.add_parser("self-optimize", help="Run GEPA over self-improvement eval cases.")
    self_optimize.add_argument("--cases", required=True, help="YAML file containing eval cases.")
    self_optimize.add_argument("--candidate", required=True, help="YAML or JSON seed candidate file.")
    self_optimize.add_argument("--run-dir", default="runs/self-optimize")
    self_optimize.add_argument("--max-metric-calls", type=int, default=12)
    self_optimize.add_argument("--reflection-model", default="anthropic/claude-opus-4-7")
    self_optimize.add_argument("--timeout-seconds", type=float, default=120.0)
    self_optimize.add_argument("--objective", default="Improve the candidate so it scores higher on the eval suite.")
    self_optimize.add_argument(
        "--background",
        default="The candidate is a dict[str, str]. The evaluator returns numeric score plus Actionable Side Information.",
    )

    self_compare = subparsers.add_parser("self-compare", help="Compare two candidates on the same eval cases.")
    self_compare.add_argument("--cases", required=True, help="YAML file containing eval cases.")
    self_compare.add_argument("--baseline", required=True, help="YAML or JSON baseline candidate file.")
    self_compare.add_argument("--candidate", required=True, help="YAML or JSON comparison candidate file.")
    self_compare.add_argument("--run-dir", default="runs/self-compare")
    self_compare.add_argument("--timeout-seconds", type=float, default=120.0)

    self_show = subparsers.add_parser("self-show-candidate", help="Print a self-improvement candidate.")
    self_show.add_argument("--candidate", required=True, help="YAML or JSON candidate file.")
    self_show.add_argument("--pretty", action="store_true")

    eval_validation_parser = subparsers.add_parser(
        "eval-validation",
        help="Run OptimizeSpec workflow validation commands. Use `optimizespec eval-validation -- <command> ...`.",
    )
    eval_validation_parser.add_argument("eval_validation_args", nargs=argparse.REMAINDER)

    return parser


def require_api_key() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is required")


def cmd_eval_demo(run_dir: str, max_runtime_seconds: float) -> int:
    require_api_key()
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
    result = optimize_demo(
        max_metric_calls=max_metric_calls,
        reflection_model=reflection_model,
        run_dir=run_dir,
        max_runtime_seconds=max_runtime_seconds,
    )
    print(json.dumps(result.best_candidate, indent=2, sort_keys=True))
    return 0


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


def cmd_self_eval(cases_path: str, candidate_path: str, run_dir: str, timeout_seconds: float) -> int:
    cases = load_eval_cases(Path(cases_path))
    candidate = load_candidate(Path(candidate_path))
    payload = evaluate_candidate(
        candidate=candidate,
        cases=cases,
        executor=TemplateEchoExecutor(),
        run_dir=Path(run_dir),
        candidate_id="candidate",
        timeout_seconds=timeout_seconds,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_self_optimize(
    cases_path: str,
    candidate_path: str,
    run_dir: str,
    max_metric_calls: int,
    reflection_model: str,
    timeout_seconds: float,
    objective: str,
    background: str,
) -> int:
    cases = load_eval_cases(Path(cases_path))
    candidate = load_candidate(Path(candidate_path))
    result = optimize_candidate(
        seed_candidate=candidate,
        cases=cases,
        executor=TemplateEchoExecutor(),
        run_dir=Path(run_dir),
        objective=objective,
        background=background,
        reflection_model=reflection_model,
        max_metric_calls=max_metric_calls,
        timeout_seconds=timeout_seconds,
    )
    print(json.dumps(result.best_candidate, indent=2, sort_keys=True))
    return 0


def cmd_self_compare(
    cases_path: str,
    baseline_path: str,
    candidate_path: str,
    run_dir: str,
    timeout_seconds: float,
) -> int:
    cases = load_eval_cases(Path(cases_path))
    baseline = load_candidate(Path(baseline_path))
    candidate = load_candidate(Path(candidate_path))
    payload = compare_candidates(
        baseline=baseline,
        candidate=candidate,
        cases=cases,
        executor=TemplateEchoExecutor(),
        run_dir=Path(run_dir),
        timeout_seconds=timeout_seconds,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_self_show_candidate(candidate_path: str, pretty: bool) -> int:
    candidate = load_candidate(Path(candidate_path))
    print(json.dumps(candidate, indent=2 if pretty else None, sort_keys=pretty))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "eval-demo":
        return cmd_eval_demo(args.run_dir, args.max_runtime_seconds)
    if args.command == "optimize-demo":
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
    if args.command == "self-eval":
        return cmd_self_eval(args.cases, args.candidate, args.run_dir, args.timeout_seconds)
    if args.command == "self-optimize":
        return cmd_self_optimize(
            args.cases,
            args.candidate,
            args.run_dir,
            args.max_metric_calls,
            args.reflection_model,
            args.timeout_seconds,
            args.objective,
            args.background,
        )
    if args.command == "self-compare":
        return cmd_self_compare(args.cases, args.baseline, args.candidate, args.run_dir, args.timeout_seconds)
    if args.command == "self-show-candidate":
        return cmd_self_show_candidate(args.candidate, args.pretty)
    if args.command == "eval-validation":
        validation_args = list(args.eval_validation_args)
        if validation_args and validation_args[0] == "--":
            validation_args = validation_args[1:]
        return eval_validation.main(validation_args)

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
