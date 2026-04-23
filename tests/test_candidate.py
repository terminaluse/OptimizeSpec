from types import SimpleNamespace

import pytest

from agent_gepa.candidate import (
    CandidateBundle,
    CandidateCompilationError,
    CustomSkillSpec,
    DEFAULT_SEED_CANDIDATE,
    StructuredCandidateCompiler,
    _CompilerCandidateError,
    _CompilerCandidateOutput,
    _CompilerEnvironmentNetworking,
    _CompilerEnvironmentPackages,
    _CompilerEnvironmentSpec,
    _CompilerSkillFile,
    _CompilerSkillSpec,
    _CompilerSubagentSpec,
)


class _FakeMessages:
    def __init__(self, parsed_output: _CompilerCandidateOutput | None) -> None:
        self.parsed_output = parsed_output
        self.calls: list[dict[str, object]] = []

    def parse(self, **kwargs: object) -> SimpleNamespace:
        self.calls.append(kwargs)
        return SimpleNamespace(parsed_output=self.parsed_output)


class _FakeClient:
    def __init__(self, parsed_output: _CompilerCandidateOutput | None) -> None:
        self.messages = _FakeMessages(parsed_output)


def _make_valid_output() -> _CompilerCandidateOutput:
    return _CompilerCandidateOutput(
        system_prompt=DEFAULT_SEED_CANDIDATE["system_prompt"],
        task_prompt=DEFAULT_SEED_CANDIDATE["task_prompt"],
        outcome_rubric=DEFAULT_SEED_CANDIDATE["outcome_rubric"],
        skills=[],
        environment_spec=_CompilerEnvironmentSpec(
            type="cloud",
            networking=_CompilerEnvironmentNetworking(
                type="limited",
                allowed_hosts=[],
                allow_mcp_servers=False,
                allow_package_managers=False,
            ),
            packages=_CompilerEnvironmentPackages(
                type="packages",
                apt=[],
                cargo=[],
                gem=[],
                go=[],
                npm=[],
                pip=[],
            ),
        ),
        subagent_specs=[],
        is_valid=True,
        errors=[],
    )


def test_candidate_bundle_uses_default_fields() -> None:
    compiler = StructuredCandidateCompiler(client=_FakeClient(_make_valid_output()))
    bundle = CandidateBundle.from_candidate({"system_prompt": "test"}, compiler=compiler)
    assert bundle.system_prompt == "test"
    assert "environment_spec" in bundle.fields
    assert bundle.skills == ()
    assert bundle.subagents == ()


def test_candidate_identity_is_stable() -> None:
    first = CandidateBundle.from_candidate(
        dict(DEFAULT_SEED_CANDIDATE),
        compiler=StructuredCandidateCompiler(client=_FakeClient(_make_valid_output())),
    )
    second = CandidateBundle.from_candidate(
        dict(DEFAULT_SEED_CANDIDATE),
        compiler=StructuredCandidateCompiler(client=_FakeClient(_make_valid_output())),
    )
    assert first.candidate_id == second.candidate_id


def test_candidate_identity_uses_canonical_structured_fields() -> None:
    parsed_output = _make_valid_output().model_copy(
        update={
            "skills": [
                _CompilerSkillSpec(
                    type="custom",
                    display_title="Exact Output Checklist",
                    files=[
                        _CompilerSkillFile(
                            path="exact-output-checklist/SKILL.md",
                            content=(
                                "---\n"
                                "name: exact-output-checklist\n"
                                "description: Verification checklist for deterministic file-output tasks.\n"
                                "---\n"
                                "Use this skill to verify exact file outputs.\n"
                            ),
                        )
                    ],
                )
            ]
        }
    )
    first = CandidateBundle.from_candidate(
        dict(DEFAULT_SEED_CANDIDATE),
        compiler=StructuredCandidateCompiler(client=_FakeClient(parsed_output)),
    )
    second_candidate = dict(DEFAULT_SEED_CANDIDATE)
    second_candidate["skills"] = (
        "- type: custom\n"
        "  display_title: Exact Output Checklist\n"
        "  files:\n"
        "    - path: exact-output-checklist/SKILL.md\n"
        "      content: |\n"
        "        ---\n"
        "        name: exact-output-checklist\n"
        "        description: Verification checklist for deterministic file-output tasks.\n"
        "        ---\n"
        "        Use this skill to verify exact file outputs.\n"
    )
    second = CandidateBundle.from_candidate(
        second_candidate,
        compiler=StructuredCandidateCompiler(client=_FakeClient(parsed_output)),
    )
    assert first.candidate_id == second.candidate_id
    assert isinstance(first.skills[0], CustomSkillSpec)
    assert first.skills[0].root_dir == "exact-output-checklist"


def test_candidate_compiler_raises_when_structured_output_is_invalid() -> None:
    invalid_output = _make_valid_output().model_copy(
        update={
            "is_valid": False,
            "errors": [_CompilerCandidateError(field="skills", message="skills field is not parseable")],
            "environment_spec": None,
        }
    )
    compiler = StructuredCandidateCompiler(client=_FakeClient(invalid_output))

    with pytest.raises(CandidateCompilationError) as excinfo:
        compiler.compile(dict(DEFAULT_SEED_CANDIDATE))

    assert excinfo.value.field_errors == {"skills": "skills field is not parseable"}


def test_candidate_compiler_rejects_custom_skill_without_skill_md() -> None:
    parsed_output = _make_valid_output().model_copy(
        update={
            "skills": [
                _CompilerSkillSpec(
                    type="custom",
                    files=[_CompilerSkillFile(path="bad-skill/helper.py", content="print('hi')\n")],
                )
            ]
        }
    )
    compiler = StructuredCandidateCompiler(client=_FakeClient(parsed_output))

    with pytest.raises(CandidateCompilationError) as excinfo:
        compiler.compile(dict(DEFAULT_SEED_CANDIDATE))

    assert excinfo.value.field_errors == {
        "skills": "custom skill definitions must include bad-skill/SKILL.md"
    }


def test_candidate_compiler_parses_nested_subagent_skills() -> None:
    parsed_output = _make_valid_output().model_copy(
        update={
            "subagent_specs": [
                _CompilerSubagentSpec(
                    name="verifier",
                    system_prompt="Verify the final output file exactly.",
                    skills=[
                        _CompilerSkillSpec(type="anthropic", skill_id="pdf"),
                    ],
                )
            ]
        }
    )
    compiler = StructuredCandidateCompiler(client=_FakeClient(parsed_output))
    bundle = compiler.compile(dict(DEFAULT_SEED_CANDIDATE))

    assert bundle.subagents[0].name == "verifier"
    assert bundle.subagents[0].skills[0].skill_id == "pdf"
