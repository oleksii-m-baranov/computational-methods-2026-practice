"""Run the agent on all benchmark tasks from tasks.json."""
import os
import sys

# Додаємо корінь проєкту до sys.path для імпорту загальнодоступного логера utils.lab_logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

import json
from agent import run_agent
from utils.lab_logger import custom_logger

if __name__ == "__main__":
    logger = custom_logger('lab2', overwrite=True)

    with open("tasks.json", encoding="utf-8") as f:
        tasks = json.load(f)

    for task in tasks:
        logger.info(f"\n=== {task['id']} | очікується: {task['expected']}")
        run_agent(task["question"])

    logger.info(f"\nОброблено задач: {len(tasks)}. Лог: logs/lab2.log")
