from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import time
from typing import Any
from uuid import uuid4

import anthropic
import httpx

from .candidate import CandidateBundle, CustomSkillSpec, SkillRef, SkillSpec, SubagentSpec
from .skill_registry import LocalSkillRegistry
from .tasks import DummyTask


DEFAULT_MODEL = "claude-opus-4-7"
MANAGED_AGENTS_BETA = "managed-agents-2026-04-01"
RESEARCH_PREVIEW_BETA = "managed-agents-2026-04-01-research-preview"
SKILLS_BETA = "skills-2025-10-02"
STREAM_BETAS = [
    MANAGED_AGENTS_BETA,
    RESEARCH_PREVIEW_BETA,
]
OUTCOME_SEND_BETA = "agent-api-2026-03-01"
MULTI_AGENT_FLAG_ENV = "CLAUDE_GEPA_ENABLE_MULTI_AGENT"
MAX_MANAGED_AGENT_SKILLS_PER_SESSION = 20


@dataclass
class RunArtifacts:
    candidate_id: str
    task_id: str
    agent_id: str
    agent_version: int
    environment_id: str
    session_id: str
    session_status: str | None
    output_text: str | None
    output_file_id: str | None
    outcome_result: str | None
    outcome_explanation: str | None
    tool_events: list[dict[str, Any]]
    event_types: list[str]
    usage: dict[str, int]
    errors: list[str]
    resolved_skills: list[dict[str, Any]]
    subagents: list[dict[str, Any]]
    environment_config: dict[str, Any]


class ManagedAgentRuntime:
    def __init__(
        self,
        client: anthropic.Anthropic | None = None,
        *,
        skill_registry_path: Path | None = None,
        enable_multi_agent: bool | None = None,
    ) -> None:
        self.client = client or anthropic.Anthropic()
        self.skill_registry = LocalSkillRegistry(skill_registry_path or Path(".claude_gepa") / "skill_registry.json")
        self.enable_multi_agent = _resolve_feature_flag(enable_multi_agent, MULTI_AGENT_FLAG_ENV)

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

        total_skill_count = len(bundle.skills) + sum(len(subagent.skills) for subagent in bundle.subagents)
        if total_skill_count > MAX_MANAGED_AGENT_SKILLS_PER_SESSION:
            raise RuntimeError(
                f"total skills across the managed-agent session must be <= {MAX_MANAGED_AGENT_SKILLS_PER_SESSION}"
            )

        resolved_root_skills, root_skill_events = self._resolve_skills(bundle.skills)
        if bundle.subagents and not self.enable_multi_agent:
            raise RuntimeError(
                f"subagent_specs requires {MULTI_AGENT_FLAG_ENV}=1 because multi-agent is a preview-gated feature"
            )
        subagent_records = self._create_subagents(bundle.subagents, suffix=suffix)

        agent = self._create_agent(
            name=f"claude-gepa-agent-{suffix}",
            system_prompt=bundle.system_prompt,
            resolved_skills=resolved_root_skills,
            description=None,
            callable_agents=subagent_records,
        )
        environment = self.client.beta.environments.create(
            name=f"claude-gepa-env-{suffix}",
            config=bundle.environment.config,
        )
        session_kwargs: dict[str, Any] = {
            "agent": {"type": "agent", "id": agent.id, "version": agent.version},
            "environment_id": environment.id,
            "resources": [
                {"type": "file", "file_id": uploaded_file.id, "mount_path": task.input_path},
            ],
            "title": f"claude-gepa-{task.task_id}",
            "metadata": {
                "candidate_id": bundle.candidate_id,
                "task_id": task.task_id,
            },
        }
        if subagent_records:
            session_kwargs["betas"] = [RESEARCH_PREVIEW_BETA]
        session = self.client.beta.sessions.create(**session_kwargs)

        event_types: list[str] = []
        tool_events: list[dict[str, Any]] = []
        errors: list[str] = []
        usage = {"input_tokens": 0, "output_tokens": 0}
        outcome_result: str | None = None
        outcome_explanation: str | None = None
        session_status: str | None = "running"
        started_at = time.monotonic()

        with self.client.beta.sessions.events.stream(session_id=session.id, betas=STREAM_BETAS) as stream:
            if use_outcomes:
                self._send_initial_events(session.id, bundle, task)
            self._send_user_message(session.id, bundle, task)

            for event in stream:
                if time.monotonic() - started_at > max_runtime_seconds:
                    errors.append(f"session exceeded max_runtime_seconds={max_runtime_seconds}")
                    self._interrupt_session(session.id)
                    break
                event_types.append(event.type)
                if event.type in {"agent.tool_use", "agent.tool_result"}:
                    tool_events.append(
                        {
                            "type": event.type,
                            "tool_name": getattr(event, "tool_name", None),
                            "session_thread_id": getattr(event, "session_thread_id", None),
                        }
                    )
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
                    session_status = "idle" if event.type == "session.status_idle" else "terminated"
                    if event.type == "session.status_terminated":
                        break
                    stop_reason = getattr(event, "stop_reason", None)
                    if not stop_reason or getattr(stop_reason, "type", None) != "requires_action":
                        break

        session_status = self._wait_for_settled_session(
            session.id,
            initial_status=session_status,
            timeout_seconds=15.0,
        )
        output_file_id, output_text = self._fetch_output_text(session.id, expected_output_path=Path(task.output_path).name)
        self._archive_session_if_idle(session.id, session_status=session_status, errors=errors)
        self._best_effort_archive_agent(agent.id, errors=errors)
        self._best_effort_archive_environment(environment.id, errors=errors)
        for subagent in subagent_records:
            self._best_effort_archive_agent(subagent["id"], errors=errors)

        return RunArtifacts(
            candidate_id=bundle.candidate_id,
            task_id=task.task_id,
            agent_id=agent.id,
            agent_version=agent.version,
            environment_id=environment.id,
            session_id=session.id,
            session_status=session_status,
            output_text=output_text,
            output_file_id=output_file_id,
            outcome_result=outcome_result,
            outcome_explanation=outcome_explanation,
            tool_events=tool_events,
            event_types=event_types,
            usage=usage,
            errors=errors,
            resolved_skills=root_skill_events,
            subagents=subagent_records,
            environment_config=bundle.environment.config,
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

    def _send_user_message(self, session_id: str, bundle: CandidateBundle, task: DummyTask) -> None:
        self.client.beta.sessions.events.send(
            session_id=session_id,
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

    def _create_subagents(self, subagents: tuple[SubagentSpec, ...], *, suffix: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for index, subagent in enumerate(subagents, start=1):
            resolved_skills, skill_events = self._resolve_skills(subagent.skills)
            created = self._create_agent(
                name=f"claude-gepa-subagent-{index}-{suffix}",
                system_prompt=subagent.system_prompt,
                resolved_skills=resolved_skills,
                description=subagent.description,
                callable_agents=None,
            )
            records.append(
                {
                    "id": created.id,
                    "version": created.version,
                    "name": subagent.name,
                    "description": subagent.description,
                    "resolved_skills": skill_events,
                }
            )
        return records

    def _create_agent(
        self,
        *,
        name: str,
        system_prompt: str,
        resolved_skills: list[SkillRef],
        description: str | None,
        callable_agents: list[dict[str, Any]] | None,
    ):
        kwargs: dict[str, Any] = {
            "name": name,
            "model": DEFAULT_MODEL,
            "system": system_prompt,
            "tools": self._build_agent_tools(),
        }
        if description is not None:
            kwargs["description"] = description
        if resolved_skills:
            kwargs["skills"] = [skill.to_api() for skill in resolved_skills]
        if callable_agents:
            kwargs["extra_body"] = {
                "callable_agents": [
                    {"type": "agent", "id": record["id"], "version": record["version"]} for record in callable_agents
                ]
            }
            kwargs["betas"] = [RESEARCH_PREVIEW_BETA]
        return self.client.beta.agents.create(**kwargs)

    def _build_agent_tools(self) -> list[dict[str, Any]]:
        return [
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
        ]

    def _resolve_skills(self, skills: tuple[SkillSpec, ...]) -> tuple[list[SkillRef], list[dict[str, Any]]]:
        resolved: list[SkillRef] = []
        events: list[dict[str, Any]] = []
        for skill in skills:
            if isinstance(skill, SkillRef):
                resolved.append(skill)
                events.append(
                    {
                        "resolution": "direct_ref",
                        "type": skill.type,
                        "skill_id": skill.skill_id,
                        "version": skill.version,
                    }
                )
                continue
            resolved_ref, event = self._resolve_custom_skill(skill)
            resolved.append(resolved_ref)
            events.append(event)
        return resolved, events

    def _resolve_custom_skill(self, skill: CustomSkillSpec) -> tuple[SkillRef, dict[str, Any]]:
        cached = self.skill_registry.find_by_fingerprint(skill.fingerprint)
        if cached is not None:
            return (
                SkillRef(type="custom", skill_id=cached.skill_id, version=cached.version),
                {
                    "resolution": "registry_reuse",
                    "skill_id": cached.skill_id,
                    "version": cached.version,
                    "logical_key": cached.logical_key,
                    "fingerprint": cached.fingerprint,
                    "display_title": cached.display_title,
                },
            )

        lineage = self.skill_registry.find_latest_by_logical_key(skill.logical_key)
        if lineage is not None:
            created_version = self.client.beta.skills.versions.create(
                lineage.skill_id,
                files=skill.to_api_files(),
                betas=[SKILLS_BETA],
            )
            entry = self.skill_registry.record(
                fingerprint=skill.fingerprint,
                logical_key=skill.logical_key,
                skill_id=created_version.skill_id,
                version=created_version.version,
                display_title=skill.display_title,
            )
            return (
                SkillRef(type="custom", skill_id=entry.skill_id, version=entry.version),
                {
                    "resolution": "created_version",
                    "skill_id": entry.skill_id,
                    "version": entry.version,
                    "logical_key": entry.logical_key,
                    "fingerprint": entry.fingerprint,
                    "display_title": entry.display_title,
                },
            )

        try:
            created_skill = self.client.beta.skills.create(
                display_title=skill.display_title,
                files=skill.to_api_files(),
                betas=[SKILLS_BETA],
            )
            return self._record_created_skill(
                skill,
                created_skill.id,
                created_skill.latest_version or "latest",
                "created_skill",
            )
        except Exception:
            if skill.display_title is None:
                raise
            existing = self._find_custom_skill_by_display_title(skill.display_title)
            if existing is None:
                raise
            self._validate_existing_skill_lineage(skill, existing)
            created_version = self.client.beta.skills.versions.create(
                existing.id,
                files=skill.to_api_files(),
                betas=[SKILLS_BETA],
            )
            return self._record_created_skill(
                skill,
                created_version.skill_id,
                created_version.version,
                "display_title_reuse",
            )

    def _record_created_skill(
        self,
        skill: CustomSkillSpec,
        skill_id: str,
        version: str,
        resolution: str,
    ) -> tuple[SkillRef, dict[str, Any]]:
        entry = self.skill_registry.record(
            fingerprint=skill.fingerprint,
            logical_key=skill.logical_key,
            skill_id=skill_id,
            version=version,
            display_title=skill.display_title,
        )
        return SkillRef(type="custom", skill_id=entry.skill_id, version=entry.version), {
            "resolution": resolution,
            "skill_id": entry.skill_id,
            "version": entry.version,
            "logical_key": entry.logical_key,
            "fingerprint": entry.fingerprint,
            "display_title": entry.display_title,
        }

    def _find_custom_skill_by_display_title(self, display_title: str) -> Any | None:
        page = self.client.beta.skills.list(
            source="custom",
            limit=100,
            betas=[SKILLS_BETA],
        )
        for item in getattr(page, "data", []):
            if getattr(item, "display_title", None) == display_title:
                return item
        return None

    def _validate_existing_skill_lineage(self, skill: CustomSkillSpec, existing_skill: Any) -> None:
        latest_version = getattr(existing_skill, "latest_version", None)
        if not latest_version:
            return
        version = self.client.beta.skills.versions.retrieve(
            latest_version,
            skill_id=existing_skill.id,
            betas=[SKILLS_BETA],
        )
        existing_name = getattr(version, "name", None)
        if existing_name and existing_name != skill.skill_name:
            raise RuntimeError(
                "custom skill display_title collision cannot be reused because the existing skill lineage "
                f"uses name {existing_name!r} but the candidate defines {skill.skill_name!r}. "
                "Use a unique display_title or keep the same SKILL.md name when creating a new version."
            )

    def _fetch_output_text(self, session_id: str, expected_output_path: str) -> tuple[str | None, str | None]:
        for _ in range(4):
            files = self.client.beta.files.list(
                scope_id=session_id,
                betas=[MANAGED_AGENTS_BETA],
            )
            for file_meta in files.data:
                if file_meta.filename == expected_output_path:
                    response = self.client.beta.files.download(file_meta.id)
                    return file_meta.id, response.read().decode("utf-8")
            time.sleep(1.0)
        return None, None

    def _interrupt_session(self, session_id: str) -> None:
        try:
            self.client.beta.sessions.events.send(
                session_id=session_id,
                events=[{"type": "user.interrupt"}],
            )
        except Exception:
            return

    def _wait_for_settled_session(
        self,
        session_id: str,
        *,
        initial_status: str | None,
        timeout_seconds: float,
        poll_interval_seconds: float = 1.0,
    ) -> str | None:
        status = initial_status
        if status == "idle":
            return status

        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            try:
                session = self.client.beta.sessions.retrieve(
                    session_id,
                    betas=[MANAGED_AGENTS_BETA],
                )
            except Exception:
                return status

            status = getattr(session, "status", status)
            if status in {"idle", "terminated"}:
                return status
            time.sleep(poll_interval_seconds)
        return status

    def _archive_session_if_idle(self, session_id: str, *, session_status: str | None, errors: list[str]) -> None:
        if session_status != "idle":
            errors.append(
                f"skipped session archive because session status was {session_status or 'unknown'}"
            )
            return
        archive_error: Exception | None = None
        for _ in range(3):
            try:
                session = self.client.beta.sessions.retrieve(
                    session_id,
                    betas=[MANAGED_AGENTS_BETA],
                )
            except Exception as exc:
                archive_error = exc
                break

            latest_status = getattr(session, "status", None)
            if latest_status != "idle":
                errors.append(
                    f"skipped session archive because session status was {latest_status or 'unknown'}"
                )
                return
            try:
                self.client.beta.sessions.archive(
                    session_id,
                    betas=[MANAGED_AGENTS_BETA],
                )
                return
            except Exception as exc:
                archive_error = exc
                time.sleep(1.0)
        if archive_error is not None:
            errors.append(f"session archive failed: {archive_error}")

    def _best_effort_archive_agent(self, agent_id: str, *, errors: list[str]) -> None:
        try:
            self.client.beta.agents.archive(agent_id)
        except Exception as exc:
            errors.append(f"agent archive failed: {exc}")

    def _best_effort_archive_environment(self, environment_id: str, *, errors: list[str]) -> None:
        try:
            self.client.beta.environments.archive(environment_id)
        except Exception as exc:
            errors.append(f"environment archive failed: {exc}")


def _resolve_feature_flag(explicit_value: bool | None, env_var: str) -> bool:
    if explicit_value is not None:
        return explicit_value
    raw_value = os.environ.get(env_var, "")
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}
