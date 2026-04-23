from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Sequence

import yaml


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from agent_gepa.self_improvement import (  # noqa: E402
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
DEFAULT_FIXTURE = ROOT / "gepa-evals" / "fixtures" / "agents" / "agent-gepa-managed-agent" / "agent.yaml"
MUTABLE_FIELDS = [
    "fixture_analysis_guidance",
    "proposal_generation_guidance",
    "design_generation_guidance",
    "spec_task_generation_guidance",
    "apply_generation_guidance",
    "scoring_asi_guidance",
]


def load_fixture(path: Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class ExistingAgentEvalGeneratorExecutor:
    def __init__(self, fixture_path: Path = DEFAULT_FIXTURE) -> None:
        self.fixture_path = fixture_path
        self.fixture = load_fixture(fixture_path)

    def run(self, candidate: dict[str, str], case: EvalCase, *, timeout_seconds: float) -> RolloutResult:
        started = time.monotonic()
        artifact_type = str(case.metadata.get("artifact_type", "proposal"))
        selected = select_fields(case, artifact_type)
        try:
            if artifact_type == "system_loop":
                generated, loop_trace = run_system_loop_smoke(case, timeout_seconds=timeout_seconds)
            else:
                generated = render_artifact(
                    artifact_type=artifact_type,
                    candidate=candidate,
                    selected_fields=selected,
                    fixture=self.fixture,
                )
                loop_trace = None
            errors: list[str] = []
        except Exception as exc:
            generated = ""
            errors = [str(exc)]
            loop_trace = None
        ended = time.monotonic()
        trajectory: list[dict[str, Any]] = [
            {
                "action": "generate_eval_artifact",
                "fixture": str(self.fixture_path.relative_to(ROOT)),
                "artifact_type": artifact_type,
                "selected_fields": selected,
                "required_terms": required_terms(case),
            }
        ]
        if loop_trace is not None:
            trajectory.append(loop_trace)
        return RolloutResult(
            case_id=case.case_id,
            actual=generated,
            final_answer=generated,
            trajectory=trajectory,
            runtime_ids={"executor": "existing-agent-eval-generator", "fixture": str(self.fixture_path)},
            usage={
                "input_tokens": len(str(case.input).split()),
                "output_tokens": len(generated.split()),
            },
            errors=errors,
            started_at=started,
            ended_at=ended,
        )


def select_fields(case: EvalCase, artifact_type: str) -> list[str]:
    explicit = case.metadata.get("focus_fields")
    if isinstance(explicit, list) and explicit:
        return [str(item) for item in explicit]
    mapping = {
        "proposal": ["fixture_analysis_guidance", "proposal_generation_guidance", "scoring_asi_guidance"],
        "design": ["fixture_analysis_guidance", "design_generation_guidance", "apply_generation_guidance"],
        "specs_tasks": ["spec_task_generation_guidance", "apply_generation_guidance"],
        "eval_cases": ["scoring_asi_guidance", "design_generation_guidance"],
        "apply_plan": ["apply_generation_guidance", "fixture_analysis_guidance"],
        "system_loop": ["apply_generation_guidance", "scoring_asi_guidance"],
    }
    return mapping.get(artifact_type, list(MUTABLE_FIELDS))


def source_file_text(fixture: dict[str, Any]) -> str:
    source_files = fixture.get("source_files", {})
    return ", ".join(str(path) for path in source_files.values())


def candidate_fields_text(fixture: dict[str, Any]) -> str:
    return ", ".join(str(item) for item in fixture.get("candidate_fields", []))


def commands_text(fixture: dict[str, Any]) -> str:
    commands = fixture.get("existing_commands", {})
    return ", ".join(str(command) for command in commands.values())


def render_artifact(
    *,
    artifact_type: str,
    candidate: dict[str, str],
    selected_fields: list[str],
    fixture: dict[str, Any],
) -> str:
    guidance = "\n\n".join(candidate.get(field, "") for field in selected_fields if candidate.get(field))
    if artifact_type == "proposal":
        return f"""## Target Agent

The target is {fixture['name']}, a {fixture['runtime']} fixture. Source files: {source_file_text(fixture)}.

## Candidate Surface

The GEPA candidate is dict[str, str] with fields {candidate_fields_text(fixture)}.

## Scoring

Use numeric scoring from 0.0 to 1.0 plus qualitative rubric review. Every rollout emits ASI.

## Guidance

{guidance}
"""
    if artifact_type == "design":
        return f"""## Runtime Discovery

Use ManagedAgentRuntime from src/agent_gepa/runtime.py, ManagedAgentEvaluator from src/agent_gepa/evaluator.py, and optimize_demo from src/agent_gepa/optimizer.py.

## Invocation

Existing references: {commands_text(fixture)}. Generated operations should cover eval-demo, optimize-demo, compare-demo, and show-seed, mapped to direct eval, optimize, compare, and show candidate.

## Rollout Lifecycle

One rollout is candidate plus eval case through a Managed Agent session. Capture trace capture data, score the result, build side_info and ASI, persist artifacts, then cleanup.

## Guidance

{guidance}
"""
    if artifact_type == "specs_tasks":
        return f"""## Requirements and Tasks

Specs SHALL cover candidate surface, eval dataset, scorer, Managed Agent runner, ASI, GEPA optimization, apply skill, validation, direct eval, and compare.

Tasks SHALL implement schemas, runner, scorer, field-specific ASI, GEPA optimize, compare, and verification.

## Guidance

{guidance}
"""
    if artifact_type == "eval_cases":
        return f"""cases:
  - id: file-transform-success
    split: train
    scorer: exact_match
    expected: file-transform tasks
  - id: structured-candidate-validity
    split: train
    scorer: structured candidate validity
  - id: runtime-failure-asi
    split: val
    scorer: runtime failure

Each case must define score, side_info, field-specific ASI, train and val splits.

## Guidance

{guidance}
"""
    if artifact_type == "apply_plan":
        return f"""## Apply Plan

Reuse ManagedAgentRuntime and reuse ManagedAgentEvaluator. Wire GEPA optimize_anything through the existing evaluator and optimizer patterns.

Expose direct eval, optimize, compare, and show candidate operations. Live Managed Agents require ANTHROPIC_API_KEY. Unsupported runtimes must be blocked.

## Guidance

{guidance}
"""
    return guidance


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
    feedback = (
        f"Matched all {len(terms)} required terms."
        if not missing
        else f"Matched {len(matched)}/{len(terms)} required terms. Missing: {', '.join(missing)}."
    )
    return ScoreResult(
        score=score,
        feedback=feedback,
        subscores={
            "required_term_coverage": score,
            "matched_terms": float(len(matched)),
            "missing_terms": float(len(missing)),
        },
    )


def system_loop_success_scorer(case: EvalCase, rollout: RolloutResult) -> ScoreResult:
    actual = str(rollout.actual or "")
    success = "SYSTEM_LOOP_SUCCESS" in actual and not rollout.errors
    return ScoreResult(
        score=1.0 if success else 0.0,
        feedback="System loop completed." if success else "System loop did not complete.",
        subscores={"system_loop_success": 1.0 if success else 0.0},
    )


def custom_scorers():
    return {
        "required_terms": required_terms_scorer,
        "system_loop_success": system_loop_success_scorer,
    }


def write_reduced_cases(path: Path) -> None:
    payload = yaml.safe_load(DEFAULT_CASES.read_text(encoding="utf-8"))
    cases = payload.get("cases", [])
    reduced = [
        case
        for case in cases
        if case.get("metadata", {}).get("artifact_type") != "system_loop"
        and case.get("id") in {"proposal-for-existing-agent", "generated-apply-plan"}
    ]
    path.write_text(yaml.safe_dump({"cases": reduced}, sort_keys=False), encoding="utf-8")


def run_command(args: list[str], *, timeout_seconds: float) -> dict[str, Any]:
    started = time.monotonic()
    completed = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
    )
    return {
        "args": args,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
        "elapsed_seconds": time.monotonic() - started,
    }


def run_system_loop_smoke(case: EvalCase, *, timeout_seconds: float) -> tuple[str, dict[str, Any]]:
    stamp = f"{case.case_id}-{int(time.time() * 1000)}"
    work_dir = ROOT / "runs" / "agent-eval-generator" / "system-loop-smoke" / stamp
    work_dir.mkdir(parents=True, exist_ok=True)
    reduced_cases = work_dir / "cases.yaml"
    write_reduced_cases(reduced_cases)

    script = Path(__file__).resolve()
    command_timeout = max(timeout_seconds / 3.0, 10.0)
    # Keep command construction explicit so command summaries are easy to inspect in ASI.
    generate_args = [
        sys.executable,
        str(script),
        "generate",
        "--output-dir",
        str(work_dir / "generated"),
    ]
    eval_args = [
        sys.executable,
        str(script),
        "eval",
        "--cases",
        str(reduced_cases),
        "--run-dir",
        str(work_dir / "eval"),
    ]
    optimize_args = [
        sys.executable,
        str(script),
        "optimize",
        "--cases",
        str(reduced_cases),
        "--max-metric-calls",
        "1",
        "--run-dir",
        str(work_dir / "optimize"),
    ]
    command_results = [
        run_command(generate_args, timeout_seconds=command_timeout),
        run_command(eval_args, timeout_seconds=command_timeout),
        run_command(optimize_args, timeout_seconds=command_timeout),
    ]
    expected_files = [
        work_dir / "generated" / "proposal.md",
        work_dir / "generated" / "design.md",
        work_dir / "eval" / "summary.json",
        work_dir / "optimize" / "candidates.json",
        work_dir / "optimize" / "run_log.txt",
    ]
    missing = [str(path.relative_to(ROOT)) for path in expected_files if not path.exists()]
    failed = [result for result in command_results if result["returncode"] != 0]
    success = not missing and not failed
    summary = {
        "action": "run_actual_system_loop",
        "work_dir": str(work_dir.relative_to(ROOT)),
        "commands": command_results,
        "missing_files": missing,
        "success": success,
    }
    marker = "SYSTEM_LOOP_SUCCESS" if success else "SYSTEM_LOOP_FAILURE"
    text = (
        f"{marker}\n"
        f"generate: {command_results[0]['returncode']}\n"
        f"eval: {command_results[1]['returncode']}\n"
        f"optimize: {command_results[2]['returncode']}\n"
        f"work_dir: {work_dir.relative_to(ROOT)}\n"
        f"required_artifacts: proposal.md, design.md, summary.json, candidates.json, run_log.txt\n"
        f"missing: {missing}\n"
    )
    return text, summary


def load_cases(path: str | Path = DEFAULT_CASES) -> list[EvalCase]:
    return load_eval_cases(Path(path))


def load_seed(path: str | Path = DEFAULT_CANDIDATE) -> dict[str, str]:
    return load_candidate(Path(path))


def generate_artifacts(output_dir: Path, candidate: dict[str, str] | None = None) -> dict[str, str]:
    active_candidate = candidate or load_seed()
    fixture = load_fixture()
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered = {
        "proposal.md": render_artifact(
            artifact_type="proposal",
            candidate=active_candidate,
            selected_fields=["fixture_analysis_guidance", "proposal_generation_guidance", "scoring_asi_guidance"],
            fixture=fixture,
        ),
        "design.md": render_artifact(
            artifact_type="design",
            candidate=active_candidate,
            selected_fields=["fixture_analysis_guidance", "design_generation_guidance", "apply_generation_guidance"],
            fixture=fixture,
        ),
        "specs/meta-eval-spec.md": render_artifact(
            artifact_type="specs_tasks",
            candidate=active_candidate,
            selected_fields=["spec_task_generation_guidance", "apply_generation_guidance"],
            fixture=fixture,
        ),
        "tasks.md": render_artifact(
            artifact_type="specs_tasks",
            candidate=active_candidate,
            selected_fields=["spec_task_generation_guidance", "apply_generation_guidance"],
            fixture=fixture,
        ),
        "eval-cases.yaml": render_artifact(
            artifact_type="eval_cases",
            candidate=active_candidate,
            selected_fields=["scoring_asi_guidance", "design_generation_guidance"],
            fixture=fixture,
        ),
        "apply-plan.md": render_artifact(
            artifact_type="apply_plan",
            candidate=active_candidate,
            selected_fields=["apply_generation_guidance", "fixture_analysis_guidance"],
            fixture=fixture,
        ),
    }
    for relative, text in rendered.items():
        path = output_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return rendered


def cmd_show_candidate(path: str, pretty: bool) -> int:
    candidate = load_seed(path)
    print(json.dumps(candidate, indent=2 if pretty else None, sort_keys=pretty))
    return 0


def cmd_generate(candidate_path: str, output_dir: str) -> int:
    rendered = generate_artifacts(Path(output_dir), load_seed(candidate_path))
    print(json.dumps({"output_dir": output_dir, "files": sorted(rendered)}, indent=2, sort_keys=True))
    return 0


def cmd_eval(cases_path: str, candidate_path: str, run_dir: str, timeout_seconds: float) -> int:
    payload = evaluate_candidate(
        candidate=load_seed(candidate_path),
        cases=load_cases(cases_path),
        executor=ExistingAgentEvalGeneratorExecutor(),
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
        executor=ExistingAgentEvalGeneratorExecutor(),
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
        executor=ExistingAgentEvalGeneratorExecutor(),
        run_dir=Path(run_dir),
        objective=(
            "Improve guidance for generating eval and optimizer artifacts for the existing agent-gepa "
            "Claude Managed Agent prototype."
        ),
        background=(
            "The fixture is this repo's existing ManagedAgentRuntime, ManagedAgentEvaluator, and optimize_demo path. "
            "The candidate fields guide proposal, design, spec/task, apply, scoring, and ASI artifact generation."
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
    parser = argparse.ArgumentParser(prog="agent_eval_generator.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show = subparsers.add_parser("show-candidate")
    show.add_argument("--candidate", default=str(DEFAULT_CANDIDATE))
    show.add_argument("--pretty", action="store_true")

    generate = subparsers.add_parser("generate")
    generate.add_argument("--candidate", default=str(DEFAULT_CANDIDATE))
    generate.add_argument("--output-dir", default="runs/agent-eval-generator/generated")

    direct_eval = subparsers.add_parser("eval")
    direct_eval.add_argument("--cases", default=str(DEFAULT_CASES))
    direct_eval.add_argument("--candidate", default=str(DEFAULT_CANDIDATE))
    direct_eval.add_argument("--run-dir", default="runs/agent-eval-generator/eval")
    direct_eval.add_argument("--timeout-seconds", type=float, default=120.0)

    compare = subparsers.add_parser("compare")
    compare.add_argument("--cases", default=str(DEFAULT_CASES))
    compare.add_argument("--baseline", default=str(DEFAULT_CANDIDATE))
    compare.add_argument("--candidate", default=str(DEFAULT_CANDIDATE))
    compare.add_argument("--run-dir", default="runs/agent-eval-generator/compare")
    compare.add_argument("--timeout-seconds", type=float, default=120.0)

    optimize = subparsers.add_parser("optimize")
    optimize.add_argument("--cases", default=str(DEFAULT_CASES))
    optimize.add_argument("--candidate", default=str(DEFAULT_CANDIDATE))
    optimize.add_argument("--run-dir", default="runs/agent-eval-generator/optimize")
    optimize.add_argument("--max-metric-calls", type=int, default=12)
    optimize.add_argument("--reflection-model", default="anthropic/claude-opus-4-7")
    optimize.add_argument("--timeout-seconds", type=float, default=120.0)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show-candidate":
        return cmd_show_candidate(args.candidate, args.pretty)
    if args.command == "generate":
        return cmd_generate(args.candidate, args.output_dir)
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
