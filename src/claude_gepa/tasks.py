from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DummyTask:
    task_id: str
    task_summary: str
    input_text: str
    expected_output: str
    input_path: str = "/workspace/task_input.txt"
    output_path: str = "/mnt/session/outputs/result.txt"


TRAIN_TASKS: list[DummyTask] = [
    DummyTask(
        task_id="uppercase-greek",
        task_summary="Convert the entire input file to uppercase and write the exact result.",
        input_text="alpha beta gamma",
        expected_output="ALPHA BETA GAMMA",
    ),
    DummyTask(
        task_id="reverse-lines",
        task_summary=(
            "Reverse the order of the lines in the input file and write the resulting lines "
            "joined by newline characters."
        ),
        input_text="red\nblue\ngreen",
        expected_output="green\nblue\nred",
    ),
    DummyTask(
        task_id="longest-token",
        task_summary=(
            "Read all whitespace-delimited tokens in the input file and write only the longest token. "
            "If multiple tokens tie for longest, write the first such token."
        ),
        input_text="ant bee hippopotamus cat",
        expected_output="hippopotamus",
    ),
    DummyTask(
        task_id="sorted-json-from-pairs",
        task_summary=(
            "Each line in the input file is `key=value`. Parse the lines and write a compact single-line "
            "JSON object with keys sorted alphabetically and values preserved as strings."
        ),
        input_text="zeta=3\nalpha=1\nbeta=2",
        expected_output='{"alpha":"1","beta":"2","zeta":"3"}',
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
    ),
    DummyTask(
        task_id="line-lengths",
        task_summary=(
            "For each line in the input file, count its character length. Write the counts as a single line "
            "joined by commas in the original line order."
        ),
        input_text="aa\nbbbb\nc",
        expected_output="2,4,1",
    ),
    DummyTask(
        task_id="reverse-words-per-line",
        task_summary=(
            "Reverse the order of words within each line while preserving line breaks. Words are separated "
            "by single spaces."
        ),
        input_text="red blue\ngreen gold",
        expected_output="blue red\ngold green",
    ),
]
