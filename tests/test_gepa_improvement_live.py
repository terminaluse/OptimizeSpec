from __future__ import annotations

import os
from pathlib import Path

import pytest

from optimizespec.self_improvement import (
    EvalCase,
    ScorerSpec,
    TemplateEchoExecutor,
    compare_candidates,
    evaluate_candidate,
    optimize_candidate,
)


def _load_env_key() -> None:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped.removeprefix("export ").strip()
        key, separator, value = stripped.partition("=")
        if key == "ANTHROPIC_API_KEY" and separator:
            os.environ[key] = value.strip().strip("'\"")
            return


@pytest.mark.skipif(
    os.environ.get("OPTIMIZESPEC_RUN_LIVE_IMPROVEMENT") != "1",
    reason="set OPTIMIZESPEC_RUN_LIVE_IMPROVEMENT=1 to run the live GEPA improvement sanity check",
)
def test_live_gepa_improves_weak_candidate(tmp_path: Path) -> None:
    _load_env_key()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY is required for the live GEPA improvement sanity check")

    cases = [
        EvalCase(
            case_id="echo-train",
            split="train",
            input="alpha",
            expected="alpha",
            scorer=ScorerSpec(type="exact_match", expected="alpha"),
        ),
        EvalCase(
            case_id="echo-val",
            split="val",
            input="beta",
            expected="beta",
            scorer=ScorerSpec(type="exact_match", expected="beta"),
        ),
    ]
    seed = {"answer_template": "wrong"}
    executor = TemplateEchoExecutor()
    mutable_fields = ["answer_template"]

    baseline = evaluate_candidate(
        candidate=seed,
        cases=cases,
        executor=executor,
        run_dir=tmp_path / "baseline",
        mutable_fields=mutable_fields,
    )
    assert baseline["mean_score"] == 0.0

    result = optimize_candidate(
        seed_candidate=seed,
        cases=cases,
        executor=executor,
        run_dir=tmp_path / "optimize",
        objective="Improve answer_template so the executor echoes each eval input exactly.",
        background=(
            "The candidate has one mutable field, answer_template. The executor computes "
            'actual = candidate["answer_template"].format(input=case.input). A perfect candidate '
            "should use the {input} placeholder and no extra text."
        ),
        reflection_model="anthropic/claude-opus-4-7",
        max_metric_calls=8,
        timeout_seconds=5.0,
        mutable_fields=mutable_fields,
        module_selector="round_robin",
    )
    best_candidate = dict(result.best_candidate)

    comparison = compare_candidates(
        baseline=seed,
        candidate=best_candidate,
        cases=cases,
        executor=executor,
        run_dir=tmp_path / "compare",
    )

    assert best_candidate != seed
    assert comparison["candidate_diff"]
    assert comparison["candidate"]["mean_score"] > comparison["baseline"]["mean_score"]
    assert comparison["candidate"]["mean_train_score"] == 1.0
    assert comparison["candidate"]["mean_val_score"] == 1.0
    assert all(item["delta"] > 0.0 for item in comparison["deltas"])
    assert (tmp_path / "optimize" / "candidates.json").exists()
