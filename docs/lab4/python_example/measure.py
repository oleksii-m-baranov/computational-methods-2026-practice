"""Запуск довгої задачі в заданій конфігурації.

Запуск:
    python measure.py none 1 probe
де none - конфігурація, 1 - кількість повторів, probe - назва серії.
Лог кожного прогону: logs/<серія>_<конфігурація>_r<повтор>.log
"""
import json
import sys
import time

from langfuse import get_client, propagate_attributes

import agent
import config
from table import make_row, print_table

# Конфігурації: які налаштування config змінюємо перед прогоном
CONFIGS = {
    "none":       {"COMPRESS": "none", "USE_STATE": False},
    "trim":       {"COMPRESS": "trim", "USE_STATE": False},
    "trim+state": {"COMPRESS": "trim", "USE_STATE": True},
    "summary":    {"COMPRESS": "summary", "USE_STATE": False},
}


def read_arguments():
    """Читає параметри запуску. Повертає (список конфігурацій, кількість повторів, серія)."""
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    series = sys.argv[3] if len(sys.argv) > 3 else "main"
    names = list(CONFIGS) if which == "all" else [which]
    return names, repeats, series


def load_task():
    """Читає довгу задачу з файла long_task.json."""
    with open("long_task.json", encoding="utf-8") as f:
        return json.load(f)


def is_correct(answer, expected):
    """Чи є очікуване число у відповіді. Неправильні відповіді перевіряйте вручну."""
    if not answer:
        return False
    text = answer.replace(" ", "").replace(",", ".")     # прибираємо пробіли, кому міняємо на крапку
    return str(expected) in text


def run_once(name, repeat, series, task):
    """Один прогін агента. Повертає (номер прогону, відповідь, час у секундах)."""
    for key, value in CONFIGS[name].items():             # застосовуємо налаштування конфігурації
        setattr(config, key, value)
    run_id = f"{series}_{name}_r{repeat}"                # наприклад: probe_none_r1

    started = time.time()
    # propagate_attributes дає трасі в Langfuse назву й мітки
    with propagate_attributes(trace_name=f"long-{run_id}", tags=[series, name]):
        answer = agent.run_agent(task["question"],
                                 max_steps=config.MAX_STEPS_LONG,
                                 logfile_name=run_id,
                                 task_id=run_id,
                                 log_overwrite=True)
    return run_id, answer, round(time.time() - started, 1)


def main():
    names, repeats, series = read_arguments()
    config.USE_CACHE = series.startswith("cache")  # кеш вмикають лише серії, назва яких починається з cache
    task = load_task()
    rows = []  # сюди збираємо рядки результатів

    for repeat in range(1, repeats + 1):                 # повтори - зовнішній цикл,
        for name in names:                               # тож конфігурації чергуються
            run_id, answer, seconds = run_once(name, repeat, series, task)
            right = is_correct(answer, task["expected"])
            rows.append(make_row(run_id, name, right, seconds))
            print(f"\n[{run_id}] час {seconds} с | правильно: {'так' if right else 'ні'}")
            print(f"[{run_id}] відповідь: {(answer or '').replace(chr(10), ' ')[:200]}")

    get_client().flush()                                 # дочекатися відправки трас у Langfuse
    print_table(rows)


if __name__ == "__main__":
    main()