from claude_gepa.candidate import CandidateBundle, DEFAULT_SEED_CANDIDATE


def test_candidate_bundle_uses_default_fields() -> None:
    bundle = CandidateBundle.from_candidate({"system_prompt": "test"})
    assert bundle.system_prompt == "test"
    assert "environment_spec" in bundle.fields
    assert bundle.skills == ()
    assert bundle.subagents == ()


def test_candidate_identity_is_stable() -> None:
    first = CandidateBundle.from_candidate(dict(DEFAULT_SEED_CANDIDATE))
    second = CandidateBundle.from_candidate(dict(DEFAULT_SEED_CANDIDATE))
    assert first.candidate_id == second.candidate_id
