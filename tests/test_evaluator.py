from agent_gepa.candidate import CandidateCompilationError
from agent_gepa.evaluator import ManagedAgentEvaluator, compute_text_match_score
from agent_gepa.tasks import VAL_TASKS


def test_exact_match_score() -> None:
    assert compute_text_match_score("hello", "hello") == 1.0
    assert compute_text_match_score("hello", " hello\n") == 0.0
    assert compute_text_match_score("hello", "world") == 0.0
    assert compute_text_match_score("hello", None) == 0.0


class _FailingCompiler:
    def compile(self, candidate: dict[str, str] | str):
        raise CandidateCompilationError(
            "candidate parse failed",
            raw_fields={"system_prompt": "bad"},
            raw_candidate_id="badc0ffee123",
            field_errors={"skills": "skills field is not parseable"},
            details={"stage": "structured_output_parse"},
        )


def test_evaluator_returns_scored_failure_for_candidate_compilation_errors(tmp_path) -> None:
    evaluator = ManagedAgentEvaluator(run_dir=tmp_path, compiler=_FailingCompiler())

    score, side_info = evaluator({"system_prompt": "bad"}, example=VAL_TASKS[0])

    assert score == 0.0
    assert side_info["candidate_id"] == "badc0ffee123"
    assert side_info["compile_stage"] == "structured_output_parse"
    assert side_info["field_errors"] == {"skills": "skills field is not parseable"}
