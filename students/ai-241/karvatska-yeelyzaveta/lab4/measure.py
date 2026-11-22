
import json
import os
import sys
import time

from langfuse import get_client, propagate_attributes

import agent
import config
from table import make_row, print_table


# Конфігурації: які налаштування config змінюємо перед прогоном
CONFIGS = {
    "none": {"COMPRESS": "none", "USE_STATE": False},
    "trim": {"COMPRESS": "trim", "USE_STATE": False},
    "trim+state": {"COMPRESS": "trim", "USE_STATE": True},
    "summary": {"COMPRESS": "summary", "USE_STATE": False},
}


def read_arguments():
    """Читає параметри запуску."""
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    series = sys.argv[3] if len(sys.argv) > 3 else "main"

    names = list(CONFIGS) if which == "all" else [which]

    if any(name not in CONFIGS for name in names):
        raise ValueError(f"Невідома конфігурація: {which}")

    return names, repeats, series


def load_task():
    """Читає довгу задачу з файла long_task.json."""
    with open("long_task.json", encoding="utf-8") as f:
        return json.load(f)


def is_correct(answer, expected):
    """Перевіряє, чи є очікуване число у відповіді."""
    if not answer:
        return False

    text = answer.replace(" ", "").replace(",", ".")
    return str(expected) in text


def run_once(name, repeat, series, task):
    """Виконує один прогін агента."""
    for key, value in CONFIGS[name].items():
        setattr(config, key, value)

    run_id = f"{series}_{name}_r{repeat}"

    started = time.time()

    with propagate_attributes(
        trace_name=f"long-{run_id}",
        tags=[series, name],
    ):
        answer = agent.run_agent(
            task=task["question"],
            max_steps=config.MAX_STEPS_LONG,
            min_tool_calls=task.get("min_calls", 0),
            logfile_name=run_id,
            task_id=run_id,
            log_overwrite=True,
        )

    seconds = round(time.time() - started, 1)

    timings_path = "logs/timings.csv"
    write_header = not os.path.exists(timings_path) or os.path.getsize(timings_path) == 0

    with open(timings_path, "a", encoding="utf-8") as f:
        if write_header:
            f.write("run_id,seconds\n")
        f.write(f"{run_id},{seconds}\n")

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
                name, repeat, series, task
            )

            right = is_correct(answer, task["expected"])
            rows.append(make_row(run_id, name, right, seconds))

            print(
                f"\n[{run_id}] час {seconds} с | "
                f"правильно: {'так' if right else 'ні'}"
            )

            print(
                f"[{run_id}] відповідь: "
                f"{(answer or '').replace(chr(10), ' ')[:200]}"
            )

    get_client().flush()
    print_table(rows)


if __name__ == "__main__":
    main()
