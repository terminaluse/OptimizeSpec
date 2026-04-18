from __future__ import annotations

from difflib import unified_diff
from pathlib import Path
from statistics import mean

import gepa.optimize_anything as oa
from gepa.optimize_anything import EngineConfig, GEPAConfig, ReflectionConfig

from .candidate import DEFAULT_SEED_CANDIDATE
from .evaluator import ManagedAgentEvaluator
from .tasks import TRAIN_TASKS, VAL_TASKS


DEMO_SEED_CANDIDATE: dict[str, str] = {
    "system_prompt": (
        "You are a helpful AI agent. When you write the final answer to a file, always end the file "
        "with a trailing newline so the result looks neatly formatted."
    ),
    "task_prompt": (
        "Task: {task_summary}\n"
        "Input file: {input_path}\n"
        "Output file: {output_path}\n"
        "Use the available tools to solve the task and put the answer in the output file.\n"
    ),
    "outcome_rubric": (
        "# Rubric\n"
        "- Create the required output file at `{output_path}`.\n"
        "- The output file should contain the task answer.\n"
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

DEFAULT_OBJECTIVE = (
    "Optimize a Claude Managed Agents configuration so it reliably completes file-based transformation "
    "tasks by reading a mounted input file and writing the exact required output file."
)

DEFAULT_BACKGROUND = (
    "The candidate is a dict[str, str] with these fields: system_prompt, task_prompt, outcome_rubric, "
    "skills, environment_spec, subagent_specs. The evaluator compiles the candidate into fresh Anthropic "
    "Managed Agents resources for each task. The benchmark rewards exact output-file correctness across "
    "multiple string and structured-text transformations. Prefer explicit file-writing instructions over "
    "generic assistant behavior."
)


def optimize_demo(
    *,
    max_metric_calls: int = 24,
    reflection_model: str = "anthropic/claude-opus-4-7",
    run_dir: str = "runs/gepa-demo",
    seed_candidate: dict[str, str] | None = None,
    max_runtime_seconds: float = 120.0,
):
    evaluator = ManagedAgentEvaluator(run_dir=Path(run_dir), max_runtime_seconds=max_runtime_seconds)
    config = GEPAConfig(
        engine=EngineConfig(max_metric_calls=max_metric_calls, run_dir=run_dir, capture_stdio=True),
        reflection=ReflectionConfig(reflection_lm=reflection_model, module_selector="all"),
    )
    return oa.optimize_anything(
        seed_candidate=dict(seed_candidate or DEMO_SEED_CANDIDATE),
        evaluator=evaluator,
        dataset=TRAIN_TASKS,
        valset=VAL_TASKS,
        objective=DEFAULT_OBJECTIVE,
        background=DEFAULT_BACKGROUND,
        config=config,
    )


def evaluate_candidate_suite(
    candidate: dict[str, str],
    *,
    run_dir: str,
    use_outcomes: bool = True,
    max_runtime_seconds: float = 45.0,
) -> dict[str, object]:
    evaluator = ManagedAgentEvaluator(
        run_dir=Path(run_dir),
        use_outcomes=use_outcomes,
        max_runtime_seconds=max_runtime_seconds,
    )
    suite = [("train", task) for task in TRAIN_TASKS] + [("val", task) for task in VAL_TASKS]
    results: list[dict[str, object]] = []

    for split, task in suite:
        score, side_info = evaluator(dict(candidate), example=task)
        results.append(
            {
                "split": split,
                "task_id": task.task_id,
                "score": score,
                "expected_output": task.expected_output,
                "actual_output": side_info.get("actual_output"),
                "outcome_result": side_info.get("outcome_result"),
                "errors": side_info.get("errors", []),
            }
        )

    train_scores = [float(item["score"]) for item in results if item["split"] == "train"]
    val_scores = [float(item["score"]) for item in results if item["split"] == "val"]
    all_scores = train_scores + val_scores
    return {
        "mean_train_score": mean(train_scores) if train_scores else 0.0,
        "mean_val_score": mean(val_scores) if val_scores else 0.0,
        "mean_score": mean(all_scores) if all_scores else 0.0,
        "tasks": results,
    }


def diff_candidates(before: dict[str, str], after: dict[str, str]) -> dict[str, str]:
    diffs: dict[str, str] = {}
    for key in sorted(set(before) | set(after)):
        if before.get(key) == after.get(key):
            continue
        diffs[key] = "\n".join(
            unified_diff(
                before.get(key, "").splitlines(),
                after.get(key, "").splitlines(),
                fromfile=f"before/{key}",
                tofile=f"after/{key}",
                lineterm="",
            )
        )
    return diffs
