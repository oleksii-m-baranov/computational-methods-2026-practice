
"""Запуск набору завдань із трасуванням Langfuse."""

import json

from langfuse import get_client, propagate_attributes

import config
from agent import run_agent
from utils.lab_logger import custom_logger


logger = custom_logger("lab3_runner")


def main():
    with open("tasks.json", "r", encoding="utf-8") as file:
        tasks = json.load(file)

    for task in tasks:
        trace_name = f"{config.RUN_TAG}-{task['id']}"

        logger.info(
            f"=== {task['id']} | Очікується: {task['expected']}"
        )

        with propagate_attributes(
            trace_name=trace_name,
            tags=[config.RUN_TAG],
        ):
            result = run_agent(task["question"])
            logger.info(f"ВІДПОВІДЬ: {result}")

    get_client().flush()
    logger.info(f"Оброблено завдань: {len(tasks)}")


if __name__ == "__main__":
    main()
