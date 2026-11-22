import json

from langfuse import get_client, propagate_attributes

import config
from agent import run_agent
from utils.lab_logger import custom_logger


logger = custom_logger("lab3_runner", f"lab3_{config.RUN_TAG}.log")


def main():
    with open("tasks.json", encoding="utf-8") as f:
        tasks = json.load(f)

    try:
        for item in tasks:
            print("\n" + "=" * 60)
            print(f"Завдання {item['id']}: {item['task']}")

            try:
                with propagate_attributes(
                    trace_name=f"{config.RUN_TAG}-{item['id']}",
                    tags=[config.RUN_TAG],
                ):
                    answer = run_agent(item["task"])

                print(f"Відповідь агента: {answer}")
                print(f"Очікуваний результат: {item['expected']}")

                logger.info(
                    "Завершено тест %s | Очікуваний результат: %s",
                    item["id"],
                    item["expected"],
                )

            except Exception as error:
                print(f"ПОМИЛКА: {error}")
                logger.exception("Помилка в тесті %s", item["id"])

    finally:
        get_client().flush()

    print(f"\nТестування завершено. Перевір файл lab3_{config.RUN_TAG}.log.")


if __name__ == "__main__":
    main()
