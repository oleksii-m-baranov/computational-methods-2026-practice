import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent import run_agent
from utils.lab_logger import custom_logger


logger = custom_logger("lab2_runner")


def main():
    with open("tasks.json", encoding="utf-8") as f:
        tasks = json.load(f)

    for item in tasks:
        print("\n" + "=" * 60)
        print(f"Завдання {item['id']}: {item['task']}")

        try:
            answer = run_agent(item["task"])
            print(f"Відповідь агента: {answer}")
            print(f"Очікуваний результат: {item['expected']}")

            logger.info(
                "Завершено тест %s | Очікуваний результат: %s",
                item["id"],
                item["expected"],
            )

        except Exception as e:
            print(f"ПОМИЛКА: {e}")
            logger.exception("Помилка в тесті %s", item["id"])

    print("\nТестування завершено. Перевір файл lab2.log.")


if __name__ == "__main__":
    main()
