"""Minimal OptimizeSpec runner scaffold.

Copy this file into an agent project, replace `TemplateEchoExecutor` with an executor
that calls the real agent, and extend the scorer/evidence fields to match the spec.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Protocol, Sequence


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    fields: dict[str, str]


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    input: str
    expected: str


@dataclass(frozen=True)
class RolloutResult:
    candidate_id: str
    case_id: str
    actual: str
    score: float
    asi: dict[str, object]


class AgentExecutor(Protocol):
    def run(self, candidate: Candidate, case: EvalCase) -> str:
        """Return the agent output for one candidate and eval case."""


class TemplateEchoExecutor:
    def run(self, candidate: Candidate, case: EvalCase) -> str:
        del candidate
        return case.input


def score_contains_expected(actual: str, expected: str) -> float:
    return 1.0 if expected and expected in actual else 0.0


def run_case(executor: AgentExecutor, candidate: Candidate, case: EvalCase) -> RolloutResult:
    actual = executor.run(candidate, case)
    score = score_contains_expected(actual, case.expected)
    asi = {
        "Input": case.input,
        "Expected": case.expected,
        "Actual": actual,
        "Feedback": "Expected text was present." if score == 1.0 else "Expected text was missing.",
        "Error": None,
        "scores": {"contains_expected": score},
    }
    return RolloutResult(candidate.candidate_id, case.case_id, actual, score, asi)


def run_suite(executor: AgentExecutor, candidate: Candidate, cases: Sequence[EvalCase]) -> list[RolloutResult]:
    return [run_case(executor, candidate, case) for case in cases]


def write_evidence(results: Sequence[RolloutResult], run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    payload = [asdict(result) for result in results]
    (run_dir / "rollouts.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
