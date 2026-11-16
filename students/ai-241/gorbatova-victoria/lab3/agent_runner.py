"""Прогін агента на всіх питаннях із tasks.json."""

"""Прогін агента на всіх питаннях із tasks.json."""

import json
<<<<<<< Updated upstream
=======
from langfuse import get_client, propagate_attributes
import config
>>>>>>> Stashed changes
from agent import run_agent
from utils.lab_logger import custom_logger
import config
from langfuse import get_client

logger = custom_logger(config.LAB_LOGFILE_NAME)

with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)

for task in tasks:
<<<<<<< Updated upstream
    logger.info(f"\n=== {task['id']} | очікується: {task['expected']}")
    run_agent(task["question"])

get_client().flush()
logger.info(f"\nОброблено задач: {len(tasks)}. Лог: {config.LAB_LOGFILE_NAME}.log")
=======
    logger.info(f"\n### {task['id']} | очікується: {task['expected']}")
    # Використовуємо Langfuse v4 API для трасування
    with propagate_attributes(trace_name=f"{config.RUN_TAG}-{task['id']}",
                              tags=[config.RUN_TAG]):
        run_agent(task["question"])

get_client().flush()
logger.info(f"\nОброблено задач: {len(tasks)}. Лог записано у {config.LAB_LOGFILE_NAME}.log")
>>>>>>> Stashed changes
