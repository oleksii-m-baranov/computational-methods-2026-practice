
"""Запуск довгої задачі та вимірювання результатів."""

import json
import os
import sys
import time

from langfuse import get_client, propagate_attributes

import agent
import config
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

    text = answer.replace(" ", "").replace(",", ".")
    return str(expected) in text


def run_once(name, repeat, series, task):
    for key, value in CONFIGS[name].items():
        setattr(config, key, value)

    run_id = f"{series}_{name}_r{repeat}"

    started = time.time()

    with propagate_attributes(
        trace_name=f"long-{run_id}",
        tags=[series, name]
    ):
        answer = agent.run_agent(
            task=task["question"],
            max_steps=config.MAX_STEPS_LONG,
            logfile_name=run_id,
            log_overwrite=True,
            task_id=run_id
        )

    seconds = round(time.time() - started, 1)

    return run_id, answer, seconds


def main():
    names, repeats, series = read_arguments()
    config.USE_CACHE = series.startswith("cache")

    task = load_task()
    os.makedirs("logs", exist_ok=True)
    rows = []

    for repeat in range(1, repeats + 1):
        for name in names:

            run_id, answer, seconds = run_once(
                name,
                repeat,
                series,
                task
            )

            right = is_correct(
                answer,
                task["expected"]
            )

            rows.append(make_row(run_id, name, right, seconds))
            print(
                f"\n[{run_id}] час {seconds} с "
                f"| правильно: {'так' if right else 'ні'}"
            )

            print(
                f"[{run_id}] відповідь: "
                f"{(answer or '').replace(chr(10), ' ')[:200]}"
            )

    get_client().flush()
    print_table(rows)
    with open(f"logs/{series}_results.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
