"""Прогін агента на всіх питаннях із tasks.json."""
import json
from agent import run_agent
from utils.lab_logger import custom_logger

logger = custom_logger('lab2')


with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)

    for task in tasks:
        logger.info(f"\n=== {task['id']} | очікується: {task['expected']}")
        run_agent(task["question"])

logger.info(f"\nОброблено задач: {len(tasks)}. Лог: lab2.log")
