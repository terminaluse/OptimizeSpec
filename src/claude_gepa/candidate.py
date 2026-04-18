from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import mimetypes
from pathlib import PurePosixPath
import re
from typing import Any, Literal, Protocol, TypeAlias

import anthropic
from pydantic import BaseModel, Field
import yaml


DEFAULT_MODEL = "claude-opus-4-7"
SKILL_NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")

DEFAULT_SEED_CANDIDATE: dict[str, str] = {
    "system_prompt": (
        "You are a careful autonomous file-processing agent. "
        "Read the provided task input, reason step by step, and write the final answer "
        "exactly to the requested output path. The output file must contain only the exact final answer, "
        "with no explanations, labels, or extra trailing newline unless the task explicitly requires one. "
        "If callable agents are available, use them for tightly scoped review or verification work."
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
        "6. If specialist skills or callable agents are available and relevant, use them deliberately.\n"
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
        "packages:\n"
        "  type: packages\n"
        "  apt: []\n"
        "  cargo: []\n"
        "  gem: []\n"
        "  go: []\n"
        "  npm: []\n"
        "  pip: []\n"
    ),
    "subagent_specs": "[]\n",
}

CANDIDATE_FIELD_NAMES: tuple[str, ...] = (
    "system_prompt",
    "task_prompt",
    "outcome_rubric",
    "skills",
    "environment_spec",
    "subagent_specs",
)

COMPILER_SYSTEM_PROMPT = """You compile Claude Managed Agents candidate dictionaries into a typed configuration.
Preserve system_prompt, task_prompt, and outcome_rubric exactly as provided.
Parse the skills, environment_spec, and subagent_specs text into the requested schema.
The skills field is hybrid:
- Reusable skill refs use {type, skill_id, version?}.
- Custom skill definitions use {type: "custom", display_title?, files:[{path, content, media_type?}]}.
For custom skills, all files must share one top-level directory and include SKILL.md at that directory root.
Subagents use the same hybrid skill schema for their nested skills list.
If a structured field cannot be parsed faithfully, set is_valid to false and include an error entry.
Do not invent missing structured values beyond obvious empty defaults.
Return only schema-conforming data."""


def _stable_candidate_json(candidate: dict[str, Any]) -> str:
    return json.dumps(candidate, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def normalize_candidate_fields(candidate: dict[str, str] | str) -> dict[str, str]:
    if isinstance(candidate, str):
        fields = dict(DEFAULT_SEED_CANDIDATE)
        fields["system_prompt"] = candidate
        return fields

    fields = dict(DEFAULT_SEED_CANDIDATE)
    fields.update(candidate)
    return fields


@dataclass(frozen=True)
class SkillRef:
    type: Literal["anthropic", "custom"]
    skill_id: str
    version: str | None = None

    def to_api(self) -> dict[str, str]:
        payload: dict[str, str] = {"type": self.type, "skill_id": self.skill_id}
        if self.version:
            payload["version"] = self.version
        return payload


@dataclass(frozen=True)
class SkillFile:
    path: str
    content: str
    media_type: str | None = None

    @property
    def normalized_path(self) -> str:
        path = PurePosixPath(self.path.strip())
        if path.is_absolute():
            raise ValueError("skill file paths must be relative")
        if ".." in path.parts:
            raise ValueError("skill file paths must not escape the root directory")
        normalized = path.as_posix()
        if normalized in {"", "."}:
            raise ValueError("skill file paths must not be empty")
        return normalized

    @property
    def resolved_media_type(self) -> str:
        if self.media_type:
            return self.media_type
        guessed, _ = mimetypes.guess_type(self.normalized_path)
        if guessed:
            return guessed
        if self.normalized_path.endswith(".md"):
            return "text/markdown"
        return "text/plain"

    def to_canonical_dict(self) -> dict[str, str]:
        payload = {"path": self.normalized_path, "content": self.content}
        if self.media_type:
            payload["media_type"] = self.media_type
        return payload

    def to_api_file(self) -> tuple[str, bytes, str]:
        return (self.normalized_path, self.content.encode("utf-8"), self.resolved_media_type)


@dataclass(frozen=True)
class CustomSkillSpec:
    display_title: str | None
    files: tuple[SkillFile, ...]
    root_dir: str
    skill_name: str
    skill_description: str
    logical_key: str
    fingerprint: str

    def to_canonical_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "type": "custom",
            "files": [item.to_canonical_dict() for item in self.files],
        }
        if self.display_title is not None:
            payload["display_title"] = self.display_title
        return payload

    def to_api_files(self) -> list[tuple[str, bytes, str]]:
        return [item.to_api_file() for item in self.files]


SkillSpec: TypeAlias = SkillRef | CustomSkillSpec


@dataclass(frozen=True)
class SubagentSpec:
    name: str
    system_prompt: str
    description: str | None = None
    skills: tuple[SkillSpec, ...] = ()


@dataclass(frozen=True)
class EnvironmentSpec:
    config: dict[str, Any]


@dataclass(frozen=True)
class CandidateBundle:
    raw_fields: dict[str, str]
    fields: dict[str, str]
    candidate_id: str
    skills: tuple[SkillSpec, ...]
    environment: EnvironmentSpec
    subagents: tuple[SubagentSpec, ...]

    @classmethod
    def from_candidate(
        cls,
        candidate: dict[str, str] | str,
        *,
        compiler: CandidateCompiler | None = None,
    ) -> "CandidateBundle":
        active_compiler = compiler or StructuredCandidateCompiler()
        return active_compiler.compile(candidate)

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


class CandidateCompilationError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        raw_fields: dict[str, str],
        raw_candidate_id: str,
        field_errors: dict[str, str] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.raw_fields = raw_fields
        self.raw_candidate_id = raw_candidate_id
        self.field_errors = field_errors or {}
        self.details = details or {}


class CandidateCompiler(Protocol):
    def compile(self, candidate: dict[str, str] | str) -> CandidateBundle:
        ...


class _CompilerSkillFile(BaseModel):
    path: str
    content: str
    media_type: str | None = None


class _CompilerSkillSpec(BaseModel):
    type: str
    skill_id: str | None = None
    version: str | None = None
    display_title: str | None = None
    files: list[_CompilerSkillFile] = Field(default_factory=list)


class _CompilerEnvironmentNetworking(BaseModel):
    type: str
    allowed_hosts: list[str] = Field(default_factory=list)
    allow_mcp_servers: bool = False
    allow_package_managers: bool = False


class _CompilerEnvironmentPackages(BaseModel):
    type: str | None = "packages"
    apt: list[str] = Field(default_factory=list)
    cargo: list[str] = Field(default_factory=list)
    gem: list[str] = Field(default_factory=list)
    go: list[str] = Field(default_factory=list)
    npm: list[str] = Field(default_factory=list)
    pip: list[str] = Field(default_factory=list)


class _CompilerEnvironmentSpec(BaseModel):
    type: str
    networking: _CompilerEnvironmentNetworking
    packages: _CompilerEnvironmentPackages = Field(default_factory=_CompilerEnvironmentPackages)


class _CompilerSubagentSpec(BaseModel):
    name: str
    system_prompt: str
    description: str | None = None
    skills: list[_CompilerSkillSpec] = Field(default_factory=list)


class _CompilerCandidateError(BaseModel):
    field: str
    message: str


class _CompilerCandidateOutput(BaseModel):
    system_prompt: str
    task_prompt: str
    outcome_rubric: str
    skills: list[_CompilerSkillSpec] = Field(default_factory=list)
    environment_spec: _CompilerEnvironmentSpec | None = None
    subagent_specs: list[_CompilerSubagentSpec] = Field(default_factory=list)
    is_valid: bool = True
    errors: list[_CompilerCandidateError] = Field(default_factory=list)


class StructuredCandidateCompiler:
    def __init__(
        self,
        *,
        client: anthropic.Anthropic | None = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 4096,
    ) -> None:
        self.client = client or anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens

    def compile(self, candidate: dict[str, str] | str) -> CandidateBundle:
        raw_fields = normalize_candidate_fields(candidate)
        raw_candidate_id = sha256(_stable_candidate_json(raw_fields).encode("utf-8")).hexdigest()[:12]
        parsed = self._parse_candidate(raw_fields, raw_candidate_id)
        try:
            compiled_skills = tuple(_skill_spec_from_model(item, field_name="skills") for item in parsed.skills)
            compiled_environment = EnvironmentSpec(config=_environment_spec_from_model(parsed.environment_spec))
            compiled_subagents = tuple(_subagent_spec_from_model(item) for item in parsed.subagent_specs)
        except ValueError as exc:
            field_name, message = _split_field_error(str(exc))
            raise CandidateCompilationError(
                message,
                raw_fields=raw_fields,
                raw_candidate_id=raw_candidate_id,
                field_errors={field_name: message},
                details={
                    "stage": "structured_candidate_validation",
                    "parsed_output": parsed.model_dump(mode="json"),
                },
            ) from exc

        canonical_fields = {
            "system_prompt": raw_fields["system_prompt"],
            "task_prompt": raw_fields["task_prompt"],
            "outcome_rubric": raw_fields["outcome_rubric"],
            "skills": canonicalize_skills(compiled_skills),
            "environment_spec": canonicalize_environment_spec(compiled_environment.config),
            "subagent_specs": canonicalize_subagents(compiled_subagents),
        }
        candidate_id = sha256(_stable_candidate_json(canonical_fields).encode("utf-8")).hexdigest()[:12]

        return CandidateBundle(
            raw_fields=raw_fields,
            fields=canonical_fields,
            candidate_id=candidate_id,
            skills=compiled_skills,
            environment=compiled_environment,
            subagents=compiled_subagents,
        )

    def _parse_candidate(
        self,
        raw_fields: dict[str, str],
        raw_candidate_id: str,
    ) -> _CompilerCandidateOutput:
        response = self.client.messages.parse(
            model=self.model,
            max_tokens=self.max_tokens,
            system=COMPILER_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "candidate_fields": raw_fields,
                            "field_contract": {
                                "system_prompt": "Preserve this text exactly.",
                                "task_prompt": "Preserve this text exactly.",
                                "outcome_rubric": "Preserve this text exactly.",
                                "skills": (
                                    "Parse this YAML/JSON-like text into a list of skill specs. "
                                    "Use direct refs for Anthropic or existing custom skills, or inline custom "
                                    "skill definitions with files when the candidate defines new skill content."
                                ),
                                "environment_spec": (
                                    "Parse this YAML/JSON-like text into one cloud environment spec with "
                                    "networking and package-manager lists."
                                ),
                                "subagent_specs": (
                                    "Parse this YAML/JSON-like text into a list of subagent specs. "
                                    "Each subagent has name, system_prompt, optional description, and "
                                    "optional hybrid skills."
                                ),
                            },
                        },
                        ensure_ascii=True,
                        sort_keys=True,
                    ),
                }
            ],
            output_format=_CompilerCandidateOutput,
        )
        parsed_output = getattr(response, "parsed_output", None)
        if parsed_output is None:
            raise CandidateCompilationError(
                "Anthropic structured-output parsing did not return parsed_output",
                raw_fields=raw_fields,
                raw_candidate_id=raw_candidate_id,
                details={"stage": "structured_output_parse"},
            )

        field_errors = {item.field: item.message for item in parsed_output.errors}
        if not parsed_output.is_valid or parsed_output.environment_spec is None:
            raise CandidateCompilationError(
                "Anthropic structured-output parsing could not produce a valid candidate",
                raw_fields=raw_fields,
                raw_candidate_id=raw_candidate_id,
                field_errors=field_errors,
                details={
                    "stage": "structured_output_parse",
                    "parsed_output": parsed_output.model_dump(mode="json"),
                },
            )
        return parsed_output


def canonicalize_skills(skills: tuple[SkillSpec, ...]) -> str:
    return _dump_canonical_yaml([_canonical_skill_payload(skill) for skill in skills])


def canonicalize_environment_spec(config: dict[str, Any]) -> str:
    return _dump_canonical_yaml(_sort_nested_mapping(config))


def canonicalize_subagents(subagents: tuple[SubagentSpec, ...]) -> str:
    payload = []
    for subagent in subagents:
        item: dict[str, Any] = {
            "name": subagent.name,
            "system_prompt": subagent.system_prompt,
            "skills": [_canonical_skill_payload(skill) for skill in subagent.skills],
        }
        if subagent.description is not None:
            item["description"] = subagent.description
        payload.append(item)
    return _dump_canonical_yaml(payload)


def _canonical_skill_payload(skill: SkillSpec) -> dict[str, Any]:
    if isinstance(skill, SkillRef):
        return skill.to_api()
    return skill.to_canonical_dict()


def _environment_spec_from_model(model: _CompilerEnvironmentSpec | None) -> dict[str, Any]:
    if model is None:
        raise ValueError("environment_spec: missing environment spec")
    packages = model.packages
    config = {
        "type": model.type,
        "networking": {
            "type": model.networking.type,
        },
        "packages": {
            "type": packages.type or "packages",
            "apt": list(packages.apt),
            "cargo": list(packages.cargo),
            "gem": list(packages.gem),
            "go": list(packages.go),
            "npm": list(packages.npm),
            "pip": list(packages.pip),
        },
    }
    if model.networking.type == "limited":
        config["networking"]["allowed_hosts"] = list(model.networking.allowed_hosts)
        config["networking"]["allow_mcp_servers"] = bool(model.networking.allow_mcp_servers)
        config["networking"]["allow_package_managers"] = bool(model.networking.allow_package_managers)
    return _sort_nested_mapping(config)


def _sort_nested_mapping(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _sort_nested_mapping(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_sort_nested_mapping(item) for item in value]
    return value


def _dump_canonical_yaml(value: Any) -> str:
    return yaml.safe_dump(
        value,
        sort_keys=False,
        allow_unicode=False,
    )


def _skill_spec_from_model(model: _CompilerSkillSpec, *, field_name: str) -> SkillSpec:
    skill_type = model.type.strip().lower()
    if skill_type not in {"anthropic", "custom"}:
        raise ValueError(f"{field_name}: unsupported skill type {model.type!r}")

    if skill_type == "anthropic":
        if not model.skill_id:
            raise ValueError(f"{field_name}: anthropic skill entries require skill_id")
        if model.files:
            raise ValueError(f"{field_name}: anthropic skill entries must not include files")
        return SkillRef(type="anthropic", skill_id=model.skill_id, version=model.version)

    if model.skill_id:
        if model.files:
            raise ValueError(f"{field_name}: custom skill refs must not include files when skill_id is provided")
        return SkillRef(type="custom", skill_id=model.skill_id, version=model.version)

    if not model.files:
        raise ValueError(f"{field_name}: custom skill definitions require files when skill_id is absent")
    return _custom_skill_from_models(model.display_title, model.files, field_name=field_name)


def _subagent_spec_from_model(model: _CompilerSubagentSpec) -> SubagentSpec:
    return SubagentSpec(
        name=model.name,
        system_prompt=model.system_prompt,
        description=model.description,
        skills=tuple(_skill_spec_from_model(item, field_name="subagent_specs") for item in model.skills),
    )


def _custom_skill_from_models(
    display_title: str | None,
    files: list[_CompilerSkillFile],
    *,
    field_name: str,
) -> CustomSkillSpec:
    normalized_files = tuple(
        sorted(
            (SkillFile(path=item.path, content=item.content, media_type=item.media_type) for item in files),
            key=lambda item: item.normalized_path,
        )
    )
    if not normalized_files:
        raise ValueError(f"{field_name}: custom skill definitions must include at least one file")

    top_level_dirs = {_top_level_dir(item.normalized_path) for item in normalized_files}
    if len(top_level_dirs) != 1:
        raise ValueError(f"{field_name}: custom skill files must share one top-level directory")
    root_dir = next(iter(top_level_dirs))
    skill_md_path = f"{root_dir}/SKILL.md"
    file_by_path = {item.normalized_path: item for item in normalized_files}
    if skill_md_path not in file_by_path:
        raise ValueError(f"{field_name}: custom skill definitions must include {skill_md_path}")

    skill_name, skill_description = _parse_skill_frontmatter(file_by_path[skill_md_path].content, field_name=field_name)
    fingerprint = sha256(
        _stable_candidate_json(
            {"files": [item.to_canonical_dict() for item in normalized_files], "display_title": display_title}
        ).encode("utf-8")
    ).hexdigest()
    return CustomSkillSpec(
        display_title=display_title,
        files=normalized_files,
        root_dir=root_dir,
        skill_name=skill_name,
        skill_description=skill_description,
        logical_key=f"{root_dir}:{skill_name}",
        fingerprint=fingerprint,
    )


def _top_level_dir(path: str) -> str:
    parts = PurePosixPath(path).parts
    if not parts:
        raise ValueError("skill file path must not be empty")
    return parts[0]


def _parse_skill_frontmatter(content: str, *, field_name: str) -> tuple[str, str]:
    if not content.startswith("---"):
        raise ValueError(f"{field_name}: SKILL.md must start with YAML frontmatter")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{field_name}: SKILL.md frontmatter must be closed with ---")
    frontmatter = yaml.safe_load(parts[1]) or {}
    name = str(frontmatter.get("name", "")).strip()
    description = str(frontmatter.get("description", "")).strip()
    if not name or not SKILL_NAME_RE.fullmatch(name) or name in {"anthropic", "claude"}:
        raise ValueError(
            f"{field_name}: SKILL.md frontmatter name must be lowercase letters, numbers, or hyphens only"
        )
    if not description:
        raise ValueError(f"{field_name}: SKILL.md frontmatter must include a non-empty description")
    return name, description


def _split_field_error(message: str) -> tuple[str, str]:
    if ": " not in message:
        return "skills", message
    field_name, details = message.split(": ", 1)
    return field_name, details
