"""Прогін агента на всіх питаннях із tasks.json."""
import json

from langfuse import get_client, propagate_attributes

import config

if config.RUN_TAG == "baseline":
    from agent_baseline import run_agent    # агент лабораторної № 2 + трасування
else:
    from agent import run_agent             # агент з перевірками (крок 6)

from utils.lab_logger import custom_logger

logger = custom_logger(config.LAB_LOGFILE_NAME)

with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)

    for task in tasks:
        logger.info(f"\n### {task['id']} | очікується: {task['expected']}")
        # назва траси (наприклад, baseline-Z1) і мітка прогону
        with propagate_attributes(trace_name=f"{config.RUN_TAG}-{task['id']}",
                                  tags=[config.RUN_TAG]):
            run_agent(task["question"])

get_client().flush()    # дочекатися відправки подій у Langfuse
logger.info(f"\nОброблено задач: {len(tasks)}. Лог: {config.LAB_LOGFILE_NAME}.log")
