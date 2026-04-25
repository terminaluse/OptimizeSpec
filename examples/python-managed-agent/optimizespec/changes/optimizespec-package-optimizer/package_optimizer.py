from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from optimizespec.self_improvement import (  # noqa: E402
    EvalCase,
    RolloutResult,
    ScoreResult,
    compare_candidates,
    evaluate_candidate,
    load_candidate,
    load_eval_cases,
    optimize_candidate,
)


CHANGE_DIR = Path(__file__).resolve().parent
DEFAULT_CASES = CHANGE_DIR / "eval-cases.yaml"
DEFAULT_CANDIDATE = CHANGE_DIR / "seed-candidate.yaml"
MUTABLE_FIELDS = [
    "package_summary",
    "eval_workflow",
    "rollout_lifecycle",
    "asi_guidance",
    "verification_guidance",
    "v1_limitations",
]


class PackageGuidanceExecutor:
    def run(self, candidate: dict[str, str], case: EvalCase, *, timeout_seconds: float) -> RolloutResult:
        started = time.monotonic()
        selected = select_fields(case)
        answer_parts = [candidate.get(field, "") for field in selected if candidate.get(field)]
        if not answer_parts:
            answer_parts = [candidate.get(field, "") for field in MUTABLE_FIELDS if candidate.get(field)]
        answer = "\n\n".join(answer_parts).strip()
        ended = time.monotonic()
        return RolloutResult(
            case_id=case.case_id,
            actual=answer,
            final_answer=answer,
            trajectory=[
                {
                    "action": "compose_package_guidance",
                    "input": case.input,
                    "selected_fields": selected,
                    "required_terms": required_terms(case),
                }
            ],
            runtime_ids={"executor": "package-guidance-fixture", "change_dir": str(CHANGE_DIR)},
            usage={
                "input_tokens": len(str(case.input).split()),
                "output_tokens": len(answer.split()),
            },
            started_at=started,
            ended_at=ended,
        )


def select_fields(case: EvalCase) -> list[str]:
    explicit = case.metadata.get("focus_fields")
    if isinstance(explicit, list) and explicit:
        return [str(item) for item in explicit]
    text = str(case.input).lower()
    fields: list[str] = []
    if "what" in text or "package" in text or "gepa" in text:
        fields.append("package_summary")
    if "run" in text or "command" in text or "candidate" in text:
        fields.append("eval_workflow")
    if "rollout" in text or "session" in text:
        fields.append("rollout_lifecycle")
    if "asi" in text or "side information" in text or "reflection" in text:
        fields.append("asi_guidance")
    if "verify" in text or "test" in text:
        fields.append("verification_guidance")
    if "limit" in text or "requirement" in text or "live" in text:
        fields.append("v1_limitations")
    return fields or list(MUTABLE_FIELDS)


def required_terms(case: EvalCase) -> list[str]:
    terms = case.metadata.get("required_terms", [])
    if not isinstance(terms, list):
        return []
    return [str(term) for term in terms]


def required_terms_scorer(case: EvalCase, rollout: RolloutResult) -> ScoreResult:
    terms = required_terms(case)
    actual = str(rollout.actual or "").lower()
    matched = [term for term in terms if term.lower() in actual]
    missing = [term for term in terms if term not in matched]
    score = len(matched) / max(len(terms), 1)
    if missing:
        feedback = f"Matched {len(matched)}/{len(terms)} required terms. Missing: {', '.join(missing)}."
    else:
        feedback = f"Matched all {len(terms)} required terms."
    return ScoreResult(
        score=score,
        feedback=feedback,
        subscores={
            "required_term_coverage": score,
            "matched_terms": float(len(matched)),
            "missing_terms": float(len(missing)),
        },
    )


def custom_scorers():
    return {"required_terms": required_terms_scorer}


def load_cases(path: str | Path = DEFAULT_CASES) -> list[EvalCase]:
    return load_eval_cases(Path(path))


def load_seed(path: str | Path = DEFAULT_CANDIDATE) -> dict[str, str]:
    return load_candidate(Path(path))


def cmd_show_candidate(path: str, pretty: bool) -> int:
    candidate = load_seed(path)
    print(json.dumps(candidate, indent=2 if pretty else None, sort_keys=pretty))
    return 0


def cmd_eval(cases_path: str, candidate_path: str, run_dir: str, timeout_seconds: float) -> int:
    payload = evaluate_candidate(
        candidate=load_seed(candidate_path),
        cases=load_cases(cases_path),
        executor=PackageGuidanceExecutor(),
        run_dir=Path(run_dir),
        mutable_fields=MUTABLE_FIELDS,
        custom_scorers=custom_scorers(),
        timeout_seconds=timeout_seconds,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_compare(cases_path: str, baseline_path: str, candidate_path: str, run_dir: str, timeout_seconds: float) -> int:
    payload = compare_candidates(
        baseline=load_seed(baseline_path),
        candidate=load_seed(candidate_path),
        cases=load_cases(cases_path),
        executor=PackageGuidanceExecutor(),
        run_dir=Path(run_dir),
        timeout_seconds=timeout_seconds,
        custom_scorers=custom_scorers(),
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_optimize(
    cases_path: str,
    candidate_path: str,
    run_dir: str,
    max_metric_calls: int,
    reflection_model: str,
    timeout_seconds: float,
) -> int:
    result = optimize_candidate(
        seed_candidate=load_seed(candidate_path),
        cases=load_cases(cases_path),
        executor=PackageGuidanceExecutor(),
        run_dir=Path(run_dir),
        objective=(
            "Improve package guidance for optimizespec so answers include required operational concepts, "
            "accurately describe GEPA rollouts, and preserve concise ASI-first workflow guidance."
        ),
        background=(
            "The candidate is a dict[str, str] with package_summary, eval_workflow, rollout_lifecycle, "
            "asi_guidance, verification_guidance, and v1_limitations. The evaluator composes answers "
            "from relevant fields and scores required-term coverage. Missing terms are reported in ASI."
        ),
        reflection_model=reflection_model,
        max_metric_calls=max_metric_calls,
        timeout_seconds=timeout_seconds,
        mutable_fields=MUTABLE_FIELDS,
        custom_scorers=custom_scorers(),
    )
    print(json.dumps(result.best_candidate, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="package_optimizer.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show = subparsers.add_parser("show-candidate")
    show.add_argument("--candidate", default=str(DEFAULT_CANDIDATE))
    show.add_argument("--pretty", action="store_true")

    direct_eval = subparsers.add_parser("eval")
    direct_eval.add_argument("--cases", default=str(DEFAULT_CASES))
    direct_eval.add_argument("--candidate", default=str(DEFAULT_CANDIDATE))
    direct_eval.add_argument("--run-dir", default="runs/package-optimizer/eval")
    direct_eval.add_argument("--timeout-seconds", type=float, default=120.0)

    compare = subparsers.add_parser("compare")
    compare.add_argument("--cases", default=str(DEFAULT_CASES))
    compare.add_argument("--baseline", default=str(DEFAULT_CANDIDATE))
    compare.add_argument("--candidate", default=str(DEFAULT_CANDIDATE))
    compare.add_argument("--run-dir", default="runs/package-optimizer/compare")
    compare.add_argument("--timeout-seconds", type=float, default=120.0)

    optimize = subparsers.add_parser("optimize")
    optimize.add_argument("--cases", default=str(DEFAULT_CASES))
    optimize.add_argument("--candidate", default=str(DEFAULT_CANDIDATE))
    optimize.add_argument("--run-dir", default="runs/package-optimizer/optimize")
    optimize.add_argument("--max-metric-calls", type=int, default=12)
    optimize.add_argument("--reflection-model", default="anthropic/claude-opus-4-7")
    optimize.add_argument("--timeout-seconds", type=float, default=120.0)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-candidate":
        return cmd_show_candidate(args.candidate, args.pretty)
    if args.command == "eval":
        return cmd_eval(args.cases, args.candidate, args.run_dir, args.timeout_seconds)
    if args.command == "compare":
        return cmd_compare(args.cases, args.baseline, args.candidate, args.run_dir, args.timeout_seconds)
    if args.command == "optimize":
        return cmd_optimize(
            args.cases,
            args.candidate,
            args.run_dir,
            args.max_metric_calls,
            args.reflection_model,
            args.timeout_seconds,
        )
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
