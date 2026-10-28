"""Запуск і аналіз довгої задачі агента."""

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
    "summary": {"COMPRESS": "summary", "USE_STATE": False},
}

MAIN_CONFIGS = ["none", "trim", "trim+state"]


def read_arguments():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    series = sys.argv[3] if len(sys.argv) > 3 else "main"

    if which == "all":
        names = MAIN_CONFIGS
    elif which in CONFIGS:
        names = [which]
    else:
        raise ValueError(f"Невідома конфігурація: {which}")

    return names, repeats, series


def load_task():
    with open("long_task.json", encoding="utf-8") as f:
        return json.load(f)


def is_correct(answer, expected):
    """Перевіряє наявність очікуваного числа у відповіді."""
    if not answer:
        return False

    text = answer.replace(" ", "").replace(",", ".")
    return str(expected) in text


def run_once(name, repeat, series, task):
    """Запускає один прогін з окремим логом і станом."""
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
            logfile_name=run_id,
            task_id=run_id,
            log_overwrite=True,
        )

    return run_id, answer, round(time.time() - started, 1)


def analyze_existing():
    """Аналізує дев'ять старих прогонів без запуску моделі."""
    task = load_task()

    # Часи з попередніх реальних запусків.
    durations = {
        "main_none_r1": 170.1,
        "main_trim_r1": 174.7,
        "main_trim+state_r1": 154.3,
        "main_none_r2": 155.5,
        "main_trim_r2": 156.4,
        "main_trim+state_r2": 157.2,
        "main_none_r3": 151.0,
        "main_trim_r3": 154.7,
        "main_trim+state_r3": 154.1,
    }

    rows = []

    for repeat in range(1, 4):
        for name in MAIN_CONFIGS:
            run_id = f"main_{name}_r{repeat}"

            with open(
                f"logs/{run_id}.log",
                encoding="utf-8",
            ) as f:
                content = f.read()

            answer = None

            for line in content.splitlines():
                if "ВІДПОВІДЬ:" in line:
                    answer = line.split(
                        "ВІДПОВІДЬ:", 1
                    )[1].strip()

            right = is_correct(
                answer,
                task["expected"],
            )

            rows.append(
                make_row(
                    run_id,
                    name,
                    right,
                    durations[run_id],
                )
            )

    print_table(rows)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "existing":
        analyze_existing()
        return

    names, repeats, series = read_arguments()
    task = load_task()

    # Кеш дозволений лише для окремих кеш-серій.
    config.USE_CACHE = series.startswith("cache")

    os.makedirs("logs", exist_ok=True)
    rows = []

    for repeat in range(1, repeats + 1):
        for name in names:
            run_id, answer, seconds = run_once(
                name, repeat, series, task
            )

            right = is_correct(
                answer,
                task["expected"],
            )

            rows.append(
                make_row(
                    run_id,
                    name,
                    right,
                    seconds,
                )
            )

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