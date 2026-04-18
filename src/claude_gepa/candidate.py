from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

import yaml


DEFAULT_SEED_CANDIDATE: dict[str, str] = {
    "system_prompt": (
        "You are a careful autonomous file-processing agent. "
        "Read the provided task input, reason step by step, and write the final answer "
        "exactly to the requested output path. The output file must contain only the exact final answer, "
        "with no explanations, labels, or extra trailing newline unless the task explicitly requires one."
    ),
    "task_prompt": (
        "Task summary: {task_summary}\n\n"
        "Input file: {input_path}\n"
        "Required output file: {output_path}\n\n"
        "Instructions:\n"
        "1. Read the input file.\n"
        "2. Produce only the requested final answer.\n"
        "3. Write the answer to the required output path.\n"
        "4. Do not add any trailing newline unless the task explicitly requires one.\n"
        "5. Verify the file content matches the intended answer exactly before stopping.\n"
    ),
    "outcome_rubric": (
        "# Output Rubric\n\n"
        "## Required output file\n"
        "- The agent writes the final answer to `{output_path}`.\n"
        "- The output file exists when the task is complete.\n\n"
        "## Output correctness\n"
        "- The file content directly answers the task.\n"
        "- The file content contains no explanation, markdown, or extra framing.\n\n"
        "## Task completion\n"
        "- The agent verifies the result before finishing.\n"
    ),
    "skills": "[]\n",
    "environment_spec": (
        "type: cloud\n"
        "networking:\n"
        "  type: limited\n"
        "  allowed_hosts: []\n"
        "  allow_mcp_servers: false\n"
        "  allow_package_managers: false\n"
        "packages: {}\n"
    ),
    "subagent_specs": "[]\n",
}


def _stable_candidate_json(candidate: dict[str, str]) -> str:
    return json.dumps(candidate, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


@dataclass(frozen=True)
class SkillRef:
    type: str
    skill_id: str
    version: str | None = None

    def to_api(self) -> dict[str, str]:
        payload: dict[str, str] = {"type": self.type, "skill_id": self.skill_id}
        if self.version:
            payload["version"] = self.version
        return payload


@dataclass(frozen=True)
class SubagentSpec:
    name: str
    system_prompt: str
    description: str | None = None
    skills: tuple[SkillRef, ...] = ()


@dataclass(frozen=True)
class EnvironmentSpec:
    config: dict[str, Any]


@dataclass(frozen=True)
class CandidateBundle:
    fields: dict[str, str]
    candidate_id: str
    skills: tuple[SkillRef, ...]
    environment: EnvironmentSpec
    subagents: tuple[SubagentSpec, ...]

    @classmethod
    def from_candidate(cls, candidate: dict[str, str] | str) -> "CandidateBundle":
        if isinstance(candidate, str):
            fields = dict(DEFAULT_SEED_CANDIDATE)
            fields["system_prompt"] = candidate
        else:
            fields = dict(DEFAULT_SEED_CANDIDATE)
            fields.update(candidate)

        candidate_json = _stable_candidate_json(fields)
        candidate_id = sha256(candidate_json.encode("utf-8")).hexdigest()[:12]
        skills = _parse_skills(fields["skills"])
        environment = EnvironmentSpec(config=_parse_environment_spec(fields["environment_spec"]))
        subagents = _parse_subagents(fields["subagent_specs"])
        return cls(
            fields=fields,
            candidate_id=candidate_id,
            skills=skills,
            environment=environment,
            subagents=subagents,
        )

    @property
    def system_prompt(self) -> str:
        return self.fields["system_prompt"]

    def render_task_prompt(self, *, task_summary: str, input_path: str, output_path: str) -> str:
        return self.fields["task_prompt"].format(
            task_summary=task_summary,
            input_path=input_path,
            output_path=output_path,
        )

    def render_outcome_rubric(self, *, output_path: str) -> str:
        return self.fields["outcome_rubric"].format(output_path=output_path)

    def updated_fields(self, **updates: str) -> dict[str, str]:
        merged = dict(self.fields)
        merged.update(updates)
        return merged


def _parse_yaml_text(text: str) -> Any:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return data if data is not None else {}


def _parse_skills(text: str) -> tuple[SkillRef, ...]:
    raw = _parse_yaml_text(text)
    if raw in ({}, None, ""):
        return ()
    if isinstance(raw, dict):
        return ()
    if not isinstance(raw, list):
        return ()
    refs: list[SkillRef] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        if "type" not in item or "skill_id" not in item:
            continue
        refs.append(
            SkillRef(
                type=str(item["type"]),
                skill_id=str(item["skill_id"]),
                version=str(item["version"]) if item.get("version") is not None else None,
            )
        )
    return tuple(refs)


def _parse_environment_spec(text: str) -> dict[str, Any]:
    raw = _parse_yaml_text(text)
    if not isinstance(raw, dict):
        return _parse_environment_spec(DEFAULT_SEED_CANDIDATE["environment_spec"])
    return raw


def _parse_subagents(text: str) -> tuple[SubagentSpec, ...]:
    raw = _parse_yaml_text(text)
    if raw in ({}, None, ""):
        return ()
    if not isinstance(raw, list):
        return ()
    specs: list[SubagentSpec] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        if "name" not in item or "system_prompt" not in item:
            continue
        skills = _parse_skills(yaml.safe_dump(item.get("skills", []), sort_keys=False))
        specs.append(
            SubagentSpec(
                name=str(item["name"]),
                system_prompt=str(item["system_prompt"]),
                description=str(item["description"]) if item.get("description") is not None else None,
                skills=skills,
            )
        )
    return tuple(specs)
