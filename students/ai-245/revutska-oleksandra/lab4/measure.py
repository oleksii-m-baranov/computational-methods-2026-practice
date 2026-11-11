

"""Запуск експериментів із контекстом, станом і кешем агента."""

import json
import sys
from pathlib import Path

from langfuse import get_client, propagate_attributes

import config
from agent import run_agent
from model import clear_cache, get_cache_stats


MODES = {
    "none": {
        "compress": "none",
        "state": False,
        "cache": False,
    },
    "trim": {
        "compress": "trim",
        "state": False,
        "cache": False,
    },
    "trim_state": {
        "compress": "trim",
        "state": True,
        "cache": False,
    },
    "cache": {
        "compress": "none",
        "state": False,
        "cache": True,
    },
}


def configure_mode(mode):
    """Встановлює налаштування вибраного експерименту."""

    settings = MODES[mode]

    config.COMPRESS = settings["compress"]
    config.USE_STATE = settings["state"]
    config.USE_CACHE = settings["cache"]

    config.RUN_TAG = mode


def main():
    if len(sys.argv) != 4:
        print(
            "Використання: "
            "python measure.py <mode> <run> <tag>"
        )
        sys.exit(1)

    mode = sys.argv[1]

    if mode not in MODES:
        raise ValueError(f"Невідомий режим: {mode}")

    try:
        run_number = int(sys.argv[2])
    except ValueError:
        raise ValueError("Номер запуску має бути цілим числом")

    tag = sys.argv[3]

    configure_mode(mode)

    with open("long_task.json", encoding="utf-8") as f:
        task_data = json.load(f)

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    result_path = (
        logs_dir / f"{tag}_{mode}_r{run_number}.log"
    )

    steps_path = (
        logs_dir / f"{tag}_{mode}_steps_r{run_number}.log"
    )

    # Кожен експеримент починається з порожнього кешу.
    clear_cache()

    # Основний лог агента накопичує запуски.
    # Запам'ятовуємо його поточний розмір.
    agent_log = logs_dir / f"{config.LAB_LOGFILE_NAME}.log"

    old_log_size = (
        agent_log.stat().st_size
        if agent_log.exists()
        else 0
    )

    print(f"Режим: {mode}")
    print(f"Запуск: {run_number}")
    print(f"Задача: {task_data['id']}")
    print(f"Мінімум викликів: {task_data['min_calls']}")
    print(f"COMPRESS: {config.COMPRESS}")
    print(f"USE_STATE: {config.USE_STATE}")
    print(f"USE_CACHE: {config.USE_CACHE}")

    with propagate_attributes(
        trace_name=f"{tag}-{mode}-r{run_number}",
        tags=[tag, mode],
    ):
        answer = run_agent(
            task_data["task"],
            max_steps=config.MAX_STEPS_LONG,
        )

    # Зберігаємо тільки записи поточного запуску.
    if agent_log.exists():
        with agent_log.open("rb") as f:
            f.seek(old_log_size)
            new_log = f.read()

        steps_path.write_text(
            new_log.decode("utf-8", errors="replace"),
            encoding="utf-8",
        )

    cache_stats = get_cache_stats()

    with result_path.open("w", encoding="utf-8") as f:
        f.write(f"mode={mode}\n")
        f.write(f"run={run_number}\n")
        f.write(f"task_id={task_data['id']}\n")
        f.write(
            f"expected={task_data['expected']['total_fine']}\n"
        )
        f.write(f"compress={config.COMPRESS}\n")
        f.write(f"use_state={config.USE_STATE}\n")
        f.write(f"use_cache={config.USE_CACHE}\n")
        f.write(f"cache_hits={cache_stats['hits']}\n")
        f.write(f"cache_misses={cache_stats['misses']}\n")
        f.write(f"cache_size={cache_stats['size']}\n")
        f.write(f"answer={answer}\n")

    print("\n=== РЕЗУЛЬТАТ ЕКСПЕРИМЕНТУ ===")
    print("Відповідь агента:", answer)
    print("Статистика кешу:", cache_stats)
    print("Файл результату:", result_path)
    print("Файл кроків:", steps_path)

    get_client().flush()


if __name__ == "__main__":
    main()
