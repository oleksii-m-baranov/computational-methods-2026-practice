"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py

Варіант 9 — Вибір ноутбука.
"""
import json

from tools import calc_installment, laptop_info

# Шість позицій. У варіанті 9 кожна позиція - пара (модель ноутбука, кількість місяців розстрочки).
ITEMS = [
    ("StudyBook 15", 9),
    ("CodeMaster Pro", 10),
    ("GameForce X17", 10),
    ("PixelCraft Studio", 9),
    ("SlimAir 13", 8),
    ("BudgetBook 11", 5),
]

# Питання для агента. У ньому має бути перелік усіх шести позицій.
QUESTION = (
    "Для кожної з шести моделей ноутбуків: StudyBook 15 (розстрочка на 9 місяців), "
    "CodeMaster Pro (розстрочка на 10 місяців), GameForce X17 (розстрочка на 10 місяців), "
    "PixelCraft Studio (розстрочка на 9 місяців), SlimAir 13 (розстрочка на 8 місяців), "
    "BudgetBook 11 (розстрочка на 5 місяців). Для кожної: "
    "(а) знайди в корпусі опис моделі (її призначення та особливості) і наведи одним реченням; "
    "(б) знайди в довіднику ціну моделі; "
    "(в) порахуй щомісячний платіж при розстрочці без переплати (0%) на задану кількість місяців. "
    "У кінці назви суму щомісячних платежів усіх шести моделей одним числом."
)

# Мінімум викликів інструментів для повного розв'язання: шість позицій по три інструменти.
MIN_CALLS = 18


def payment_of_one(model, months):
    """Щомісячний платіж для однієї моделі ноутбука при розстрочці без переплати (0%)."""
    info = laptop_info(model)                        # рядок із довідника: "Ціна: 27000 грн, ..."
    price = float(info.split()[1])                   # ціна з довідника
    result = calc_installment(price, months, 0)      # розрахунок платежу через інструмент
    return float(result.split()[0])                  # щомісячний платіж


def compute():
    """Правильна відповідь: сума щомісячних платежів по всіх шести позиціях. Рахуємо самі, без моделі."""
    total = 0.0
    for model, months in ITEMS:
        total = total + payment_of_one(model, months)
    return total


def save_task(total):
    """Записує питання, правильну відповідь і MIN_CALLS у файл long_task.json."""
    task = {
        "id": "L1",
        "question": QUESTION,
        "expected": format(round(total, 2), "g"),   # число як текст, без зайвих нулів
        "min_calls": MIN_CALLS,
    }
    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


task = save_task(compute())
print("Правильна відповідь:", task["expected"])
print("Файл long_task.json записано")
