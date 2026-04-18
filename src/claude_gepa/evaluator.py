from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import traceback
from typing import Any

import gepa.optimize_anything as oa

from .candidate import CandidateBundle
from .runtime import ManagedAgentRuntime, RunArtifacts
from .tasks import DummyTask


@dataclass(frozen=True)
class EvaluationResult:
    score: float
    side_info: dict[str, Any]


def compute_text_match_score(expected: str, actual: str | None) -> float:
    if actual is None:
        return 0.0
    return 1.0 if actual.strip() == expected.strip() else 0.0


class ManagedAgentEvaluator:
    def __init__(
        self,
        *,
        run_dir: Path | None = None,
        runtime: ManagedAgentRuntime | None = None,
        use_outcomes: bool = True,
        max_runtime_seconds: float = 45.0,
    ) -> None:
        self.runtime = runtime or ManagedAgentRuntime()
        self.run_dir = run_dir or Path("runs") / "latest"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.use_outcomes = use_outcomes
        self.max_runtime_seconds = max_runtime_seconds

    def __call__(
        self,
        candidate: dict[str, str] | str,
        example: DummyTask | None = None,
        optimization_state: Any | None = None,
        **_: Any,
    ) -> tuple[float, dict[str, Any]]:
        if example is None:
            raise ValueError("ManagedAgentEvaluator requires a task example")

        bundle = CandidateBundle.from_candidate(candidate)
        _safe_oa_log(f"Evaluating candidate={bundle.candidate_id} task={example.task_id}")
        if optimization_state is not None:
            _safe_oa_log("OptimizationState provided to evaluator")

        artifacts: RunArtifacts | None = None
        try:
            artifacts = self.runtime.run_task(
                bundle,
                example,
                use_outcomes=self.use_outcomes,
                max_runtime_seconds=self.max_runtime_seconds,
            )
            score = compute_text_match_score(example.expected_output, artifacts.output_text)
            side_info = build_side_info(example, bundle, artifacts, score)
        except Exception as exc:
            score = 0.0
            side_info = {
                "candidate_id": bundle.candidate_id,
                "task_id": example.task_id,
                "expected_output": example.expected_output,
                "actual_output": None,
                "errors": [str(exc)],
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc(),
                "field_feedback": {
                    "system_prompt": "Tighten the system prompt to reduce runtime mistakes.",
                    "task_prompt": "Make required file paths and completion criteria more explicit.",
                    "outcome_rubric": "Simplify the rubric if the outcome path is unsupported or unstable.",
                    "skills": "Remove non-essential skills while debugging runtime failures.",
                    "environment_spec": "Reduce environment complexity and network/package requirements first.",
                    "subagent_specs": "Keep subagent specs empty unless multi-agent support is confirmed.",
                },
                "scores": {
                    "task_success": 0.0,
                    "outcome_success": 0.0,
                    "latency_inv": 0.0,
                    "cost_inv": 0.0,
                },
                "runtime": {},
            }
        self._persist_run(bundle, example, artifacts, side_info)
        return score, side_info

    def _persist_run(
        self,
        bundle: CandidateBundle,
        task: DummyTask,
        artifacts: RunArtifacts | None,
        side_info: dict[str, Any],
    ) -> None:
        out_dir = self.run_dir / bundle.candidate_id / task.task_id
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "candidate.json").write_text(
            json.dumps(bundle.fields, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (out_dir / "side_info.json").write_text(
            json.dumps(side_info, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        if artifacts is not None and artifacts.output_text is not None:
            (out_dir / "result.txt").write_text(artifacts.output_text, encoding="utf-8")


def _safe_oa_log(message: str) -> None:
    try:
        oa.get_log_context()
    except RuntimeError:
        return
    oa.log(message)


def build_side_info(
    task: DummyTask,
    bundle: CandidateBundle,
    artifacts: RunArtifacts,
    score: float,
) -> dict[str, Any]:
    latency_proxy = 1.0 / max(len(artifacts.event_types), 1)
    token_total = artifacts.usage["input_tokens"] + artifacts.usage["output_tokens"]
    cost_inv = 1.0 / max(token_total, 1)

    field_feedback = {
        "system_prompt": "The system prompt should reinforce careful file-writing behavior.",
        "task_prompt": "The task prompt should make the input path and required output path unambiguous.",
        "outcome_rubric": "The rubric should emphasize file creation and exact final output formatting.",
        "skills": "Keep skills empty unless they add clear value for the current benchmark.",
        "environment_spec": "The environment should stay minimal unless a task requires packages or network access.",
        "subagent_specs": "Keep subagent specs empty unless multi-agent delegation is beneficial and available.",
    }

    return {
        "candidate_id": bundle.candidate_id,
        "task_id": task.task_id,
        "expected_output": task.expected_output,
        "actual_output": artifacts.output_text,
        "outcome_result": artifacts.outcome_result,
        "outcome_explanation": artifacts.outcome_explanation,
        "errors": artifacts.errors,
        "field_feedback": field_feedback,
        "scores": {
            "task_success": score,
            "outcome_success": 1.0 if artifacts.outcome_result == "satisfied" else 0.0,
            "latency_inv": latency_proxy,
            "cost_inv": cost_inv,
        },
        "runtime": {
            "agent_id": artifacts.agent_id,
            "agent_version": artifacts.agent_version,
            "environment_id": artifacts.environment_id,
            "session_id": artifacts.session_id,
            "event_types": artifacts.event_types,
            "tool_events": artifacts.tool_events,
            "usage": artifacts.usage,
        },
    }
