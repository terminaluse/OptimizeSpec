from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DummyTask:
    task_id: str
    task_summary: str
    input_text: str
    expected_output: str
    focus_fields: tuple[str, ...] = ()
    input_path: str = "/workspace/task_input.txt"
    output_path: str = "/mnt/session/outputs/result.txt"


TRAIN_TASKS: list[DummyTask] = [
    DummyTask(
        task_id="uppercase-greek",
        task_summary="Convert the entire input file to uppercase and write the exact result.",
        input_text="alpha beta gamma",
        expected_output="ALPHA BETA GAMMA",
        focus_fields=("system_prompt", "task_prompt"),
    ),
    DummyTask(
        task_id="reverse-lines",
        task_summary=(
            "Reverse the order of the lines in the input file and write the resulting lines "
            "joined by newline characters."
        ),
        input_text="red\nblue\ngreen",
        expected_output="green\nblue\nred",
        focus_fields=("system_prompt", "task_prompt"),
    ),
    DummyTask(
        task_id="longest-token",
        task_summary=(
            "Read all whitespace-delimited tokens in the input file and write only the longest token. "
            "If multiple tokens tie for longest, write the first such token."
        ),
        input_text="ant bee hippopotamus cat",
        expected_output="hippopotamus",
        focus_fields=("system_prompt", "task_prompt", "subagent_specs"),
    ),
    DummyTask(
        task_id="sorted-json-from-pairs",
        task_summary=(
            "Each line in the input file is `key=value`. Parse the lines and write a compact single-line "
            "JSON object with keys sorted alphabetically and values preserved as strings."
        ),
        input_text="zeta=3\nalpha=1\nbeta=2",
        expected_output='{"alpha":"1","beta":"2","zeta":"3"}',
        focus_fields=("system_prompt", "task_prompt"),
    ),
    DummyTask(
        task_id="unicode-slugs",
        task_summary=(
            "Each line in the input file is a phrase. Convert every line to a lowercase ASCII slug with "
            "words separated by single hyphens, then write the slugs joined by newline characters. "
            "Use any relevant packages, specialist skills, or callable agents if available."
        ),
        input_text="Crème brûlée\npiñata party",
        expected_output="creme-brulee\npinata-party",
        focus_fields=("environment_spec", "skills", "subagent_specs"),
    ),
    DummyTask(
        task_id="csv-sum-by-key",
        task_summary=(
            "The input file is CSV with columns `team,points`. Sum points by team and write a compact "
            "single-line JSON object with keys sorted alphabetically and integer values."
        ),
        input_text="red,3\nblue,7\nred,4",
        expected_output='{"blue":7,"red":7}',
        focus_fields=("system_prompt", "task_prompt", "subagent_specs"),
    ),
]


VAL_TASKS: list[DummyTask] = [
    DummyTask(
        task_id="comma-to-pipes",
        task_summary=(
            "Replace every comma in the input file with a pipe character and preserve all "
            "other characters exactly."
        ),
        input_text="a,b,c,d",
        expected_output="a|b|c|d",
        focus_fields=("system_prompt", "task_prompt"),
    ),
    DummyTask(
        task_id="line-lengths",
        task_summary=(
            "For each line in the input file, count its character length. Write the counts as a single line "
            "joined by commas in the original line order."
        ),
        input_text="aa\nbbbb\nc",
        expected_output="2,4,1",
        focus_fields=("system_prompt", "task_prompt"),
    ),
    DummyTask(
        task_id="reverse-words-per-line",
        task_summary=(
            "Reverse the order of words within each line while preserving line breaks. Words are separated "
            "by single spaces."
        ),
        input_text="red blue\ngreen gold",
        expected_output="blue red\ngold green",
        focus_fields=("system_prompt", "task_prompt", "subagent_specs"),
    ),
    DummyTask(
        task_id="yaml-key-order",
        task_summary=(
            "The input file is YAML containing a mapping of string keys to scalar values. Write a compact "
            "single-line JSON object with keys sorted alphabetically and the original scalar values preserved."
        ),
        input_text="zeta: 3\nalpha: one\nbeta: true\n",
        expected_output='{"alpha":"one","beta":true,"zeta":3}',
        focus_fields=("environment_spec", "skills"),
    ),
    DummyTask(
        task_id="dedup-sorted-words",
        task_summary=(
            "Read all whitespace-delimited words, drop duplicates, sort the remaining words alphabetically, "
            "and write them joined by commas."
        ),
        input_text="pear apple pear banana apple",
        expected_output="apple,banana,pear",
        focus_fields=("system_prompt", "task_prompt", "subagent_specs"),
    ),
]
