"""Запуск п'яти задач та запис трас у Langfuse."""

import json
import os
import sys

# Підключення utils з кореня репозиторію
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", ".."
        )
    ),
)

from langfuse import get_client, propagate_attributes

import config
from agent import run_agent
from utils.lab_logger import custom_logger


logger = custom_logger(config.LAB_LOGFILE_NAME)


with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)


for task in tasks:

    logger.info(
        f"\n=== {task['id']} | "
        f"очікується: {task['expected']}"
    )

    with propagate_attributes(
        trace_name=f"{config.RUN_TAG}-{task['id']}",
        tags=[config.RUN_TAG],
    ):
        run_agent(task["question"])


# Обов'язково відправляємо всі події
get_client().flush()

logger.info(
    f"\nОброблено задач: {len(tasks)}. "
    f"Лог: {config.LAB_LOGFILE_NAME}.log"
)
