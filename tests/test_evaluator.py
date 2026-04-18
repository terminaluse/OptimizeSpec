from claude_gepa.evaluator import compute_text_match_score


def test_exact_match_score() -> None:
    assert compute_text_match_score("hello", "hello") == 1.0
    assert compute_text_match_score("hello", " hello\n") == 1.0
    assert compute_text_match_score("hello", "world") == 0.0
    assert compute_text_match_score("hello", None) == 0.0
