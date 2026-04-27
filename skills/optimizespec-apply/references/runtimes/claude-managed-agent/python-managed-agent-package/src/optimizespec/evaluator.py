from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import traceback
from typing import Any

import gepa.optimize_anything as oa

from .candidate import CandidateBundle, CandidateCompilationError, CandidateCompiler, StructuredCandidateCompiler
from .runtime import ManagedAgentRuntime, RunArtifacts
from .tasks import DummyTask


@dataclass(frozen=True)
class EvaluationResult:
    score: float
    side_info: dict[str, Any]


def compute_text_match_score(expected: str, actual: str | None) -> float:
    if actual is None:
        return 0.0
    return 1.0 if actual == expected else 0.0


def compute_live_rollout_score(task: DummyTask, artifacts: RunArtifacts) -> float:
    if artifacts.errors or artifacts.timed_out or artifacts.interrupted:
        return 0.0
    return compute_text_match_score(task.expected_output, artifacts.output_text)


class ManagedAgentEvaluator:
    def __init__(
        self,
        *,
        run_dir: Path | None = None,
        runtime: ManagedAgentRuntime | None = None,
        compiler: CandidateCompiler | None = None,
        use_outcomes: bool = True,
        max_runtime_seconds: float = 45.0,
    ) -> None:
        self.runtime = runtime or ManagedAgentRuntime()
        self.compiler = compiler or StructuredCandidateCompiler()
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

        bundle: CandidateBundle | None = None
        try:
            bundle = CandidateBundle.from_candidate(candidate, compiler=self.compiler)
        except CandidateCompilationError as exc:
            score = 0.0
            side_info = build_candidate_compilation_failure_side_info(example, exc)
            self._persist_run(None, example, None, side_info)
            return score, side_info

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
            score = compute_live_rollout_score(example, artifacts)
            side_info = build_side_info(example, bundle, artifacts, score)
        except Exception as exc:
            score = 0.0
            field_feedback = {
                "system_prompt": "Tighten the system prompt to reduce runtime mistakes.",
                "task_prompt": "Make required file paths and completion criteria more explicit.",
                "outcome_rubric": "Simplify the rubric if the outcome path is unsupported or unstable.",
                "skills": (
                    "Keep the skills field parseable. Use direct refs for reusable skills or inline custom "
                    "skill definitions with a root-level SKILL.md when the candidate needs new skill content."
                ),
                "environment_spec": (
                    "Keep environment networking and package-manager config valid. Use package lists only when "
                    "they materially help the task."
                ),
                "subagent_specs": (
                    "Use callable subagents only for narrowly scoped specialist work. Each subagent should have "
                    "a clear role and valid nested skills."
                ),
            }
            side_info = {
                "Input": example.input_text,
                "Expected": example.expected_output,
                "Actual": None,
                "Feedback": "Runtime setup or rollout execution failed.",
                "Error": str(exc),
                "Agent Trajectory": [],
                "Runtime": {
                    "setup_error": str(exc),
                    "runtime_metadata": {},
                    "usage": {},
                    "cleanup": {"status": "skipped", "warnings": []},
                },
                "candidate_id": bundle.candidate_id,
                "raw_candidate": {
                    "raw_fields": bundle.raw_fields,
                    "canonical_fields": bundle.fields,
                },
                "task_id": example.task_id,
                "expected_output": example.expected_output,
                "actual_output": None,
                "errors": [str(exc)],
                "cleanup_warnings": [],
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc(),
                "field_feedback": field_feedback,
                "scores": {
                    "task_success": 0.0,
                    "outcome_success": 0.0,
                    "latency_inv": 0.0,
                    "cost_inv": 0.0,
                },
                "runtime": {
                    "setup_error": str(exc),
                    "resolved_skills": [],
                    "subagents": [],
                },
                **{
                    f"{field_name}_specific_info": {
                        "Current Value": bundle.fields.get(field_name),
                        "Feedback": feedback,
                        "scores": {"task_success": 0.0},
                    }
                    for field_name, feedback in field_feedback.items()
                },
            }
        self._persist_run(bundle, example, artifacts, side_info)
        return score, side_info

    def _persist_run(
        self,
        bundle: CandidateBundle | None,
        task: DummyTask,
        artifacts: RunArtifacts | None,
        side_info: dict[str, Any],
    ) -> None:
        candidate_id = side_info.get("candidate_id", "unknown-candidate")
        if bundle is not None:
            candidate_id = bundle.candidate_id
        out_dir = self.run_dir / candidate_id / task.task_id
        out_dir.mkdir(parents=True, exist_ok=True)
        candidate_payload = side_info.get("raw_candidate")
        if bundle is not None:
            candidate_payload = {
                "raw_fields": bundle.raw_fields,
                "canonical_fields": bundle.fields,
            }
        if candidate_payload is not None:
            (out_dir / "candidate.json").write_text(
                json.dumps(candidate_payload, indent=2, sort_keys=True),
                encoding="utf-8",
            )
        rollout_record = build_rollout_record(
            task=task,
            bundle=bundle,
            artifacts=artifacts,
            side_info=side_info,
        )
        (out_dir / "rollout.json").write_text(
            json.dumps(rollout_record, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (out_dir / "score.json").write_text(
            json.dumps(build_score_record(side_info), indent=2, sort_keys=True),
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
        "skills": (
            "Use skills for reusable domain guidance. Anthropic skills use direct refs; custom skills need a "
            "root-level SKILL.md plus any supporting files."
        ),
        "environment_spec": (
            "Use the environment to enable network access or package-manager installs only when the benchmark task "
            "materially benefits from them."
        ),
        "subagent_specs": (
            "Use subagents for tightly scoped decomposition or verification. Each subagent should have a focused "
            "system prompt and only the skills it needs."
        ),
    }
    runtime_metadata = {
        "agent_id": artifacts.agent_id,
        "agent_version": artifacts.agent_version,
        "environment_id": artifacts.environment_id,
        "environment_config": artifacts.environment_config,
        "session_id": artifacts.session_id,
        "session_status": artifacts.session_status,
        "event_types": artifacts.event_types,
        "output_file_id": artifacts.output_file_id,
        "resolved_skills": artifacts.resolved_skills,
        "subagents": artifacts.subagents,
        "managed_agents_betas": ["managed-agents-2026-04-01-research-preview"],
    }
    runtime_payload = {
        "setup_error": None,
        "runtime_metadata": runtime_metadata,
        "usage": artifacts.usage,
        "cleanup": {
            "status": artifacts.cleanup_status,
            "warnings": artifacts.cleanup_warnings,
        },
        "timeout": {
            "configured_seconds": artifacts.timeout_seconds,
            "timed_out": artifacts.timed_out,
            "interrupted": artifacts.interrupted,
        },
    }
    field_specific = {
        f"{field_name}_specific_info": {
            "Current Value": bundle.fields.get(field_name),
            "Feedback": feedback,
            "scores": {"task_success": score},
        }
        for field_name, feedback in field_feedback.items()
    }
    if artifacts.timed_out or artifacts.interrupted or artifacts.errors:
        feedback = "Live rollout timed out, was interrupted, or reported runtime errors."
    elif score >= 1.0:
        feedback = "Live output matched expected output."
    else:
        feedback = "Live output did not match expected output."

    return {
        "Input": task.input_text,
        "Expected": task.expected_output,
        "Actual": artifacts.output_text,
        "Feedback": feedback,
        "Error": artifacts.errors or None,
        "Agent Trajectory": artifacts.event_types,
        "Runtime": runtime_payload,
        "candidate_id": bundle.candidate_id,
        "raw_candidate": {
            "raw_fields": bundle.raw_fields,
            "canonical_fields": bundle.fields,
        },
        "task_id": task.task_id,
        "focus_fields": list(task.focus_fields),
        "expected_output": task.expected_output,
        "actual_output": artifacts.output_text,
        "outcome_result": artifacts.outcome_result,
        "outcome_explanation": artifacts.outcome_explanation,
        "errors": artifacts.errors,
        "cleanup_warnings": artifacts.cleanup_warnings,
        "field_feedback": field_feedback,
        "scores": {
            "task_success": score,
            "outcome_success": 1.0 if artifacts.outcome_result == "satisfied" else 0.0,
            "latency_inv": latency_proxy,
            "cost_inv": cost_inv,
        },
        "runtime": {
            **runtime_metadata,
            "tool_events": artifacts.tool_events,
            "usage": artifacts.usage,
            "cleanup": runtime_payload["cleanup"],
            "timeout": runtime_payload["timeout"],
        },
        **field_specific,
    }


def build_candidate_compilation_failure_side_info(
    task: DummyTask,
    exc: CandidateCompilationError,
) -> dict[str, Any]:
    field_feedback = {
        "system_prompt": "Preserve the prompt text exactly and avoid pushing structured config into prompt fields.",
        "task_prompt": "Keep task templating intact and do not move config data into task instructions.",
        "outcome_rubric": "Keep rubric text distinct from structured runtime configuration.",
        "skills": (
            "Provide a parseable list of skills. Each item must be either a direct reusable ref or a custom "
            "skill definition with files under one root directory and a valid SKILL.md."
        ),
        "environment_spec": (
            "Provide one parseable cloud environment spec with networking and package-manager lists that match "
            "the Anthropic environment schema."
        ),
        "subagent_specs": (
            "Provide a parseable list of subagent definitions with name, system_prompt, optional description, "
            "and optional nested hybrid skills."
        ),
    }
    for field, message in exc.field_errors.items():
        field_feedback[field] = message

    return {
        "Input": task.input_text,
        "Expected": task.expected_output,
        "Actual": None,
        "Feedback": "Candidate failed to compile into Managed Agents runtime configuration.",
        "Error": str(exc),
        "Agent Trajectory": [],
        "Runtime": {
            "setup_error": None,
            "runtime_metadata": {},
            "usage": {},
            "cleanup": {"status": "skipped", "warnings": []},
        },
        "candidate_id": exc.raw_candidate_id,
        "raw_candidate": {
            "raw_fields": exc.raw_fields,
            "canonical_fields": None,
        },
        "task_id": task.task_id,
        "focus_fields": list(task.focus_fields),
        "expected_output": task.expected_output,
        "actual_output": None,
        "errors": [str(exc)],
        "compile_stage": exc.details.get("stage"),
        "field_errors": exc.field_errors,
        "details": exc.details,
        "field_feedback": field_feedback,
        "scores": {
            "task_success": 0.0,
            "outcome_success": 0.0,
            "latency_inv": 0.0,
            "cost_inv": 0.0,
        },
        "runtime": {},
        **{
            f"{field_name}_specific_info": {
                "Current Value": exc.raw_fields.get(field_name),
                "Feedback": feedback,
                "scores": {"task_success": 0.0},
            }
            for field_name, feedback in field_feedback.items()
        },
    }


def build_rollout_record(
    *,
    task: DummyTask,
    bundle: CandidateBundle | None,
    artifacts: RunArtifacts | None,
    side_info: dict[str, Any],
) -> dict[str, Any]:
    if artifacts is None:
        runtime = side_info.get("Runtime") or {}
        errors = side_info.get("errors") or ([side_info["Error"]] if side_info.get("Error") else [])
        return {
            "candidate_id": side_info.get("candidate_id", "unknown-candidate"),
            "eval_case_id": task.task_id,
            "status": "failed",
            "final_output": side_info.get("Actual"),
            "trace_summary": side_info.get("Agent Trajectory", []),
            "tool_activity": [],
            "usage": runtime.get("usage", {}),
            "errors": errors,
            "timeout": runtime.get(
                "timeout",
                {"configured_seconds": None, "timed_out": False, "interrupted": False},
            ),
            "cleanup": runtime.get("cleanup", {"status": "skipped", "warnings": []}),
            "timestamps": {"started_at": None, "ended_at": None},
            "score_inputs": {
                "expected_output": task.expected_output,
                "final_output_ref": None,
                "trace_ref": "rollout.json",
                "runtime_metadata_ref": "rollout.json#runtime_metadata",
            },
            "runtime_metadata": runtime.get("runtime_metadata", {}),
        }

    trace_summary = [{"type": event_type} for event_type in artifacts.event_types]
    return {
        "candidate_id": artifacts.candidate_id,
        "eval_case_id": artifacts.task_id,
        "status": artifacts.status,
        "final_output": artifacts.output_text,
        "trace_summary": trace_summary,
        "tool_activity": artifacts.tool_events,
        "usage": artifacts.usage,
        "errors": artifacts.errors,
        "timeout": {
            "configured_seconds": artifacts.timeout_seconds,
            "timed_out": artifacts.timed_out,
            "interrupted": artifacts.interrupted,
        },
        "cleanup": {
            "status": artifacts.cleanup_status,
            "warnings": artifacts.cleanup_warnings,
        },
        "timestamps": {
            "started_at": artifacts.started_at,
            "ended_at": artifacts.ended_at,
        },
        "score_inputs": {
            "expected_output": task.expected_output,
            "final_output_ref": "result.txt" if artifacts.output_text is not None else None,
            "trace_ref": "rollout.json",
            "runtime_metadata_ref": "rollout.json#runtime_metadata",
            "side_info_ref": "side_info.json",
        },
        "runtime_metadata": {
            "agent_id": artifacts.agent_id,
            "agent_version": artifacts.agent_version,
            "environment_id": artifacts.environment_id,
            "environment_config": artifacts.environment_config,
            "session_id": artifacts.session_id,
            "session_status": artifacts.session_status,
            "output_file_id": artifacts.output_file_id,
            "outcome_result": artifacts.outcome_result,
            "outcome_explanation": artifacts.outcome_explanation,
            "event_types": artifacts.event_types,
            "resolved_skills": artifacts.resolved_skills,
            "subagents": artifacts.subagents,
            "managed_agents_betas": ["managed-agents-2026-04-01-research-preview"],
        },
    }


def build_score_record(side_info: dict[str, Any]) -> dict[str, Any]:
    scores = dict(side_info.get("scores") or {})
    return {
        "candidate_id": side_info.get("candidate_id", "unknown-candidate"),
        "eval_case_id": side_info.get("task_id", "unknown-case"),
        "score": float(scores.get("task_success", 0.0) or 0.0),
        "scores": scores,
        "feedback": side_info.get("Feedback"),
        "outcome_result": side_info.get("outcome_result"),
        "errors": side_info.get("errors", []),
        "rollout_evidence_path": "rollout.json",
        "side_info_path": "side_info.json",
        "result_path": "result.txt" if side_info.get("actual_output") is not None else None,
    }
