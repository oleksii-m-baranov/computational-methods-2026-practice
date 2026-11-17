import json

from langfuse import get_client, propagate_attributes

import config
from agent import run_agent
from lab_logger import custom_logger


RUN_TAG = getattr(config, "RUN_TAG", "checks")

logger = custom_logger(config.LAB_LOGFILE_NAME)


def main():
    with open("tasks.json", encoding="utf-8") as f:
        tasks = json.load(f)

    total = len(tasks)
    completed = 0
    failed = 0

    logger.info(f"=== ПОЧАТОК ЕКСПЕРИМЕНТУ: {RUN_TAG} ===")
    logger.info(f"Кількість завдань: {total}")

    try:
        for task in tasks:
            task_id = task["id"]
            question = task["question"]
            expected = task.get("expected", "не вказано")

            logger.info(
                f"\n=== {task_id} | очікується: {expected} ==="
            )

            try:
                with propagate_attributes(
                    trace_name=f"{RUN_TAG}-{task_id}",
                    tags=["lab3", RUN_TAG],
                ):
                    result = run_agent(question)

                logger.info(f"Результат агента: {result}")
                completed += 1

            except Exception as error:
                failed += 1
                logger.error(
                    f"ПОМИЛКА ЗАВДАННЯ {task_id}: {error}"
                )

    finally:
        get_client().flush()

    logger.info("\n=== ПІДСУМОК ЕКСПЕРИМЕНТУ ===")
    logger.info(f"Режим: {RUN_TAG}")
    logger.info(f"Усього завдань: {total}")
    logger.info(f"Завершено без винятків: {completed}")
    logger.info(f"Помилок виконання: {failed}")
    logger.info(f"Лог: {config.LAB_LOGFILE_NAME}.log")


if __name__ == "__main__":
    main()
