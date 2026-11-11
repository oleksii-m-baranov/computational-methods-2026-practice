"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск: python make_task.py

Варіант 9 — вибір ноутбука.
"""
import json

# Беремо власні функції-інструменти з tools.py.
from tools import laptop_info, calc_installment

# Шість моделей ноутбуків.
ITEMS = [
    "StudyBook 14",
    "OfficeMate 15",
    "TravelLite 14",
    "CodeNova 15",
    "GameStorm X15",
    "ArtVision 15",
]

# Питання для агента. У ньому має бути перелік усіх шести позицій.
QUESTION = (
    "Для кожної з шести моделей ноутбуків: StudyBook 14, OfficeMate 15, TravelLite 14, "
    "CodeNova 15, GameStorm X15, ArtVision 15. Для кожної: "
    "(а) знайди в корпусі опис моделі й наведи його одним реченням; "
    "(б) знайди в довіднику ціну моделі; "
    "(в) порахуй щомісячний платіж при розстрочці на 6 місяців із переплатою 10%. "
    "У кінці назви суму щомісячних платежів усіх шести ноутбуків одним числом."
)

# Мінімум викликів інструментів: шість моделей по три інструменти.
MIN_CALLS = 18


def cost_of_one(model):
    """Щомісячний платіж для одного ноутбука."""
    info = laptop_info(model)
    price = float(info.split(":")[1].split()[0])
    payment = calc_installment(price, 6, 10)
    return float(payment.split()[0])


def compute():
    """Правильна відповідь: сума по всіх шести моделях. Рахуємо самі, без моделі."""
    total = 0.0
    for model in ITEMS:
        total = total + cost_of_one(model)
    return total


def save_task(total):
    """Записує питання, правильну відповідь і MIN_CALLS у файл long_task.json."""
    task = {
        "id": "L1",
        "question": QUESTION,
        "expected": format(round(total, 2), "g"),
        "min_calls": MIN_CALLS,
    }
    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


task = save_task(compute())
print("Правильна відповідь:", task["expected"])
print("Файл long_task.json записано")