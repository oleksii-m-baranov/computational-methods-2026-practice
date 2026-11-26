
"""Запуск Baseline на всіх тестових завданнях із трасуванням Langfuse."""

import json

from langfuse import get_client, propagate_attributes

import config
from baseline_agent import run_agent
from utils.lab_logger import custom_logger

logger = custom_logger("lab3_baseline_runner")


def main():
    with open("tasks.json", encoding="utf-8") as file:
        tasks = json.load(file)

    for task in tasks:
        trace_name = f"baseline-{task['id']}"

        logger.info(
            f"\n=== {task['id']} | Очікується: {task['expected']}"
        )

        with propagate_attributes(
            trace_name=trace_name,
            tags=["baseline"],
        ):
            result = run_agent(task["question"])
            logger.info(f"ВІДПОВІДЬ: {result}")

    get_client().flush()
    logger.info(f"Оброблено завдань: {len(tasks)}")


if __name__ == "__main__":
    main()
