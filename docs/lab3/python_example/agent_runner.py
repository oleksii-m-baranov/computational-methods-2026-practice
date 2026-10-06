"""Прогін агента на всіх питаннях із tasks.json."""
import json

from agent import run_agent
from utils.lab_logger import custom_logger

import config
from langfuse import get_client, propagate_attributes


logger = custom_logger('lab3')

with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)

    for task in tasks:
        logger.info(f"\n=== {task['id']} | очікується: {task['expected']}")
        with propagate_attributes(trace_name=f"{config.RUN_TAG}-{task['id']}",
                                  tags=[config.RUN_TAG]):
            run_agent(task["question"])

get_client().flush()
logger.info(f"\nОброблено задач: {len(tasks)}. Лог: lab3.log")
