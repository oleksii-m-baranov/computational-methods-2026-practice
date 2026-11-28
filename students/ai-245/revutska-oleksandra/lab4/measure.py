
import json
import sys
import time
from pathlib import Path

from langfuse import get_client, propagate_attributes

import config
from agent import run_agent
from table import make_row, print_table

CONFIGS = {
    "none": {"COMPRESS": "none", "USE_STATE": False},
    "trim": {"COMPRESS": "trim", "USE_STATE": False},
    "trim+state": {"COMPRESS": "trim", "USE_STATE": True},
}


def read_arguments():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    series = sys.argv[3] if len(sys.argv) > 3 else "main"

    names = list(CONFIGS) if which == "all" else [which]
    return names, repeats, series


def load_task():
    with open("long_task.json", encoding="utf-8") as f:
        return json.load(f)


def is_correct(answer, expected):
    if not answer:
        return False

    if isinstance(expected, dict):
        expected = expected["total_fine"]

    text = str(answer).replace(" ", "").replace(",", ".")
    number = str(expected).replace(",", ".")
    return number in text


def run_once(name, repeat, series, task):
    for key, value in CONFIGS[name].items():
        setattr(config, key, value)

    config.USE_CACHE = series.startswith("cache")

    run_id = f"{series}_{name}_r{repeat}"
    question = task.get("question") or task["task"]

    started = time.perf_counter()

    with propagate_attributes(
        trace_name=f"long-{run_id}",
        tags=[series, name],
    ):
        answer = run_agent(
            task=question,
            max_steps=config.MAX_STEPS_LONG,
            logfile_name=run_id,
            task_id=run_id,
            log_overwrite=True,
        )

    seconds = round(time.perf_counter() - started, 1)
    return run_id, answer, seconds


def main():
    names, repeats, series = read_arguments()
    task = load_task()

    Path("logs").mkdir(exist_ok=True)
    rows = []

    for repeat in range(1, repeats + 1):
        for name in names:
            run_id, answer, seconds = run_once(
                name, repeat, series, task
            )

            right = is_correct(answer, task["expected"])

            print(
                f"\n[{run_id}] час {seconds} с | "
                f"правильно: {'так' if right else 'ні'}"
            )
            print(f"[{run_id}] відповідь: {answer}")

            with open(
                f"logs/{run_id}.log",
                "a",
                encoding="utf-8",
            ) as f:
                f.write(f"\nЧАС, с: {seconds}\n")
                f.write(f"ПРАВИЛЬНО: {'так' if right else 'ні'}\n")

            rows.append(
                make_row(run_id, name, right, seconds)
            )

    get_client().flush()
    print_table(rows)


if __name__ == "__main__":
    main()
