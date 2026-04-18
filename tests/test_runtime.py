from types import SimpleNamespace

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


class _FakeBeta:
    def __init__(self, sessions: _FakeSessions) -> None:
        self.sessions = sessions


class _FakeClient:
    def __init__(self, sessions: _FakeSessions) -> None:
        self.beta = _FakeBeta(sessions)


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
    sessions = _FakeSessions(["running"])
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
