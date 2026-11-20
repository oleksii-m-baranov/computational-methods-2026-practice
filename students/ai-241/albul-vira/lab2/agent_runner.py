"""Прогін агента на всіх питаннях із tasks.json."""
import json
import sys
from pathlib import Path

current_dir = Path(__file__).resolve()
for parent in [current_dir] + list(current_dir.parents):
    if (parent / "utils").is_dir():
        if str(parent) not in sys.path:
            sys.path.insert(0, str(parent))
        break

from agent import run_agent
from utils.lab_logger import custom_logger

logger = custom_logger('lab2')

with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)

for task in tasks:
    logger.info(f"\n=== {task['id']} | очікується: {task['expected']}")
    run_agent(task["question"])

logger.info(f"\nОброблено задач: {len(tasks)}. Лог збережено в lab2.log")
