"""Прогін п’яти задач із перевірками та записом трас Langfuse."""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from utils.lab_logger import custom_logger
import config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", choices=["checks"], default="checks")
    options = parser.parse_args()
    os.chdir(HERE)
    config.RUN_TAG = options.run
    logger = custom_logger(config.LAB_LOGFILE_NAME, overwrite=True)
    from agent import run_agent
    from langfuse import get_client, propagate_attributes

    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        raise SystemExit("Не задано ключі Langfuse у файлі .env")

    with (HERE / "tasks.json").open(encoding="utf-8") as f:
        tasks = json.load(f)
    logger.info(f"РЕЖИМ: {options.run} | модель: {config.MODEL} | temperature={config.TEMPERATURE}")
    for task in tasks:
        logger.info(f"\n=== {task['id']} | очікується: {task['expected']}")
        with propagate_attributes(trace_name=f"{config.RUN_TAG}-{task['id']}", tags=[config.RUN_TAG]):
            run_agent(task["question"])
    get_client().flush()
    logger.info(f"\nОброблено задач: {len(tasks)}. Прогін: {config.RUN_TAG}")
    for handler in logger.handlers:
        handler.flush()
    shutil.copy2(HERE / "logs" / f"{config.LAB_LOGFILE_NAME}.log", HERE / "lab3_checks.log")


if __name__ == "__main__":
    main()
