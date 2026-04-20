from types import SimpleNamespace

import pytest

from claude_gepa.candidate import (
    CandidateBundle,
    CustomSkillSpec,
    EnvironmentSpec,
    SkillFile,
    SubagentSpec,
)
from claude_gepa.runtime import ManagedAgentRuntime


class _FakeSessions:
    def __init__(self, statuses: list[str], *, archive_error: Exception | None = None) -> None:
        self._statuses = list(statuses)
        self.archive_calls: list[str] = []
        self.archive_error = archive_error

    def retrieve(self, session_id: str, *, betas: list[str]) -> SimpleNamespace:
        status = self._statuses.pop(0) if self._statuses else "idle"
        return SimpleNamespace(status=status)

    def archive(self, session_id: str, *, betas: list[str]) -> None:
        self.archive_calls.append(session_id)
        if self.archive_error is not None:
            raise self.archive_error


class _FakeSkillVersions:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, skill_id: str, *, files, betas):
        self.calls.append({"skill_id": skill_id, "files": list(files), "betas": list(betas)})
        return SimpleNamespace(skill_id=skill_id, version="v2")


class _FakeSkills:
    def __init__(self) -> None:
        self.create_calls: list[dict[str, object]] = []
        self.versions = _FakeSkillVersions()

    def create(self, *, display_title, files, betas):
        self.create_calls.append({"display_title": display_title, "files": list(files), "betas": list(betas)})
        return SimpleNamespace(id="skill_new", latest_version="v1")


class _FakeAgents:
    def __init__(self) -> None:
        self.create_calls: list[dict[str, object]] = []

    def create(self, **kwargs):
        self.create_calls.append(kwargs)
        return SimpleNamespace(id=f"agent_{len(self.create_calls)}", version=len(self.create_calls))

    def archive(self, agent_id: str) -> None:
        return None


class _FakeEnvironments:
    def create(self, *, name: str, config):
        return SimpleNamespace(id="env_test", config=config)

    def archive(self, environment_id: str) -> None:
        return None


class _FakeBeta:
    def __init__(self, sessions: _FakeSessions | None = None) -> None:
        self.sessions = sessions or _FakeSessions(["idle"])
        self.skills = _FakeSkills()
        self.agents = _FakeAgents()
        self.environments = _FakeEnvironments()
        self.files = SimpleNamespace(upload=lambda file: SimpleNamespace(id="file_test"))


class _FakeClient:
    def __init__(self, sessions: _FakeSessions | None = None) -> None:
        self.beta = _FakeBeta(sessions)


def _make_custom_skill(*, fingerprint: str = "fp1") -> CustomSkillSpec:
    return CustomSkillSpec(
        display_title="Exact Output Checklist",
        files=(
            SkillFile(
                path="exact-output-checklist/SKILL.md",
                content=(
                    "---\n"
                    "name: exact-output-checklist\n"
                    "description: Verification checklist for deterministic file-output tasks.\n"
                    "---\n"
                    "Use this skill to verify exact file outputs.\n"
                ),
            ),
        ),
        root_dir="exact-output-checklist",
        skill_name="exact-output-checklist",
        skill_description="Verification checklist for deterministic file-output tasks.",
        logical_key="exact-output-checklist:exact-output-checklist",
        fingerprint=fingerprint,
    )


def _make_bundle_with_subagent() -> CandidateBundle:
    return CandidateBundle(
        raw_fields={},
        fields={
            "system_prompt": "Coordinate work.",
            "task_prompt": "Task {task_summary} {input_path} {output_path}",
            "outcome_rubric": "Write to {output_path}",
            "skills": "[]\n",
            "environment_spec": "type: cloud\n",
            "subagent_specs": "- name: verifier\n",
        },
        candidate_id="cand_test",
        skills=(),
        environment=EnvironmentSpec(
            config={
                "type": "cloud",
                "networking": {"type": "limited", "allowed_hosts": [], "allow_mcp_servers": False, "allow_package_managers": False},
                "packages": {"type": "packages", "apt": [], "cargo": [], "gem": [], "go": [], "npm": [], "pip": []},
            }
        ),
        subagents=(SubagentSpec(name="verifier", system_prompt="Verify output."),),
    )


def test_wait_for_settled_session_polls_until_idle(monkeypatch) -> None:
    sessions = _FakeSessions(["running", "running", "idle"])
    runtime = ManagedAgentRuntime(client=_FakeClient(sessions))
    monkeypatch.setattr("claude_gepa.runtime.time.sleep", lambda _: None)

    status = runtime._wait_for_settled_session(
        "sesn_test",
        initial_status="running",
        timeout_seconds=5.0,
        poll_interval_seconds=0.1,
    )

    assert status == "idle"


def test_archive_session_if_idle_skips_running_session() -> None:
    sessions = _FakeSessions(["running", "running", "running"])
    runtime = ManagedAgentRuntime(client=_FakeClient(sessions))
    errors: list[str] = []

    runtime._archive_session_if_idle("sesn_test", session_status="running", errors=errors)

    assert sessions.archive_calls == []
    assert errors == ["skipped session archive because session status was running"]


def test_archive_session_if_idle_records_archive_failures() -> None:
    sessions = _FakeSessions(["idle"], archive_error=RuntimeError("boom"))
    runtime = ManagedAgentRuntime(client=_FakeClient(sessions))
    errors: list[str] = []

    runtime._archive_session_if_idle("sesn_test", session_status="idle", errors=errors)

    assert sessions.archive_calls == ["sesn_test", "sesn_test", "sesn_test"]
    assert errors == ["session archive failed: boom"]


def test_archive_session_if_idle_waits_for_idle_before_archiving(monkeypatch) -> None:
    sessions = _FakeSessions(["running", "idle"])
    runtime = ManagedAgentRuntime(client=_FakeClient(sessions))
    errors: list[str] = []
    monkeypatch.setattr("claude_gepa.runtime.time.sleep", lambda _: None)

    runtime._archive_session_if_idle("sesn_test", session_status="idle", errors=errors)

    assert sessions.archive_calls == ["sesn_test"]
    assert errors == []


def test_resolve_custom_skill_reuses_registry_entry(tmp_path) -> None:
    runtime = ManagedAgentRuntime(client=_FakeClient(), skill_registry_path=tmp_path / "skills.json")
    skill = _make_custom_skill(fingerprint="fp-reuse")
    runtime.skill_registry.record(
        fingerprint=skill.fingerprint,
        logical_key=skill.logical_key,
        skill_id="skill_cached",
        version="v1",
        display_title=skill.display_title,
    )

    resolved, events = runtime._resolve_skills((skill,))

    assert resolved[0].skill_id == "skill_cached"
    assert resolved[0].version == "v1"
    assert events[0]["resolution"] == "registry_reuse"
    assert runtime.client.beta.skills.create_calls == []
    assert runtime.client.beta.skills.versions.calls == []


def test_resolve_custom_skill_creates_new_version_for_known_logical_key(tmp_path) -> None:
    runtime = ManagedAgentRuntime(client=_FakeClient(), skill_registry_path=tmp_path / "skills.json")
    runtime.skill_registry.record(
        fingerprint="older-fingerprint",
        logical_key="exact-output-checklist:exact-output-checklist",
        skill_id="skill_cached",
        version="v1",
        display_title="Exact Output Checklist",
    )
    skill = _make_custom_skill(fingerprint="new-fingerprint")

    resolved, events = runtime._resolve_skills((skill,))

    assert resolved[0].skill_id == "skill_cached"
    assert resolved[0].version == "v2"
    assert events[0]["resolution"] == "created_version"
    assert runtime.client.beta.skills.versions.calls[0]["skill_id"] == "skill_cached"


def test_create_agent_includes_callable_agents_extra_body(tmp_path) -> None:
    runtime = ManagedAgentRuntime(
        client=_FakeClient(),
        skill_registry_path=tmp_path / "skills.json",
        enable_multi_agent=True,
    )

    runtime._create_agent(
        name="main-agent",
        system_prompt="Coordinate work.",
        resolved_skills=[],
        description=None,
        callable_agents=[{"id": "agent_sub", "version": 7}],
    )

    create_call = runtime.client.beta.agents.create_calls[0]
    assert create_call["extra_body"] == {
        "callable_agents": [{"type": "agent", "id": "agent_sub", "version": 7}]
    }
    assert create_call["betas"] == ["managed-agents-2026-04-01-research-preview"]


def test_run_task_rejects_subagents_when_multi_agent_flag_is_disabled(tmp_path) -> None:
    runtime = ManagedAgentRuntime(client=_FakeClient(), skill_registry_path=tmp_path / "skills.json")

    with pytest.raises(RuntimeError) as excinfo:
        runtime.run_task(
            _make_bundle_with_subagent(),
            SimpleNamespace(
                task_id="task1",
                input_path="/workspace/task_input.txt",
                input_text="hello",
                output_path="/mnt/session/outputs/result.txt",
                task_summary="verify",
            ),
        )

    assert "CLAUDE_GEPA_ENABLE_MULTI_AGENT=1" in str(excinfo.value)


def test_runtime_reads_multi_agent_flag_from_env(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("CLAUDE_GEPA_ENABLE_MULTI_AGENT", "1")
    runtime = ManagedAgentRuntime(client=_FakeClient(), skill_registry_path=tmp_path / "skills.json")

    assert runtime.enable_multi_agent is True
