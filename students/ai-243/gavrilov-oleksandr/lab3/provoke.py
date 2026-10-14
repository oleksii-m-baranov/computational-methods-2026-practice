"""Провокування помилок моделі для розбору перевірок (крок 9)."""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import json

from langfuse import get_client, propagate_attributes

import config
from agent import run_agent
from utils.lab_logger import custom_logger

logger = custom_logger('lab3_provoke', overwrite=True)

with open("provoking_tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)

    for task in tasks:
        logger.info(f"\n### {task['id']} | що провокуємо: {task['provokes']}")
        with propagate_attributes(trace_name=f"provoke-{task['id']}",
                                  tags=["checks"]):
            run_agent(task["question"])

get_client().flush()
logger.info(f"\nОброблено задач: {len(tasks)}.")