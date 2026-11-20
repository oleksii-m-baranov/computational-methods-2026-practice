"""Прогін агента на всіх питаннях із tasks.json із трасуванням Langfuse."""

import json

import config
from agent import run_agent
from langfuse import get_client, propagate_attributes
from utils.lab_logger import custom_logger


logger = custom_logger("lab3_checks")


with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)


for task in tasks:
    logger.info(
        f"\n=== {task['id']} | "
        f"очікується: {task['expected']}"
    )

    # Окрема траса для кожного тестового завдання
    with propagate_attributes(
        trace_name=f"{config.RUN_TAG}-{task['id']}",
        tags=[config.RUN_TAG],
    ):
        answer = run_agent(task["question"])

    logger.info(f"Отримана відповідь: {answer}")


# Передаємо накопичені траси до Langfuse
get_client().flush()

logger.info(
    f"\nОброблено задач: {len(tasks)}. Лог: lab3_checks.log"
)