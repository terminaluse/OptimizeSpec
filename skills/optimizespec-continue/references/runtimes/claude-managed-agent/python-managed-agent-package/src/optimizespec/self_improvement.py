from __future__ import annotations

from dataclasses import dataclass, field
from difflib import unified_diff
import json
from pathlib import Path
from statistics import mean
from typing import Any, Callable, Literal, Protocol

import gepa.optimize_anything as oa
from gepa.optimize_anything import EngineConfig, GEPAConfig, ReflectionConfig
import yaml


ScoreType = Literal["exact_match", "json_match", "file_exists", "custom"]
Split = Literal["train", "val", "test"]


@dataclass(frozen=True)
class ScorerSpec:
    type: ScoreType = "exact_match"
    expected: Any | None = None
    rubric: str | None = None


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    input: Any
    expected: Any | None = None
    expected_shape: str | None = None
    rubric: str | None = None
    scorer: ScorerSpec = field(default_factory=ScorerSpec)
    split: Split = "train"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RolloutResult:
    case_id: str
    actual: Any | None
    status: str = "completed"
    final_answer: str | None = None
    generated_files: dict[str, str] = field(default_factory=dict)
    trajectory: list[dict[str, Any]] = field(default_factory=list)
    tool_activity: list[dict[str, Any]] = field(default_factory=list)
    runtime_ids: dict[str, Any] = field(default_factory=dict)
    runtime_metadata: dict[str, Any] = field(default_factory=dict)
    usage: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    cleanup_warnings: list[str] = field(default_factory=list)
    timeout_seconds: float | None = None
    timed_out: bool = False
    interrupted: bool = False
    started_at: float | None = None
    ended_at: float | None = None


@dataclass(frozen=True)
class ScoreResult:
    score: float
    feedback: str
    subscores: dict[str, float] = field(default_factory=dict)


class RolloutExecutor(Protocol):
    def run(self, candidate: dict[str, str], case: EvalCase, *, timeout_seconds: float) -> RolloutResult:
        ...


def load_yaml_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_candidate(path: Path) -> dict[str, str]:
    payload = load_yaml_file(path) if path.suffix in {".yaml", ".yml"} else json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"candidate file must contain a mapping: {path}")
    candidate: dict[str, str] = {}
    for key, value in payload.items():
        if value is None:
            candidate[str(key)] = ""
        elif isinstance(value, str):
            candidate[str(key)] = value
        else:
            candidate[str(key)] = yaml.safe_dump(value, sort_keys=False)
    return candidate


def load_eval_cases(path: Path) -> list[EvalCase]:
    payload = load_yaml_file(path)
    raw_cases = payload.get("cases", payload) if isinstance(payload, dict) else payload
    if not isinstance(raw_cases, list):
        raise ValueError("eval cases file must contain a list or a mapping with a `cases` list")
    return [parse_eval_case(item) for item in raw_cases]


def parse_eval_case(payload: dict[str, Any]) -> EvalCase:
    if not isinstance(payload, dict):
        raise ValueError("each eval case must be a mapping")
    case_id = str(payload.get("id") or payload.get("case_id") or "").strip()
    if not case_id:
        raise ValueError("eval case is missing `id`")
    scorer_payload = payload.get("scorer") or {}
    if not isinstance(scorer_payload, dict):
        raise ValueError(f"eval case {case_id} has invalid scorer")
    scorer = ScorerSpec(
        type=scorer_payload.get("type", "exact_match"),
        expected=scorer_payload.get("expected", payload.get("expected")),
        rubric=scorer_payload.get("rubric", payload.get("rubric")),
    )
    split = payload.get("split", "train")
    if split not in {"train", "val", "test"}:
        raise ValueError(f"eval case {case_id} has unsupported split {split!r}")
    metadata = dict(payload.get("metadata") or {})
    for optional_key in ("criteria", "grader", "acceptance"):
        if optional_key in payload and optional_key not in metadata:
            metadata[optional_key] = payload[optional_key]
    return EvalCase(
        case_id=case_id,
        input=payload.get("input"),
        expected=payload.get("expected", scorer.expected),
        expected_shape=payload.get("expected_shape"),
        rubric=payload.get("rubric", scorer.rubric),
        scorer=scorer,
        split=split,
        metadata=metadata,
    )


def split_cases(cases: list[EvalCase]) -> tuple[list[EvalCase], list[EvalCase]]:
    train = [case for case in cases if case.split == "train"]
    val = [case for case in cases if case.split == "val"]
    if not train and cases:
        train = list(cases)
    return train, val


def score_rollout(case: EvalCase, rollout: RolloutResult, custom_scorers: dict[str, Callable[[EvalCase, RolloutResult], ScoreResult]] | None = None) -> ScoreResult:
    scorer = case.scorer
    actual = rollout.actual if rollout.actual is not None else rollout.final_answer
    expected = scorer.expected if scorer.expected is not None else case.expected

    if rollout.errors:
        return ScoreResult(score=0.0, feedback=f"Rollout failed: {'; '.join(rollout.errors)}")

    if scorer.type == "exact_match":
        score = 1.0 if str(actual) == str(expected) else 0.0
        return ScoreResult(
            score=score,
            feedback="Exact match." if score == 1.0 else f"Expected {expected!r}, got {actual!r}.",
            subscores={"correctness": score},
        )

    if scorer.type == "json_match":
        try:
            actual_json = actual if not isinstance(actual, str) else json.loads(actual)
            expected_json = expected if not isinstance(expected, str) else json.loads(expected)
        except Exception as exc:
            return ScoreResult(score=0.0, feedback=f"JSON parse failure: {exc}", subscores={"correctness": 0.0})
        score = 1.0 if actual_json == expected_json else 0.0
        return ScoreResult(
            score=score,
            feedback="JSON matched." if score == 1.0 else f"Expected JSON {expected_json!r}, got {actual_json!r}.",
            subscores={"correctness": score},
        )

    if scorer.type == "file_exists":
        target = str(expected or case.expected_shape or "").strip()
        exists = bool(target and target in rollout.generated_files)
        score = 1.0 if exists else 0.0
        return ScoreResult(
            score=score,
            feedback=f"File {target!r} exists." if exists else f"File {target!r} was not generated.",
            subscores={"file_exists": score},
        )

    if scorer.type == "custom":
        scorer_name = str(expected or case.metadata.get("custom_scorer") or "").strip()
        if custom_scorers and scorer_name in custom_scorers:
            return custom_scorers[scorer_name](case, rollout)
        return ScoreResult(score=0.0, feedback=f"Custom scorer {scorer_name!r} is not registered.")

    raise ValueError(f"unsupported scorer type: {scorer.type}")


def build_asi(
    *,
    case: EvalCase,
    candidate: dict[str, str],
    rollout: RolloutResult,
    score: ScoreResult,
    mutable_fields: list[str] | None = None,
) -> dict[str, Any]:
    elapsed = None
    if rollout.started_at is not None and rollout.ended_at is not None:
        elapsed = max(rollout.ended_at - rollout.started_at, 0.0)
    token_total = int(rollout.usage.get("input_tokens", 0) or 0) + int(rollout.usage.get("output_tokens", 0) or 0)
    scores = {
        "correctness": score.score,
        **score.subscores,
        "latency_inv": 1.0 / max(elapsed or 0.0, 0.001),
        "cost_inv": 1.0 / max(token_total, 1),
    }
    side_info: dict[str, Any] = {
        "Input": case.input,
        "Expected": case.expected if case.expected is not None else case.expected_shape,
        "Actual": rollout.actual if rollout.actual is not None else rollout.final_answer,
        "Feedback": score.feedback,
        "Error": rollout.errors or None,
        "Agent Trajectory": rollout.trajectory,
        "Runtime": {
            "setup_error": "; ".join(rollout.errors) if rollout.errors and not rollout.actual else None,
            "case_id": case.case_id,
            "runtime_ids": rollout.runtime_ids,
            "runtime_metadata": rollout.runtime_metadata,
            "usage": rollout.usage,
            "generated_files": sorted(rollout.generated_files),
            "elapsed_seconds": elapsed,
            "timeout": {
                "configured_seconds": rollout.timeout_seconds,
                "timed_out": rollout.timed_out,
                "interrupted": rollout.interrupted,
            },
            "cleanup": {
                "status": "completed" if not rollout.cleanup_warnings else "partial",
                "warnings": rollout.cleanup_warnings,
            },
        },
        "scores": scores,
    }
    for field_name in mutable_fields or sorted(candidate):
        side_info[f"{field_name}_specific_info"] = {
            "Current Value": candidate.get(field_name),
            "Feedback": infer_field_feedback(field_name, score, rollout),
            "scores": {"case_score": score.score},
        }
    return side_info


def infer_field_feedback(field_name: str, score: ScoreResult, rollout: RolloutResult) -> str:
    if rollout.errors:
        if any(term in field_name for term in ("environment", "skill", "tool", "resource", "subagent")):
            return "Runtime configuration may be invalid or insufficient for this eval case."
        return "The candidate should make failure handling and task completion more explicit."
    if score.score >= 1.0:
        return "This field did not prevent success on this case; preserve useful behavior."
    if "prompt" in field_name or "instruction" in field_name:
        return "Clarify task constraints, output format, and verification steps for this case."
    if "scorer" in field_name or "rubric" in field_name:
        return "Align the scorer or rubric with the expected output and qualitative judgement."
    if any(term in field_name for term in ("environment", "skill", "tool", "resource", "subagent")):
        return "Check whether runtime capabilities or helper guidance are missing for this case."
    return "Use the top-level feedback to decide whether this field should change."


def persist_rollout(
    *,
    run_dir: Path,
    candidate_id: str,
    case: EvalCase,
    candidate: dict[str, str],
    rollout: RolloutResult,
    score: ScoreResult,
    side_info: dict[str, Any],
) -> None:
    out_dir = run_dir / "rollouts" / candidate_id / case.case_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "candidate.json").write_text(json.dumps(candidate, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "score.json").write_text(
        json.dumps(
            {
                "candidate_id": candidate_id,
                "eval_case_id": case.case_id,
                "score": score.score,
                "feedback": score.feedback,
                "subscores": score.subscores,
                "rollout_evidence_path": "rollout.json",
                "side_info_path": "side_info.json",
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    (out_dir / "side_info.json").write_text(json.dumps(side_info, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "rollout.json").write_text(
        json.dumps(build_runtime_neutral_rollout_record(candidate_id, case, rollout), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def build_runtime_neutral_rollout_record(
    candidate_id: str,
    case: EvalCase,
    rollout: RolloutResult,
) -> dict[str, Any]:
    cleanup_warnings = list(rollout.cleanup_warnings)
    return {
        "candidate_id": candidate_id,
        "eval_case_id": case.case_id,
        "status": rollout.status if not rollout.timed_out else "timeout",
        "final_output": rollout.actual if rollout.actual is not None else rollout.final_answer,
        "trace_summary": rollout.trajectory,
        "tool_activity": rollout.tool_activity,
        "usage": rollout.usage,
        "errors": rollout.errors,
        "timeout": {
            "configured_seconds": rollout.timeout_seconds,
            "timed_out": rollout.timed_out,
            "interrupted": rollout.interrupted,
        },
        "cleanup": {
            "status": "completed" if not cleanup_warnings else "partial",
            "warnings": cleanup_warnings,
        },
        "timestamps": {
            "started_at": rollout.started_at,
            "ended_at": rollout.ended_at,
        },
        "score_inputs": {
            "expected_output": case.expected if case.expected is not None else case.expected_shape,
            "final_output_ref": "rollout.json#final_output",
            "trace_ref": "rollout.json#trace_summary",
            "runtime_metadata_ref": "rollout.json#runtime_metadata",
            "side_info_ref": "side_info.json",
        },
        "runtime_metadata": {
            "runtime_ids": rollout.runtime_ids,
            "generated_files": rollout.generated_files,
            **rollout.runtime_metadata,
        },
    }


def evaluate_candidate(
    *,
    candidate: dict[str, str],
    cases: list[EvalCase],
    executor: RolloutExecutor,
    run_dir: Path,
    candidate_id: str = "candidate",
    timeout_seconds: float = 120.0,
    mutable_fields: list[str] | None = None,
    custom_scorers: dict[str, Callable[[EvalCase, RolloutResult], ScoreResult]] | None = None,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for case in cases:
        rollout = executor.run(candidate, case, timeout_seconds=timeout_seconds)
        score = score_rollout(case, rollout, custom_scorers=custom_scorers)
        side_info = build_asi(case=case, candidate=candidate, rollout=rollout, score=score, mutable_fields=mutable_fields)
        persist_rollout(
            run_dir=run_dir,
            candidate_id=candidate_id,
            case=case,
            candidate=candidate,
            rollout=rollout,
            score=score,
            side_info=side_info,
        )
        results.append(
            {
                "case_id": case.case_id,
                "split": case.split,
                "score": score.score,
                "feedback": score.feedback,
                "actual": side_info["Actual"],
                "expected": side_info["Expected"],
                "errors": rollout.errors,
            }
        )
    split_scores: dict[str, list[float]] = {"train": [], "val": [], "test": []}
    for item in results:
        split_scores[str(item["split"])].append(float(item["score"]))
    summary = {
        "mean_score": mean([float(item["score"]) for item in results]) if results else 0.0,
        "mean_train_score": mean(split_scores["train"]) if split_scores["train"] else 0.0,
        "mean_val_score": mean(split_scores["val"]) if split_scores["val"] else 0.0,
        "mean_test_score": mean(split_scores["test"]) if split_scores["test"] else 0.0,
        "cases": results,
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


class GEPAEvaluator:
    def __init__(
        self,
        *,
        executor: RolloutExecutor,
        run_dir: Path,
        mutable_fields: list[str] | None = None,
        timeout_seconds: float = 120.0,
        custom_scorers: dict[str, Callable[[EvalCase, RolloutResult], ScoreResult]] | None = None,
    ) -> None:
        self.executor = executor
        self.run_dir = run_dir
        self.mutable_fields = mutable_fields
        self.timeout_seconds = timeout_seconds
        self.custom_scorers = custom_scorers

    def __call__(self, candidate: dict[str, str], example: EvalCase | None = None, **_: Any) -> tuple[float, dict[str, Any]]:
        if example is None:
            raise ValueError("GEPAEvaluator requires an EvalCase example")
        rollout = self.executor.run(candidate, example, timeout_seconds=self.timeout_seconds)
        score = score_rollout(example, rollout, custom_scorers=self.custom_scorers)
        side_info = build_asi(
            case=example,
            candidate=candidate,
            rollout=rollout,
            score=score,
            mutable_fields=self.mutable_fields,
        )
        persist_rollout(
            run_dir=self.run_dir,
            candidate_id=stable_candidate_id(candidate),
            case=example,
            candidate=candidate,
            rollout=rollout,
            score=score,
            side_info=side_info,
        )
        return score.score, side_info


def optimize_candidate(
    *,
    seed_candidate: dict[str, str],
    cases: list[EvalCase],
    executor: RolloutExecutor,
    run_dir: Path,
    objective: str,
    background: str,
    reflection_model: str = "anthropic/claude-opus-4-7",
    max_metric_calls: int = 48,
    timeout_seconds: float = 120.0,
    mutable_fields: list[str] | None = None,
    reflection_prompt_template: dict[str, str] | None = None,
    module_selector: Any = "round_robin",
    custom_scorers: dict[str, Callable[[EvalCase, RolloutResult], ScoreResult]] | None = None,
):
    train, val = split_cases(cases)
    evaluator = GEPAEvaluator(
        executor=executor,
        run_dir=run_dir,
        mutable_fields=mutable_fields,
        timeout_seconds=timeout_seconds,
        custom_scorers=custom_scorers,
    )
    config = GEPAConfig(
        engine=EngineConfig(max_metric_calls=max_metric_calls, run_dir=str(run_dir), capture_stdio=True),
        reflection=ReflectionConfig(
            reflection_lm=reflection_model,
            module_selector=module_selector,
            reflection_prompt_template=reflection_prompt_template,
        ),
    )
    return oa.optimize_anything(
        seed_candidate=dict(seed_candidate),
        evaluator=evaluator,
        dataset=train,
        valset=val or None,
        objective=objective,
        background=background,
        config=config,
    )


def compare_candidates(
    *,
    baseline: dict[str, str],
    candidate: dict[str, str],
    cases: list[EvalCase],
    executor: RolloutExecutor,
    run_dir: Path,
    timeout_seconds: float = 120.0,
    custom_scorers: dict[str, Callable[[EvalCase, RolloutResult], ScoreResult]] | None = None,
) -> dict[str, Any]:
    baseline_eval = evaluate_candidate(
        candidate=baseline,
        cases=cases,
        executor=executor,
        run_dir=run_dir / "baseline",
        candidate_id="baseline",
        timeout_seconds=timeout_seconds,
        custom_scorers=custom_scorers,
    )
    candidate_eval = evaluate_candidate(
        candidate=candidate,
        cases=cases,
        executor=executor,
        run_dir=run_dir / "candidate",
        candidate_id="candidate",
        timeout_seconds=timeout_seconds,
        custom_scorers=custom_scorers,
    )
    baseline_by_case = {item["case_id"]: item for item in baseline_eval["cases"]}
    candidate_by_case = {item["case_id"]: item for item in candidate_eval["cases"]}
    deltas = []
    for case_id in sorted(set(baseline_by_case) | set(candidate_by_case)):
        before = baseline_by_case.get(case_id, {})
        after = candidate_by_case.get(case_id, {})
        before_score = float(before.get("score", 0.0) or 0.0)
        after_score = float(after.get("score", 0.0) or 0.0)
        deltas.append(
            {
                "case_id": case_id,
                "baseline_score": before_score,
                "candidate_score": after_score,
                "delta": after_score - before_score,
                "baseline_actual": before.get("actual"),
                "candidate_actual": after.get("actual"),
                "expected": after.get("expected") or before.get("expected"),
            }
        )
    payload = {
        "baseline": baseline_eval,
        "candidate": candidate_eval,
        "candidate_diff": diff_candidates(baseline, candidate),
        "deltas": deltas,
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "comparison.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def diff_candidates(before: dict[str, str], after: dict[str, str]) -> dict[str, str]:
    diffs: dict[str, str] = {}
    for key in sorted(set(before) | set(after)):
        if before.get(key) == after.get(key):
            continue
        diffs[key] = "\n".join(
            unified_diff(
                before.get(key, "").splitlines(),
                after.get(key, "").splitlines(),
                fromfile=f"before/{key}",
                tofile=f"after/{key}",
                lineterm="",
            )
        )
    return diffs


def stable_candidate_id(candidate: dict[str, str]) -> str:
    import hashlib

    payload = json.dumps(candidate, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
