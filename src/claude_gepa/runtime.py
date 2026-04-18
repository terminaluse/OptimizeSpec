from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import time
from typing import Any
from uuid import uuid4

import anthropic
import httpx

from .candidate import CandidateBundle, SubagentSpec
from .tasks import DummyTask


DEFAULT_MODEL = "claude-opus-4-7"
STREAM_BETAS = [
    "managed-agents-2026-04-01",
    "managed-agents-2026-04-01-research-preview",
]
OUTCOME_SEND_BETA = "agent-api-2026-03-01"


@dataclass
class RunArtifacts:
    candidate_id: str
    task_id: str
    agent_id: str
    agent_version: int
    environment_id: str
    session_id: str
    output_text: str | None
    output_file_id: str | None
    outcome_result: str | None
    outcome_explanation: str | None
    tool_events: list[dict[str, Any]]
    event_types: list[str]
    usage: dict[str, int]
    errors: list[str]


class ManagedAgentRuntime:
    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        self.client = client or anthropic.Anthropic()

    def run_task(
        self,
        bundle: CandidateBundle,
        task: DummyTask,
        *,
        use_outcomes: bool = True,
        max_runtime_seconds: float = 45.0,
    ) -> RunArtifacts:
        suffix = f"{bundle.candidate_id}-{task.task_id}-{uuid4().hex[:8]}"
        uploaded_file = self.client.beta.files.upload(
            file=(Path(task.input_path).name, task.input_text.encode("utf-8"), "text/plain")
        )

        if bundle.subagents:
            raise RuntimeError(
                "subagent_specs is non-empty, but the installed anthropic Python SDK does not expose "
                "typed callable_agents support for Managed Agents multi-agent sessions yet."
            )

        subagent_records = []
        agent = self.client.beta.agents.create(**self._build_agent_payload(bundle, suffix, subagent_records))
        environment = self.client.beta.environments.create(
            name=f"claude-gepa-env-{suffix}",
            config=bundle.environment.config,
        )
        session = self.client.beta.sessions.create(
            agent={"type": "agent", "id": agent.id, "version": agent.version},
            environment_id=environment.id,
            resources=[
                {"type": "file", "file_id": uploaded_file.id, "mount_path": task.input_path},
            ],
            title=f"claude-gepa-{task.task_id}",
            metadata={
                "candidate_id": bundle.candidate_id,
                "task_id": task.task_id,
            },
        )

        event_types: list[str] = []
        tool_events: list[dict[str, Any]] = []
        errors: list[str] = []
        usage = {"input_tokens": 0, "output_tokens": 0}
        outcome_result: str | None = None
        outcome_explanation: str | None = None
        started_at = time.monotonic()

        with self.client.beta.sessions.events.stream(session_id=session.id, betas=STREAM_BETAS) as stream:
            if use_outcomes:
                self._send_initial_events(session.id, bundle, task)
            else:
                self.client.beta.sessions.events.send(
                    session_id=session.id,
                    events=[
                        {
                            "type": "user.message",
                            "content": [
                                {
                                    "type": "text",
                                    "text": bundle.render_task_prompt(
                                        task_summary=task.task_summary,
                                        input_path=task.input_path,
                                        output_path=task.output_path,
                                    ),
                                }
                            ],
                        }
                    ],
                )

            for event in stream:
                if time.monotonic() - started_at > max_runtime_seconds:
                    errors.append(f"session exceeded max_runtime_seconds={max_runtime_seconds}")
                    try:
                        self.client.beta.sessions.events.send(
                            session_id=session.id,
                            events=[{"type": "user.interrupt"}],
                        )
                    except Exception:
                        pass
                    break
                event_types.append(event.type)
                if event.type in {"agent.tool_use", "agent.tool_result"}:
                    tool_events.append({"type": event.type, "tool_name": getattr(event, "tool_name", None)})
                elif event.type == "span.outcome_evaluation_end":
                    outcome_result = event.result
                    outcome_explanation = event.explanation
                elif event.type == "span.model_request_end":
                    model_usage = getattr(event, "model_usage", None)
                    if model_usage is not None:
                        usage["input_tokens"] += int(getattr(model_usage, "input_tokens", 0) or 0)
                        usage["output_tokens"] += int(getattr(model_usage, "output_tokens", 0) or 0)
                elif event.type == "session.error":
                    message = getattr(event, "message", "unknown session error")
                    errors.append(str(message))
                elif event.type in {"session.status_idle", "session.status_terminated"}:
                    if event.type == "session.status_terminated":
                        break
                    stop_reason = getattr(event, "stop_reason", None)
                    if not stop_reason or getattr(stop_reason, "type", None) != "requires_action":
                        break

        output_file_id, output_text = self._fetch_output_text(session.id, expected_output_path=Path(task.output_path).name)

        self.client.beta.sessions.archive(session.id)
        self.client.beta.agents.archive(agent.id)
        self.client.beta.environments.archive(environment.id)
        for subagent in subagent_records:
            self.client.beta.agents.archive(subagent["id"])

        return RunArtifacts(
            candidate_id=bundle.candidate_id,
            task_id=task.task_id,
            agent_id=agent.id,
            agent_version=agent.version,
            environment_id=environment.id,
            session_id=session.id,
            output_text=output_text,
            output_file_id=output_file_id,
            outcome_result=outcome_result,
            outcome_explanation=outcome_explanation,
            tool_events=tool_events,
            event_types=event_types,
            usage=usage,
            errors=errors,
        )

    def _send_initial_events(self, session_id: str, bundle: CandidateBundle, task: DummyTask) -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required to send outcome events")

        payload = {
            "events": [
                {
                    "type": "define_outcome",
                    "description": bundle.render_task_prompt(
                        task_summary=task.task_summary,
                        input_path=task.input_path,
                        output_path=task.output_path,
                    ),
                    "rubric": {"type": "text", "content": bundle.render_outcome_rubric(output_path=task.output_path)},
                    "max_iterations": 3,
                }
            ]
        }

        response = httpx.post(
            f"https://api.anthropic.com/v1/sessions/{session_id}/events",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "anthropic-beta": OUTCOME_SEND_BETA,
                "content-type": "application/json",
            },
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()

    def _build_agent_payload(
        self,
        bundle: CandidateBundle,
        suffix: str,
        subagent_records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": f"claude-gepa-agent-{suffix}",
            "model": DEFAULT_MODEL,
            "system": bundle.system_prompt,
            "tools": [
                {
                    "type": "agent_toolset_20260401",
                    "default_config": {
                        "enabled": True,
                        "permission_policy": {"type": "always_allow"},
                    },
                    "configs": [
                        {"name": "web_search", "enabled": False},
                        {"name": "web_fetch", "enabled": False},
                    ],
                }
            ],
        }
        if bundle.skills:
            payload["skills"] = [skill.to_api() for skill in bundle.skills]
        if subagent_records:
            payload["callable_agents"] = [
                {"type": "agent", "id": record["id"]} for record in subagent_records
            ]
        return payload

    def _fetch_output_text(self, session_id: str, expected_output_path: str) -> tuple[str | None, str | None]:
        for _ in range(4):
            files = self.client.beta.files.list(
                scope_id=session_id,
                betas=["managed-agents-2026-04-01"],
            )
            for file_meta in files.data:
                if file_meta.filename == expected_output_path:
                    response = self.client.beta.files.download(file_meta.id)
                    return file_meta.id, response.read().decode("utf-8")
            time.sleep(1.0)
        return None, None
