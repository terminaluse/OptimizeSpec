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
        "You are a careful autonomous file-processing agent. "
        "Always read the mounted input file, produce the exact requested result, and write only that final answer "
        "to the required output path. Use available skills when they are relevant, and if callable agents are "
        "available, delegate narrowly scoped review or verification work before you finish."
    ),
    "task_prompt": (
        "Task summary: {task_summary}\n\n"
        "Input file: {input_path}\n"
        "Required output file: {output_path}\n\n"
        "Execution checklist:\n"
        "1. Read the input file.\n"
        "2. Solve the transformation exactly.\n"
        "3. Write only the final answer to the required output file.\n"
        "4. Use relevant attached skills or environment capabilities when they materially help.\n"
        "5. If callable agents are available, ask one to verify your final output before stopping.\n"
        "6. Ensure there is no extra newline unless the task explicitly requires one.\n"
    ),
    "outcome_rubric": (
        "# Exact Output Rubric\n\n"
        "## File creation\n"
        "- The agent writes the final answer to `{output_path}`.\n"
        "- The file exists at task completion.\n\n"
        "## Exactness\n"
        "- The file content directly answers the task.\n"
        "- The file contains no explanation, markdown, or extra framing.\n"
        "- The file contains no extra trailing newline unless the task requires one.\n\n"
        "## Agent process\n"
        "- The agent uses relevant skills, environment capabilities, or callable agents when they improve correctness.\n"
        "- The agent verifies the final file before stopping.\n"
    ),
    "skills": (
        "- type: custom\n"
        "  display_title: Exact Output Checklist\n"
        "  files:\n"
        "    - path: exact-output-checklist/SKILL.md\n"
        "      content: |\n"
        "        ---\n"
        "        name: exact-output-checklist\n"
        "        description: Verification checklist for deterministic file-output tasks.\n"
        "        ---\n"
        "        Use this skill when a task requires reading a mounted file and writing an exact output file.\n"
        "        Always:\n"
        "        1. Read the full input file before planning.\n"
        "        2. Write only the final answer to the requested output path.\n"
        "        3. Re-open or otherwise verify the output file before stopping.\n"
        "        4. Prefer short deterministic scripts over manual editing for structured transforms.\n"
    ),
    "environment_spec": (
        "type: cloud\n"
        "networking:\n"
        "  type: limited\n"
        "  allowed_hosts: []\n"
        "  allow_mcp_servers: false\n"
        "  allow_package_managers: true\n"
        "packages:\n"
        "  type: packages\n"
        "  apt: []\n"
        "  cargo: []\n"
        "  gem: []\n"
        "  go: []\n"
        "  npm: []\n"
        "  pip:\n"
        "    - python-slugify==8.0.4\n"
    ),
    "subagent_specs": "[]\n",
}

DEFAULT_OBJECTIVE = (
    "Optimize a Claude Managed Agents configuration so it reliably completes file-based transformation "
    "tasks by reading mounted input files and writing exact output files. Improve not only prompts but also "
    "the skill surface, environment configuration, and callable subagent setup when those changes increase "
    "correctness or robustness."
)

DEFAULT_BACKGROUND = (
    "The candidate is a dict[str, str] with these fields: system_prompt, task_prompt, outcome_rubric, "
    "skills, environment_spec, subagent_specs. The evaluator compiles the candidate into fresh Anthropic "
    "Managed Agents resources for each task. The skills field is hybrid: each item is either a reusable skill "
    "ref {type, skill_id, version?} or a custom skill definition {type: custom, display_title?, files:[{path, content, media_type?}]}. "
    "Custom skills must keep all files under one top-level directory and include SKILL.md at that directory root. "
    "The environment_spec field is a cloud environment config with networking and package-manager lists. "
    "The subagent_specs field is a list of callable subagent definitions with name, system_prompt, optional "
    "description, and optional nested hybrid skills. Prefer exact output-file correctness, valid structured "
    "configuration, and changes that materially help benchmark tasks."
)

DEFAULT_REFLECTION_TEMPLATES: dict[str, str] = {
    "system_prompt": (
        "You are mutating only the `system_prompt` field for a Claude Managed Agent.\n"
        "Current value:\n```\n<curr_param>\n```\n\n"
        "Evaluation data:\n```\n<side_info>\n```\n\n"
        "Propose a drop-in replacement system prompt that improves exact file-output behavior, deliberate tool use, "
        "and when helpful the use of available skills or callable agents. Return only the new prompt inside ``` blocks."
    ),
    "task_prompt": (
        "You are mutating only the `task_prompt` field for a Claude Managed Agent.\n"
        "Current value:\n```\n<curr_param>\n```\n\n"
        "Evaluation data:\n```\n<side_info>\n```\n\n"
        "Make the task instructions clearer about reading the input file, writing the exact output path, and using "
        "skills, environment capabilities, or callable agents only when they materially help. Return only the new "
        "task prompt inside ``` blocks."
    ),
    "outcome_rubric": (
        "You are mutating only the `outcome_rubric` field.\n"
        "Current value:\n```\n<curr_param>\n```\n\n"
        "Evaluation data:\n```\n<side_info>\n```\n\n"
        "Strengthen the rubric so it rewards exact file creation, exact file content, and useful use of skills, "
        "environment features, or callable agents without adding unrelated goals. Return only the new rubric inside ``` blocks."
    ),
    "skills": (
        "You are mutating only the `skills` field of a GEPA candidate.\n"
        "Current value:\n```\n<curr_param>\n```\n\n"
        "Evaluation data:\n```\n<side_info>\n```\n\n"
        "Return only valid YAML for the `skills` field inside ``` blocks.\n"
        "Each list item must be one of:\n"
        "1. A reusable ref: {type: anthropic|custom, skill_id: ..., version?: ...}\n"
        "2. A custom skill definition: {type: custom, display_title?: ..., files:[{path: ..., content: ..., media_type?: ...}]}\n"
        "For custom skill definitions, all file paths must share one top-level directory and include SKILL.md at the "
        "root of that directory. SKILL.md must have YAML frontmatter with valid `name` and `description` fields. "
        "Make only changes that materially help benchmark performance."
    ),
    "environment_spec": (
        "You are mutating only the `environment_spec` field.\n"
        "Current value:\n```\n<curr_param>\n```\n\n"
        "Evaluation data:\n```\n<side_info>\n```\n\n"
        "Return only valid YAML for a Claude Managed Agents cloud environment config inside ``` blocks.\n"
        "Use the shape:\n"
        "type: cloud\n"
        "networking:\n"
        "  type: limited|unrestricted\n"
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
        "Only add network access or packages when they materially help benchmark tasks."
    ),
    "subagent_specs": (
        "You are mutating only the `subagent_specs` field.\n"
        "Current value:\n```\n<curr_param>\n```\n\n"
        "Evaluation data:\n```\n<side_info>\n```\n\n"
        "Return only valid YAML for a list of callable subagents inside ``` blocks.\n"
        "Each item must have `name` and `system_prompt`, may include `description`, and may include nested `skills` "
        "using the same hybrid skills schema as the top-level `skills` field. Use subagents only for tightly scoped "
        "specialist work such as verification, decomposition, or structured review."
    ),
}


def optimize_demo(
    *,
    max_metric_calls: int = 48,
    reflection_model: str = "anthropic/claude-opus-4-7",
    run_dir: str = "runs/gepa-demo",
    seed_candidate: dict[str, str] | None = None,
    max_runtime_seconds: float = 120.0,
):
    evaluator = ManagedAgentEvaluator(run_dir=Path(run_dir), max_runtime_seconds=max_runtime_seconds)
    config = GEPAConfig(
        engine=EngineConfig(max_metric_calls=max_metric_calls, run_dir=run_dir, capture_stdio=True),
        reflection=ReflectionConfig(
            reflection_lm=reflection_model,
            module_selector="round_robin",
            reflection_prompt_template=DEFAULT_REFLECTION_TEMPLATES,
        ),
    )
    return oa.optimize_anything(
        seed_candidate=dict(seed_candidate or DEMO_SEED_CANDIDATE),
        evaluator=evaluator,
        dataset=TRAIN_TASKS,
        valset=VAL_TASKS,
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
                "focus_fields": list(task.focus_fields),
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
