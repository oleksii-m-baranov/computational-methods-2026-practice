"""Запуск усіх п'яти завдань лабораторної роботи №2."""

import json
from agent import run_agent
from utils.lab_logger import custom_logger

logger = custom_logger("lab2")

with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)

for task in tasks:
    logger.info(
        f"\n=== {task['id']} | очікується: {task['expected']}"
    )

    try:
        run_agent(task["question"])
    except Exception as error:
        logger.error(f"ПОМИЛКА ЗАДАЧІ {task['id']}: {error}")

logger.info(
    f"\nОброблено задач: {len(tasks)}. Лог: lab2.log"
)
