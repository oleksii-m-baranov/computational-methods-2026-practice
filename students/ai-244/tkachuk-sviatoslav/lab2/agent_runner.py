"""Запуск п'яти завдань із tasks.json та створення підсумкового логу."""
import json
from pathlib import Path
from shutil import copyfile
from agent import run_agent
from utils.lab_logger import custom_logger

# Логер у utils пише до logs/lab2.log.
# У методичці водночас згадані lab2.log і log2.lab у корені лабораторної.
logger = custom_logger("lab2", overwrite=True)

with Path("tasks.json").open(encoding="utf-8") as f:
    tasks = json.load(f)

for task in tasks:
    logger.info(f"\n=== {task['id']} | очікується: {task['expected']}")
    try:
        run_agent(task["question"])
    except Exception as exc:
        # Навіть якщо Ollama відключився, фіксуємо причину у логу.
        logger.error(f"Помилка запуску агента для {task['id']}: {exc}")
        raise

logger.info(f"\nОброблено задач: {len(tasks)}. Лог: logs/lab2.log")
for handler in logger.handlers:
    handler.flush()
source = Path(__file__).resolve().parent / "logs" / "lab2.log"
# Обидві назви, щоб задовольнити суперечливі назви в методичці.
copyfile(source, "lab2.log")
copyfile(source, "log2.lab")
print("Готово: lab2.log, log2.lab; далі: python analyze_log.py")
