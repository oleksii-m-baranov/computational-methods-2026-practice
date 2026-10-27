"""Прогін агента на всіх питаннях із tasks.json для перевірки звичайних задач та пасток."""

import json

from agent import run_agent
from utils.lab_logger import custom_logger

logger = custom_logger("lab2")

# Завантажуємо tasks.json
with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)

print(f"Починаємо тестування агента. Загалом задач: {len(tasks)}\n")

for task in tasks:
    task_id = task["id"]
    task_type = task.get("type", "regular")
    question = task["question"]
    expected = task["expected"]

    # Формуємо заголовок залежно від типу задачі (звичайна чи пастка)
    if task_type == "trap":
        badge = "🚨 ТЕСТ-ПАСТКА"
        trap_desc = task.get("trap_description", "")
        expected_behavior = task.get("expected_behavior", "")
        log_message = (
            f"\n{'='*50}\n"
            f"=== [{badge}] {task_id} ===\n"
            f"Питання: {question}\n"
            f"Очікувана поведінка: {expected}\n"
            f"Суть пастки: {trap_desc}\n"
            f"{'='*50}"
        )
    else:
        badge = "🔍 ЗВИЧАЙНА ЗАДАЧА"
        log_message = (
            f"\n{'-'*50}\n"
            f"=== [{badge}] {task_id} ===\n"
            f"Питання: {question}\n"
            f"Очікується: {expected}\n"
            f"{'-'*50}"
        )

    logger.info(log_message)
    print(log_message)

    # Викликаємо агента для поточного запитання
    try:
        agent_response = run_agent(question)
        logger.info(f"Відповідь агента:\n{agent_response}\n")
        print(f"👉 Відповідь агента:\n{agent_response}\n")
    except Exception as e:
        error_msg = f"Помилка під час виконання задачі {task_id}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}\n")

completion_message = f"\nОброблено задач: {len(tasks)}. Перевірте лог-файл: lab2.log"
logger.info(completion_message)
print(completion_message)