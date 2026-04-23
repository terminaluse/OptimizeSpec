from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Sequence

import yaml

from .self_improvement import (
    EvalCase,
    RolloutResult,
    ScoreResult,
    ScorerSpec,
    compare_candidates,
    evaluate_candidate,
    load_candidate,
    optimize_candidate,
    parse_eval_case,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "gepa-evals" / "fixtures" / "agents"
DEFAULT_RUN_DIR = ROOT / "runs" / "eval-validation"
LIVE_ENV_FLAG = "AGENT_GEPA_EVAL_VALIDATION_LIVE"
REQUIRED_LIVE_ENV = "ANTHROPIC_API_KEY"
MUTABLE_FIELDS = [
    "fixture_analysis_guidance",
    "proposal_generation_guidance",
    "design_generation_guidance",
    "spec_task_generation_guidance",
    "apply_generation_guidance",
    "scoring_asi_guidance",
]
HARD_CONTRACT_KEYS = {
    "fixture_metadata",
    "eval_cases",
    "candidate_fields",
    "rollout_result",
    "score_result",
    "asi",
    "command_evidence",
    "summary",
    "comparison",
}
DEFAULT_REQUIRED_ARTIFACTS = [
    "generated/proposal.md",
    "generated/design.md",
    "generated/specs/eval-validation-spec.md",
    "generated/tasks.md",
    "generated/eval-cases.yaml",
    "generated/seed-candidate.yaml",
    "generated/apply-plan.md",
    "eval/summary.json",
    "compare/comparison.json",
    "optimize/candidates.json",
    "optimize/run_log.txt",
]


class ContractValidationError(ValueError):
    """Raised when a machine-consumed eval-validation contract is malformed."""


@dataclass(frozen=True)
class CommandEvidence:
    args: list[str]
    returncode: int
    stdout_tail: str
    stderr_tail: str
    elapsed_seconds: float
    generated_files: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "args": self.args,
            "returncode": self.returncode,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
            "elapsed_seconds": self.elapsed_seconds,
            "generated_files": self.generated_files,
            "errors": self.errors,
        }


@dataclass(frozen=True)
class FixtureMetadata:
    fixture_id: str
    name: str
    runtime: str
    description: str
    source_files: dict[str, str]
    existing_commands: dict[str, str]
    candidate_fields: list[str]
    expected_behavior: dict[str, Any]
    runtime_facts: list[str] = field(default_factory=list)
    v1_constraints: list[str] = field(default_factory=list)
    fixture_type: str = "positive"
    expected_failure: str | None = None
    requires_live: bool = False
    required_env: list[str] = field(default_factory=list)

    @property
    def is_positive(self) -> bool:
        return self.fixture_type == "positive"


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def dump_yaml(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def read_fixture_request(fixture_id: str) -> str:
    path = FIXTURE_ROOT / fixture_id / "request.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def list_fixture_ids() -> list[str]:
    if not FIXTURE_ROOT.exists():
        return []
    return sorted(path.name for path in FIXTURE_ROOT.iterdir() if (path / "agent.yaml").exists())


def load_fixture(fixture_id: str) -> FixtureMetadata:
    path = FIXTURE_ROOT / fixture_id / "agent.yaml"
    if not path.exists():
        raise ContractValidationError(f"fixture metadata file does not exist: {path}")
    payload = load_yaml(path)
    if not isinstance(payload, dict):
        raise ContractValidationError(f"fixture metadata must be a mapping: {path}")
    return validate_fixture_metadata(payload, fixture_id=fixture_id)


def require_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"fixture metadata field {key!r} must be a non-empty string")
    return value.strip()


def require_str_list(payload: dict[str, Any], key: str, *, allow_empty: bool = False) -> list[str]:
    value = payload.get(key, [])
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ContractValidationError(f"fixture metadata field {key!r} must be a list of non-empty strings")
    if not allow_empty and not value:
        raise ContractValidationError(f"fixture metadata field {key!r} must not be empty")
    return [item.strip() for item in value]


def require_str_mapping(payload: dict[str, Any], key: str, *, allow_empty: bool = False) -> dict[str, str]:
    value = payload.get(key, {})
    if not isinstance(value, dict) or any(not isinstance(k, str) or not isinstance(v, str) or not v.strip() for k, v in value.items()):
        raise ContractValidationError(f"fixture metadata field {key!r} must be a mapping of strings to non-empty strings")
    if not allow_empty and not value:
        raise ContractValidationError(f"fixture metadata field {key!r} must not be empty")
    return {str(k): str(v) for k, v in value.items()}


def validate_fixture_metadata(payload: dict[str, Any], *, fixture_id: str | None = None) -> FixtureMetadata:
    metadata_id = str(payload.get("id") or fixture_id or payload.get("name") or "").strip()
    if not metadata_id:
        raise ContractValidationError("fixture metadata needs an id or name")
    name = require_str(payload, "name")
    runtime = require_str(payload, "runtime")
    description = require_str(payload, "description")
    fixture_type = str(payload.get("fixture_type", "positive")).strip()
    if fixture_type not in {"positive", "negative"}:
        raise ContractValidationError("fixture metadata field 'fixture_type' must be 'positive' or 'negative'")

    source_files = require_str_mapping(payload, "source_files", allow_empty=fixture_type == "negative")
    existing_commands = require_str_mapping(payload, "existing_commands", allow_empty=fixture_type == "negative")
    candidate_fields = require_str_list(payload, "candidate_fields", allow_empty=fixture_type == "negative")
    expected_behavior = payload.get("expected_behavior")
    if not isinstance(expected_behavior, dict):
        raise ContractValidationError("fixture metadata field 'expected_behavior' must be a mapping")

    if fixture_type == "positive":
        required_commands = {"direct_eval", "optimize", "compare", "show_candidate"}
        missing = sorted(required_commands - set(existing_commands))
        if missing:
            raise ContractValidationError(f"positive fixture is missing commands: {', '.join(missing)}")
        if runtime != "Claude Managed Agents":
            raise ContractValidationError("positive validation fixtures must use Claude Managed Agents runtime")

    live = expected_behavior.get("live", {})
    requires_live = bool(live.get("requires_live", False)) if isinstance(live, dict) else False
    required_env = list(live.get("required_env", [])) if isinstance(live, dict) and isinstance(live.get("required_env", []), list) else []
    return FixtureMetadata(
        fixture_id=metadata_id,
        name=name,
        runtime=runtime,
        description=description,
        source_files=source_files,
        existing_commands=existing_commands,
        candidate_fields=candidate_fields,
        expected_behavior=expected_behavior,
        runtime_facts=require_str_list(payload, "runtime_facts", allow_empty=True),
        v1_constraints=require_str_list(payload, "v1_constraints", allow_empty=True),
        fixture_type=fixture_type,
        expected_failure=str(payload.get("expected_failure") or "").strip() or None,
        requires_live=requires_live,
        required_env=[str(item) for item in required_env],
    )


def default_seed_candidate(fixture: FixtureMetadata) -> dict[str, str]:
    files = ", ".join(fixture.source_files.values()) or "the fixture metadata"
    fields = ", ".join(fixture.candidate_fields or MUTABLE_FIELDS)
    commands = ", ".join(fixture.existing_commands.values()) or "no runnable commands"
    return {
        "fixture_analysis_guidance": (
            f"Inspect {fixture.name} before proposing evals. Runtime: {fixture.runtime}. "
            f"Ground the workflow in {files}. Candidate fields: {fields}."
        ),
        "proposal_generation_guidance": (
            "The proposal must state the target agent, eval objective, input examples, expected output examples, "
            "numeric scoring, qualitative rubric, discovery questions, and ASI as a first-class output."
        ),
        "design_generation_guidance": (
            f"The design must name direct eval, optimize, compare, and candidate inspection invocation. "
            f"Existing command references: {commands}. Describe rollout lifecycle, session setup, trace capture, "
            "scorer execution, side_info/ASI, persistence, cleanup, and credential assumptions."
        ),
        "spec_task_generation_guidance": (
            "Specs and tasks must cover fixture validation, eval dataset, candidate surface, rollout executor, "
            "scorers, ASI, GEPA optimization, compare, negative fixtures, validation, and validation docs."
        ),
        "apply_generation_guidance": (
            "The apply plan must expose runnable generate, direct eval, compare, optimize, verify, and show-candidate "
            "operations. It must reuse existing target runtime helpers, block unsupported runtimes, and persist evidence."
        ),
        "scoring_asi_guidance": (
            "Scoring must separate hard contracts for machine-consumed data from semantic scoring for agent-written prose. "
            "ASI must include input, expected, actual, feedback, errors, command traces, generated files, and field-specific feedback."
        ),
    }


def write_seed_candidate(path: Path, fixture: FixtureMetadata) -> dict[str, str]:
    candidate = default_seed_candidate(fixture)
    dump_yaml(path, candidate)
    return candidate


def load_candidate_or_default(path: str | None, fixture: FixtureMetadata) -> dict[str, str]:
    if path:
        candidate = load_candidate(Path(path))
    else:
        candidate = default_seed_candidate(fixture)
    validate_candidate_fields(candidate, MUTABLE_FIELDS)
    return candidate


def validate_candidate_fields(candidate: dict[str, str], mutable_fields: list[str]) -> None:
    if not isinstance(candidate, dict) or not candidate:
        raise ContractValidationError("candidate must be a non-empty mapping")
    bad_values = [key for key, value in candidate.items() if not isinstance(key, str) or not isinstance(value, str)]
    if bad_values:
        raise ContractValidationError(f"candidate fields must be strings: {bad_values}")
    missing = [field for field in mutable_fields if field not in candidate]
    if missing:
        raise ContractValidationError(f"candidate is missing mutable fields: {', '.join(missing)}")


def semantic_checks(fixture: FixtureMetadata) -> dict[str, list[str]]:
    value = fixture.expected_behavior.get("semantic_checks", {})
    if not isinstance(value, dict):
        return {}
    checks: dict[str, list[str]] = {}
    for key, terms in value.items():
        if isinstance(terms, list):
            checks[str(key)] = [str(term) for term in terms]
    return checks


def required_terms_for_artifact(fixture: FixtureMetadata, artifact_type: str) -> list[str]:
    checks = semantic_checks(fixture)
    if artifact_type in checks:
        return checks[artifact_type]
    defaults = {
        "proposal": ["target agent", "eval objective", "input", "expected output", "numeric scoring", "qualitative rubric", "ASI"],
        "design": ["direct eval", "rollout lifecycle", "scorer", "ASI", "GEPA", "compare", "credentials"],
        "specs_tasks": ["candidate surface", "eval dataset", "scorer", "ASI", "GEPA optimization", "validation"],
        "eval_cases": ["train", "val", "input", "expected", "scorer", "metadata"],
        "apply_plan": ["runnable commands", "direct eval", "optimize", "compare", "verify", "unsupported runtimes"],
    }
    return defaults.get(artifact_type, [])


def default_eval_cases(fixture: FixtureMetadata, *, include_system_loop: bool = True) -> list[EvalCase]:
    if not fixture.is_positive:
        expected_failure = fixture.expected_failure or "useful failure"
        return [
            EvalCase(
                case_id=f"{fixture.fixture_id}-negative",
                input=f"Validate negative fixture behavior for {fixture.name}.",
                expected=expected_failure,
                scorer=ScorerSpec(type="custom", expected="negative_fixture_useful_failure"),
                split="test",
                metadata={"artifact_type": "negative", "expected_failure": expected_failure},
            )
        ]

    cases = [
        EvalCase(
            case_id=f"{fixture.fixture_id}-proposal",
            input=f"Generate a proposal for {fixture.name}.",
            expected=", ".join(required_terms_for_artifact(fixture, "proposal")),
            scorer=ScorerSpec(type="custom", expected="semantic_required_concepts"),
            split="train",
            metadata={"artifact_type": "proposal", "required_terms": required_terms_for_artifact(fixture, "proposal")},
        ),
        EvalCase(
            case_id=f"{fixture.fixture_id}-design",
            input=f"Generate a design for {fixture.name}.",
            expected=", ".join(required_terms_for_artifact(fixture, "design")),
            scorer=ScorerSpec(type="custom", expected="semantic_required_concepts"),
            split="train",
            metadata={"artifact_type": "design", "required_terms": required_terms_for_artifact(fixture, "design")},
        ),
        EvalCase(
            case_id=f"{fixture.fixture_id}-specs-tasks",
            input=f"Generate specs and tasks for {fixture.name}.",
            expected=", ".join(required_terms_for_artifact(fixture, "specs_tasks")),
            scorer=ScorerSpec(type="custom", expected="semantic_required_concepts"),
            split="val",
            metadata={"artifact_type": "specs_tasks", "required_terms": required_terms_for_artifact(fixture, "specs_tasks")},
        ),
        EvalCase(
            case_id=f"{fixture.fixture_id}-eval-cases",
            input=f"Generate eval cases for {fixture.name}.",
            expected=", ".join(required_terms_for_artifact(fixture, "eval_cases")),
            scorer=ScorerSpec(type="custom", expected="eval_cases_artifact_quality"),
            split="val",
            metadata={"artifact_type": "eval_cases", "required_terms": required_terms_for_artifact(fixture, "eval_cases")},
        ),
        EvalCase(
            case_id=f"{fixture.fixture_id}-apply-plan",
            input=f"Generate an apply plan for {fixture.name}.",
            expected=", ".join(required_terms_for_artifact(fixture, "apply_plan")),
            scorer=ScorerSpec(type="custom", expected="semantic_required_concepts"),
            split="val",
            metadata={"artifact_type": "apply_plan", "required_terms": required_terms_for_artifact(fixture, "apply_plan")},
        ),
    ]
    if include_system_loop:
        cases.append(
            EvalCase(
                case_id=f"{fixture.fixture_id}-system-loop",
                input=f"Run the eval workflow validation system loop for {fixture.name}.",
                expected="SYSTEM_LOOP_SUCCESS",
                scorer=ScorerSpec(type="custom", expected="system_loop_success"),
                split="test",
                metadata={"artifact_type": "system_loop", "required_terms": ["SYSTEM_LOOP_SUCCESS"]},
            )
        )
    return cases


def write_eval_cases(path: Path, fixture: FixtureMetadata, *, include_system_loop: bool = True) -> list[EvalCase]:
    cases = default_eval_cases(fixture, include_system_loop=include_system_loop)
    payload = {"cases": [serialize_eval_case(case) for case in cases]}
    dump_yaml(path, payload)
    return cases


def serialize_eval_case(case: EvalCase) -> dict[str, Any]:
    return {
        "id": case.case_id,
        "split": case.split,
        "input": case.input,
        "expected": case.expected,
        "scorer": {"type": case.scorer.type, "expected": case.scorer.expected, "rubric": case.scorer.rubric},
        "metadata": case.metadata,
    }


def load_eval_cases_strict(path: Path, custom_scorers: dict[str, Any]) -> list[EvalCase]:
    payload = load_yaml(path)
    raw_cases = payload.get("cases", payload) if isinstance(payload, dict) else payload
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ContractValidationError("eval cases must contain a non-empty cases list")
    cases: list[EvalCase] = []
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            raise ContractValidationError("each eval case must be a mapping")
        case = parse_eval_case(raw_case)
        if case.scorer.type == "custom" and str(case.scorer.expected) not in custom_scorers:
            raise ContractValidationError(f"eval case {case.case_id} references unknown custom scorer {case.scorer.expected!r}")
        if case.input is None:
            raise ContractValidationError(f"eval case {case.case_id} is missing input")
        if case.expected is None and case.expected_shape is None:
            raise ContractValidationError(f"eval case {case.case_id} is missing expected output or expected_shape")
        cases.append(case)
    if not any(case.split == "train" for case in cases) and len(cases) > 1:
        raise ContractValidationError("eval cases need at least one train split")
    return cases


def required_terms(case: EvalCase) -> list[str]:
    terms = case.metadata.get("required_terms", [])
    if not isinstance(terms, list):
        return []
    return [str(term) for term in terms]


def semantic_required_concepts_scorer(case: EvalCase, rollout: RolloutResult) -> ScoreResult:
    terms = required_terms(case)
    actual = str(rollout.actual or "").lower()
    matched = [term for term in terms if term.lower() in actual]
    missing = [term for term in terms if term not in matched]
    score = len(matched) / max(len(terms), 1)
    return ScoreResult(
        score=score,
        feedback=(
            f"Matched all {len(terms)} semantic concepts."
            if not missing
            else f"Matched {len(matched)}/{len(terms)} semantic concepts. Missing: {', '.join(missing)}."
        ),
        subscores={"semantic_concept_coverage": score, "missing_concepts": float(len(missing))},
    )


def eval_cases_artifact_quality_scorer(case: EvalCase, rollout: RolloutResult) -> ScoreResult:
    semantic = semantic_required_concepts_scorer(case, rollout)
    try:
        payload = yaml.safe_load(str(rollout.actual or "")) or {}
        raw_cases = payload.get("cases", payload) if isinstance(payload, dict) else payload
        parsed = [parse_eval_case(item) for item in raw_cases]
        split_ok = bool({item.split for item in parsed} & {"val", "test"}) and any(item.split == "train" for item in parsed)
        scorer_ok = all(item.scorer.type for item in parsed)
        structure_score = 1.0 if parsed and split_ok and scorer_ok else 0.0
        feedback = semantic.feedback if structure_score == 1.0 else "Eval-case artifact parsed but lacks train plus val/test splits or scorer definitions."
    except Exception as exc:
        structure_score = 0.0
        feedback = f"Eval-case artifact failed hard contract parsing: {exc}"
    score = (semantic.score + structure_score) / 2.0
    return ScoreResult(
        score=score,
        feedback=feedback,
        subscores={**semantic.subscores, "eval_case_structure": structure_score},
    )


def system_loop_success_scorer(case: EvalCase, rollout: RolloutResult) -> ScoreResult:
    actual = str(rollout.actual or "")
    success = "SYSTEM_LOOP_SUCCESS" in actual and not rollout.errors
    return ScoreResult(
        score=1.0 if success else 0.0,
        feedback="System loop completed." if success else "System loop did not complete.",
        subscores={"system_loop_success": 1.0 if success else 0.0},
    )


def negative_fixture_useful_failure_scorer(case: EvalCase, rollout: RolloutResult) -> ScoreResult:
    actual = str(rollout.actual or "").lower()
    expected = str(case.metadata.get("expected_failure") or case.expected or "").lower()
    markers = ["blocked", "clarification", "unsupported", "missing", "invalid", "unsafe"]
    marker_hit = any(marker in actual for marker in markers)
    expected_hit = bool(expected and expected in actual)
    score = 1.0 if marker_hit and (expected_hit or not expected) else 0.0
    return ScoreResult(
        score=score,
        feedback="Negative fixture failed usefully." if score == 1.0 else "Negative fixture did not preserve useful failure diagnostics.",
        subscores={"useful_failure": score},
    )


def custom_scorers() -> dict[str, Any]:
    return {
        "semantic_required_concepts": semantic_required_concepts_scorer,
        "eval_cases_artifact_quality": eval_cases_artifact_quality_scorer,
        "system_loop_success": system_loop_success_scorer,
        "negative_fixture_useful_failure": negative_fixture_useful_failure_scorer,
    }


class EvalValidationExecutor:
    def __init__(self, *, fixture: FixtureMetadata, run_dir: Path, live: bool = False) -> None:
        self.fixture = fixture
        self.run_dir = run_dir
        self.live = live

    def run(self, candidate: dict[str, str], case: EvalCase, *, timeout_seconds: float) -> RolloutResult:
        started = time.monotonic()
        artifact_type = str(case.metadata.get("artifact_type", "proposal"))
        try:
            if artifact_type == "system_loop":
                actual, trace, generated_files, errors = run_system_loop(self.fixture, self.run_dir, timeout_seconds=timeout_seconds)
            elif artifact_type == "negative":
                actual = render_negative_response(self.fixture)
                trace = [{"action": "score_negative_fixture", "expected_failure": self.fixture.expected_failure}]
                generated_files = {}
                errors = []
            else:
                actual = render_artifact(artifact_type, self.fixture, candidate)
                trace = [{"action": "render_artifact", "artifact_type": artifact_type, "fixture": self.fixture.fixture_id}]
                generated_files = {artifact_path_for_type(artifact_type): actual}
                errors = []
        except Exception as exc:
            actual = ""
            trace = [{"action": "eval_validation_executor_error", "artifact_type": artifact_type, "error": str(exc)}]
            generated_files = {}
            errors = [str(exc)]
        ended = time.monotonic()
        rollout = RolloutResult(
            case_id=case.case_id,
            actual=actual,
            final_answer=actual,
            generated_files=generated_files,
            trajectory=trace,
            runtime_ids={"executor": "eval-validation", "fixture": self.fixture.fixture_id},
            usage={
                "input_tokens": len(str(case.input).split()),
                "output_tokens": len(str(actual).split()),
            },
            errors=errors,
            started_at=started,
            ended_at=ended,
        )
        validate_rollout_result(rollout)
        return rollout


def artifact_path_for_type(artifact_type: str) -> str:
    return {
        "proposal": "proposal.md",
        "design": "design.md",
        "specs_tasks": "specs/eval-validation-spec.md",
        "eval_cases": "eval-cases.yaml",
        "apply_plan": "apply-plan.md",
    }.get(artifact_type, f"{artifact_type}.txt")


def render_artifact(artifact_type: str, fixture: FixtureMetadata, candidate: dict[str, str]) -> str:
    guidance = "\n\n".join(candidate.get(field, "") for field in MUTABLE_FIELDS if candidate.get(field)).strip()
    source_files = ", ".join(fixture.source_files.values()) or "missing source files"
    commands = ", ".join(f"{key}: {value}" for key, value in fixture.existing_commands.items()) or "missing invocation details"
    fields = ", ".join(fixture.candidate_fields or MUTABLE_FIELDS)
    if artifact_type == "proposal":
        return f"""## Target Agent

Target agent: {fixture.name}. Runtime: {fixture.runtime}. Source files: {source_files}.

## Eval Objective

Create evals for the target agent with concrete input examples, expected output examples, numeric scoring from 0.0 to 1.0, qualitative rubric feedback, discovery questions, and ASI.

## Candidate Surface

Candidate fields: {fields}. GEPA treats the candidate as dict[str, str].

## Guidance

{guidance}
"""
    if artifact_type == "design":
        return f"""## Runner Invocation

Existing commands: {commands}. The validation harness must expose direct eval, compare, optimize, verify, and candidate inspection.

## Rollout Lifecycle

One rollout loads a candidate and eval case, starts the Claude Managed Agents session or deterministic fixture executor, captures trace data, runs the scorer, builds side_info and ASI, persists artifacts, and performs cleanup.

## Optimizer

GEPA optimization uses optimize_candidate and optimize_anything with train/val splits, objective, background, max_metric_calls, command evidence, run logs, and candidate outputs.

## Credentials

Live Claude Managed Agents validation requires {REQUIRED_LIVE_ENV}; deterministic validation does not require live credentials.

## Guidance

{guidance}
"""
    if artifact_type == "specs_tasks":
        return f"""## ADDED Requirements

### Requirement: Eval workflow validation covers candidate surface and eval dataset
The system SHALL validate the candidate surface, eval dataset, scorer behavior, Managed Agent runner, ASI, GEPA optimization, compare, negative fixtures, and validation documentation for {fixture.name}.

#### Scenario: Validation runs
- **WHEN** direct eval, compare, optimize, and verify run for {fixture.fixture_id}
- **THEN** validation evidence is persisted and scored.

## Tasks

- [ ] Implement fixture validation
- [ ] Implement eval dataset and scorer behavior
- [ ] Implement ASI and GEPA optimization
- [ ] Implement compare, validation, negative fixtures, and validation docs

## Guidance

{guidance}
"""
    if artifact_type == "eval_cases":
        payload = {
            "cases": [
                {
                    "id": "artifact-quality-train",
                    "split": "train",
                    "input": "Generate eval artifacts for the fixture.",
                    "expected": "input expected scorer metadata",
                    "scorer": {"type": "custom", "expected": "semantic_required_concepts"},
                    "metadata": {"required_terms": ["input", "expected", "scorer", "metadata"]},
                },
                {
                    "id": "runner-validation-val",
                    "split": "val",
                    "input": "Run direct eval and compare.",
                    "expected": "train val scorer side_info",
                    "scorer": {"type": "custom", "expected": "semantic_required_concepts"},
                    "metadata": {"required_terms": ["train", "val", "scorer", "side_info"]},
                },
            ]
        }
        return yaml.safe_dump(payload, sort_keys=False)
    if artifact_type == "apply_plan":
        return f"""## Apply Plan

Expose runnable commands for generate, direct eval, compare, optimize, verify, and show candidate. Reuse the target repo runtime helpers where possible. Persist summary.json, comparison.json, candidates.json, run_log.txt, side_info.json, command evidence, and generated files.

Unsupported runtimes are blocked. Live Managed Agents require {REQUIRED_LIVE_ENV}; deterministic fixtures remain the default.

## Command Shape

python -m agent_gepa.eval_validation generate --fixture {fixture.fixture_id} --run-dir runs/eval-validation/{fixture.fixture_id}
python -m agent_gepa.eval_validation eval --fixture {fixture.fixture_id} --run-dir runs/eval-validation/{fixture.fixture_id}
python -m agent_gepa.eval_validation compare --fixture {fixture.fixture_id} --run-dir runs/eval-validation/{fixture.fixture_id}
python -m agent_gepa.eval_validation optimize --fixture {fixture.fixture_id} --max-metric-calls 1 --run-dir runs/eval-validation/{fixture.fixture_id}
python -m agent_gepa.eval_validation verify --fixture {fixture.fixture_id} --run-dir runs/eval-validation/{fixture.fixture_id}

## Guidance

{guidance}
"""
    return guidance


def render_negative_response(fixture: FixtureMetadata) -> str:
    reason = fixture.expected_failure or "missing required information"
    if fixture.runtime != "Claude Managed Agents":
        return f"BLOCKED: unsupported runtime for v1. Expected Claude Managed Agents but got {fixture.runtime}. {reason}."
    return f"BLOCKED: clarification required before optimization. Missing or invalid details: {reason}."


def generate_artifacts(fixture: FixtureMetadata, run_dir: Path, candidate: dict[str, str] | None = None) -> dict[str, str]:
    active_candidate = candidate or default_seed_candidate(fixture)
    validate_candidate_fields(active_candidate, MUTABLE_FIELDS)
    out_dir = run_dir / "generated"
    rendered = {
        "proposal.md": render_artifact("proposal", fixture, active_candidate),
        "design.md": render_artifact("design", fixture, active_candidate),
        "specs/eval-validation-spec.md": render_artifact("specs_tasks", fixture, active_candidate),
        "tasks.md": render_artifact("specs_tasks", fixture, active_candidate),
        "eval-cases.yaml": render_artifact("eval_cases", fixture, active_candidate),
        "apply-plan.md": render_artifact("apply_plan", fixture, active_candidate),
    }
    for relative, text in rendered.items():
        path = out_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    write_seed_candidate(out_dir / "seed-candidate.yaml", fixture)
    write_eval_cases(out_dir / "eval-validation-cases.yaml", fixture)
    evidence = {
        "fixture": fixture.fixture_id,
        "generated_files": sorted(str((out_dir / relative).relative_to(run_dir)) for relative in rendered),
        "hard_contracts": sorted(HARD_CONTRACT_KEYS),
        "semantic_contracts": ["proposal", "design", "specs", "tasks", "apply_plan"],
    }
    (out_dir / "generation-summary.json").write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    return rendered


def command_evidence_path(run_dir: Path, name: str) -> Path:
    return run_dir / "command-logs" / f"{name}.json"


def run_command(args: list[str], *, cwd: Path, timeout_seconds: float, generated_root: Path | None = None) -> CommandEvidence:
    started = time.monotonic()
    errors: list[str] = []
    env = os.environ.copy()
    src_path = str(ROOT / "src")
    env["PYTHONPATH"] = src_path if not env.get("PYTHONPATH") else f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    try:
        completed = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=timeout_seconds, env=env)
        returncode = completed.returncode
        stdout_tail = completed.stdout[-2000:]
        stderr_tail = completed.stderr[-2000:]
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        stdout_tail = (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else ""
        stderr_tail = (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else ""
        errors.append(f"timeout after {timeout_seconds} seconds")
    generated_files: list[str] = []
    if generated_root and generated_root.exists():
        generated_files = sorted(str(path.relative_to(generated_root)) for path in generated_root.rglob("*") if path.is_file())
    evidence = CommandEvidence(
        args=args,
        returncode=returncode,
        stdout_tail=stdout_tail,
        stderr_tail=stderr_tail,
        elapsed_seconds=time.monotonic() - started,
        generated_files=generated_files,
        errors=errors,
    )
    validate_command_evidence(evidence.to_dict())
    return evidence


def persist_command_evidence(run_dir: Path, name: str, evidence: CommandEvidence) -> None:
    path = command_evidence_path(run_dir, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


def persist_self_command_evidence(run_dir: Path, name: str, started_at: float, generated_files: list[str] | None = None) -> None:
    evidence = CommandEvidence(
        args=list(sys.argv),
        returncode=0,
        stdout_tail="",
        stderr_tail="",
        elapsed_seconds=max(time.monotonic() - started_at, 0.0),
        generated_files=generated_files or [],
        errors=[],
    )
    validate_command_evidence(evidence.to_dict())
    persist_command_evidence(run_dir, name, evidence)


def run_system_loop(fixture: FixtureMetadata, parent_run_dir: Path, *, timeout_seconds: float) -> tuple[str, list[dict[str, Any]], dict[str, str], list[str]]:
    stamp = f"{fixture.fixture_id}-{int(time.time() * 1000)}"
    work_dir = parent_run_dir / "system-loop" / stamp
    work_dir.mkdir(parents=True, exist_ok=True)
    command_timeout = max(timeout_seconds, 30.0)
    commands = {
        "generate": [
            sys.executable,
            "-m",
            "agent_gepa.eval_validation",
            "generate",
            "--fixture",
            fixture.fixture_id,
            "--run-dir",
            str(work_dir),
        ],
        "eval": [
            sys.executable,
            "-m",
            "agent_gepa.eval_validation",
            "eval",
            "--fixture",
            fixture.fixture_id,
            "--run-dir",
            str(work_dir),
            "--skip-system-loop",
        ],
        "compare": [
            sys.executable,
            "-m",
            "agent_gepa.eval_validation",
            "compare",
            "--fixture",
            fixture.fixture_id,
            "--run-dir",
            str(work_dir),
            "--skip-system-loop",
        ],
        "optimize": [
            sys.executable,
            "-m",
            "agent_gepa.eval_validation",
            "optimize",
            "--fixture",
            fixture.fixture_id,
            "--run-dir",
            str(work_dir),
            "--max-metric-calls",
            "1",
            "--skip-system-loop",
        ],
    }
    evidence: dict[str, CommandEvidence] = {}
    for name, args in commands.items():
        result = run_command(args, cwd=ROOT, timeout_seconds=command_timeout, generated_root=work_dir)
        persist_command_evidence(work_dir, name, result)
        evidence[name] = result

    verification = verify_run_dir(fixture, work_dir, require_live=False)
    expected_files = required_artifacts(fixture)
    missing = [path for path in expected_files if not (work_dir / path).exists()]
    failed = [name for name, item in evidence.items() if item.returncode != 0]
    success = verification["success"] and not missing and not failed
    marker = "SYSTEM_LOOP_SUCCESS" if success else "SYSTEM_LOOP_FAILURE"
    text = (
        f"{marker}\n"
        f"fixture: {fixture.fixture_id}\n"
        f"work_dir: {display_path(work_dir)}\n"
        f"failed_commands: {failed}\n"
        f"missing_files: {missing}\n"
    )
    trace = [
        {
            "action": "run_eval_validation_system_loop",
            "work_dir": display_path(work_dir),
            "commands": {name: item.to_dict() for name, item in evidence.items()},
            "verification": verification,
            "missing_files": missing,
            "success": success,
        }
    ]
    generated_files = {str(path.relative_to(work_dir)): path.read_text(encoding="utf-8", errors="ignore")[:2000] for path in work_dir.rglob("*") if path.is_file()}
    errors = [] if success else [f"failed_commands={failed}; missing_files={missing}"]
    return text, trace, generated_files, errors


def required_artifacts(fixture: FixtureMetadata) -> list[str]:
    value = fixture.expected_behavior.get("required_artifacts")
    if isinstance(value, list) and value:
        return [str(item) for item in value]
    return list(DEFAULT_REQUIRED_ARTIFACTS)


def display_path(path: Path, base: Path = ROOT) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def require_live_ready(fixture: FixtureMetadata, *, live: bool) -> None:
    if not fixture.requires_live:
        return
    if not live:
        raise ContractValidationError(f"fixture {fixture.fixture_id} requires live validation; set {LIVE_ENV_FLAG}=1 or pass --live")
    missing = [name for name in (fixture.required_env or [REQUIRED_LIVE_ENV]) if not os.environ.get(name)]
    if missing:
        raise ContractValidationError(f"live validation requires environment variables: {', '.join(missing)}")


def validate_rollout_result(rollout: RolloutResult) -> None:
    if not isinstance(rollout.case_id, str) or not rollout.case_id:
        raise ContractValidationError("rollout result requires a case_id")
    if not isinstance(rollout.generated_files, dict):
        raise ContractValidationError("rollout generated_files must be a mapping")
    if not isinstance(rollout.trajectory, list):
        raise ContractValidationError("rollout trajectory must be a list")
    if not isinstance(rollout.errors, list):
        raise ContractValidationError("rollout errors must be a list")


def validate_score_result(score: ScoreResult) -> None:
    if not isinstance(score.score, (float, int)) or not 0.0 <= float(score.score) <= 1.0:
        raise ContractValidationError("score result score must be a number from 0.0 to 1.0")
    if not isinstance(score.feedback, str):
        raise ContractValidationError("score result feedback must be a string")
    if not isinstance(score.subscores, dict):
        raise ContractValidationError("score result subscores must be a mapping")


def validate_side_info(side_info: dict[str, Any]) -> None:
    required = {"Input", "Expected", "Actual", "Feedback", "Error", "Agent Trajectory", "Runtime", "scores"}
    missing = sorted(required - set(side_info))
    if missing:
        raise ContractValidationError(f"ASI is missing keys: {', '.join(missing)}")
    if not isinstance(side_info["scores"], dict):
        raise ContractValidationError("ASI scores must be a mapping")


def validate_summary(payload: dict[str, Any]) -> None:
    for key in ("mean_score", "mean_train_score", "mean_val_score", "mean_test_score", "cases"):
        if key not in payload:
            raise ContractValidationError(f"summary is missing {key!r}")
    if not isinstance(payload["cases"], list):
        raise ContractValidationError("summary cases must be a list")


def validate_comparison(payload: dict[str, Any]) -> None:
    for key in ("baseline", "candidate", "candidate_diff", "deltas"):
        if key not in payload:
            raise ContractValidationError(f"comparison is missing {key!r}")
    if not isinstance(payload["deltas"], list):
        raise ContractValidationError("comparison deltas must be a list")


def validate_command_evidence(payload: dict[str, Any]) -> None:
    for key in ("args", "returncode", "stdout_tail", "stderr_tail", "elapsed_seconds", "generated_files", "errors"):
        if key not in payload:
            raise ContractValidationError(f"command evidence is missing {key!r}")
    if not isinstance(payload["args"], list) or not isinstance(payload["returncode"], int):
        raise ContractValidationError("command evidence args and returncode have invalid types")


def validate_run_artifacts(run_dir: Path) -> list[str]:
    errors: list[str] = []
    for relative, validator in {
        "eval/summary.json": validate_summary,
        "compare/comparison.json": validate_comparison,
    }.items():
        path = run_dir / relative
        if path.exists():
            try:
                validator(json.loads(path.read_text(encoding="utf-8")))
            except Exception as exc:
                errors.append(f"{relative}: {exc}")
        else:
            errors.append(f"{relative}: missing")
    for path in (run_dir / "command-logs").glob("*.json") if (run_dir / "command-logs").exists() else []:
        try:
            validate_command_evidence(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            errors.append(f"{path.relative_to(run_dir)}: {exc}")
    return errors


def verify_run_dir(fixture: FixtureMetadata, run_dir: Path, *, require_live: bool = False) -> dict[str, Any]:
    if require_live:
        require_live_ready(fixture, live=True)
    expected_files = required_artifacts(fixture)
    missing = [relative for relative in expected_files if not (run_dir / relative).exists()]
    contract_errors = validate_run_artifacts(run_dir)
    payload = {
        "fixture": fixture.fixture_id,
        "run_dir": str(run_dir),
        "expected_files": expected_files,
        "missing_files": missing,
        "contract_errors": contract_errors,
        "success": not missing and not contract_errors,
    }
    out = run_dir / "verification" / "verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def cmd_generate(fixture_id: str, run_dir: str, candidate_path: str | None, live: bool) -> int:
    started = time.monotonic()
    fixture = load_fixture(fixture_id)
    require_live_ready(fixture, live=live)
    run_path = Path(run_dir)
    candidate = load_candidate_or_default(candidate_path, fixture)
    generated = generate_artifacts(fixture, run_path, candidate)
    persist_self_command_evidence(run_path, "generate", started, [f"generated/{path}" for path in sorted(generated)])
    payload = {"fixture": fixture.fixture_id, "run_dir": str(run_path), "files": sorted(generated)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_eval(fixture_id: str, run_dir: str, candidate_path: str | None, cases_path: str | None, timeout_seconds: float, skip_system_loop: bool, live: bool) -> int:
    started = time.monotonic()
    fixture = load_fixture(fixture_id)
    require_live_ready(fixture, live=live)
    run_path = Path(run_dir)
    candidate = load_candidate_or_default(candidate_path, fixture)
    if cases_path:
        cases = load_eval_cases_strict(Path(cases_path), custom_scorers())
    else:
        cases = default_eval_cases(fixture, include_system_loop=not skip_system_loop)
    summary = evaluate_candidate(
        candidate=candidate,
        cases=cases,
        executor=EvalValidationExecutor(fixture=fixture, run_dir=run_path, live=live),
        run_dir=run_path / "eval",
        candidate_id="candidate",
        timeout_seconds=timeout_seconds,
        mutable_fields=MUTABLE_FIELDS,
        custom_scorers=custom_scorers(),
    )
    validate_summary(summary)
    persist_self_command_evidence(run_path, "eval", started, ["eval/summary.json"])
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def cmd_compare(
    fixture_id: str,
    run_dir: str,
    baseline_path: str | None,
    candidate_path: str | None,
    cases_path: str | None,
    timeout_seconds: float,
    skip_system_loop: bool,
    live: bool,
) -> int:
    started = time.monotonic()
    fixture = load_fixture(fixture_id)
    require_live_ready(fixture, live=live)
    run_path = Path(run_dir)
    baseline = load_candidate_or_default(baseline_path, fixture)
    candidate = load_candidate_or_default(candidate_path, fixture)
    cases = load_eval_cases_strict(Path(cases_path), custom_scorers()) if cases_path else default_eval_cases(fixture, include_system_loop=not skip_system_loop)
    comparison = compare_candidates(
        baseline=baseline,
        candidate=candidate,
        cases=cases,
        executor=EvalValidationExecutor(fixture=fixture, run_dir=run_path, live=live),
        run_dir=run_path / "compare",
        timeout_seconds=timeout_seconds,
        custom_scorers=custom_scorers(),
    )
    validate_comparison(comparison)
    persist_self_command_evidence(run_path, "compare", started, ["compare/comparison.json"])
    print(json.dumps(comparison, indent=2, sort_keys=True))
    return 0


def cmd_optimize(
    fixture_id: str,
    run_dir: str,
    candidate_path: str | None,
    cases_path: str | None,
    max_metric_calls: int,
    reflection_model: str,
    timeout_seconds: float,
    skip_system_loop: bool,
    live: bool,
    release_budget: bool,
) -> int:
    started = time.monotonic()
    fixture = load_fixture(fixture_id)
    require_live_ready(fixture, live=live)
    run_path = Path(run_dir)
    candidate = load_candidate_or_default(candidate_path, fixture)
    cases = load_eval_cases_strict(Path(cases_path), custom_scorers()) if cases_path else default_eval_cases(fixture, include_system_loop=not skip_system_loop)
    if release_budget:
        max_metric_calls = max(max_metric_calls, 12)
    result = optimize_candidate(
        seed_candidate=candidate,
        cases=cases,
        executor=EvalValidationExecutor(fixture=fixture, run_dir=run_path, live=live),
        run_dir=run_path / "optimize",
        objective=f"Improve eval workflow validation guidance for {fixture.name}.",
        background=(
            "The candidate is a dict[str, str] guidance surface. Hard contracts apply to fixture metadata, eval cases, "
            "candidate fields, rollout results, score results, ASI, command evidence, and summaries. Prose artifacts use semantic scoring."
        ),
        reflection_model=reflection_model,
        max_metric_calls=max_metric_calls,
        timeout_seconds=timeout_seconds,
        mutable_fields=MUTABLE_FIELDS,
        custom_scorers=custom_scorers(),
    )
    payload = {"fixture": fixture.fixture_id, "best_candidate": dict(result.best_candidate), "max_metric_calls": max_metric_calls}
    (run_path / "optimize" / "eval-validation-result.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    persist_self_command_evidence(run_path, "optimize", started, ["optimize/eval-validation-result.json"])
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_verify(fixture_id: str, run_dir: str, live: bool) -> int:
    started = time.monotonic()
    fixture = load_fixture(fixture_id)
    payload = verify_run_dir(fixture, Path(run_dir), require_live=live and fixture.requires_live)
    persist_self_command_evidence(Path(run_dir), "verify", started, ["verification/verification.json"])
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["success"] else 1


def cmd_show_fixture(fixture_id: str | None, pretty: bool) -> int:
    if fixture_id:
        payload = load_fixture(fixture_id).__dict__
    else:
        payload = {"fixtures": list_fixture_ids()}
    print(json.dumps(payload, indent=2 if pretty else None, sort_keys=pretty))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m agent_gepa.eval_validation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show = subparsers.add_parser("show-fixture")
    show.add_argument("--fixture")
    show.add_argument("--pretty", action="store_true")

    generate = subparsers.add_parser("generate")
    generate.add_argument("--fixture", required=True)
    generate.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    generate.add_argument("--candidate")
    generate.add_argument("--live", action="store_true")

    direct_eval = subparsers.add_parser("eval")
    direct_eval.add_argument("--fixture", required=True)
    direct_eval.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    direct_eval.add_argument("--candidate")
    direct_eval.add_argument("--cases")
    direct_eval.add_argument("--timeout-seconds", type=float, default=120.0)
    direct_eval.add_argument("--skip-system-loop", action="store_true")
    direct_eval.add_argument("--live", action="store_true")

    compare = subparsers.add_parser("compare")
    compare.add_argument("--fixture", required=True)
    compare.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    compare.add_argument("--baseline")
    compare.add_argument("--candidate")
    compare.add_argument("--cases")
    compare.add_argument("--timeout-seconds", type=float, default=120.0)
    compare.add_argument("--skip-system-loop", action="store_true")
    compare.add_argument("--live", action="store_true")

    optimize = subparsers.add_parser("optimize")
    optimize.add_argument("--fixture", required=True)
    optimize.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    optimize.add_argument("--candidate")
    optimize.add_argument("--cases")
    optimize.add_argument("--max-metric-calls", type=int, default=1)
    optimize.add_argument("--reflection-model", default="anthropic/claude-opus-4-7")
    optimize.add_argument("--timeout-seconds", type=float, default=120.0)
    optimize.add_argument("--skip-system-loop", action="store_true")
    optimize.add_argument("--release-budget", action="store_true")
    optimize.add_argument("--live", action="store_true")

    verify = subparsers.add_parser("verify")
    verify.add_argument("--fixture", required=True)
    verify.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    verify.add_argument("--live", action="store_true")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    live = bool(getattr(args, "live", False) or os.environ.get(LIVE_ENV_FLAG) == "1")
    try:
        if args.command == "show-fixture":
            return cmd_show_fixture(args.fixture, args.pretty)
        if args.command == "generate":
            return cmd_generate(args.fixture, args.run_dir, args.candidate, live)
        if args.command == "eval":
            return cmd_eval(args.fixture, args.run_dir, args.candidate, args.cases, args.timeout_seconds, args.skip_system_loop, live)
        if args.command == "compare":
            return cmd_compare(args.fixture, args.run_dir, args.baseline, args.candidate, args.cases, args.timeout_seconds, args.skip_system_loop, live)
        if args.command == "optimize":
            return cmd_optimize(
                args.fixture,
                args.run_dir,
                args.candidate,
                args.cases,
                args.max_metric_calls,
                args.reflection_model,
                args.timeout_seconds,
                args.skip_system_loop,
                live,
                args.release_budget,
            )
        if args.command == "verify":
            return cmd_verify(args.fixture, args.run_dir, live)
    except ContractValidationError as exc:
        print(json.dumps({"error": str(exc), "contract_error": True}, indent=2, sort_keys=True), file=sys.stderr)
        return 2
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
