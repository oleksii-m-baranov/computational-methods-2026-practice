"""Запуск агента на всіх тестових завданнях."""

import json
from agent import run_agent
from utils.lab_logger import custom_logger

logger = custom_logger("lab2")

with open("tasks.json", encoding="utf-8") as file:
    tasks = json.load(file)

for task in tasks:
    logger.info(
        f"\n=== {task['id']} | Очікується: {task['expected']}"
    )
    run_agent(task["question"])

logger.info(
    f"\nОброблено завдань: {len(tasks)}. Лог: lab2.log"
)