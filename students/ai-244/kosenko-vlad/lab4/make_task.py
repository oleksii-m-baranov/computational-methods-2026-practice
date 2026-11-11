"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py

Варіант 9 (вибір ноутбука): шість моделей, для кожної - опис у корпусі,
ціна з довідника і щомісячний платіж при розстрочці на задану кількість місяців.
"""
import json
import re

# Беремо власні функції-інструменти з tools.py
from tools import calc_installment, laptop_info

# Шість позицій. У варіанті 9 кожна позиція - пара (модель, кількість місяців розстрочки).
ITEMS = [("Nexora StudyTab 13", 10), ("VividCanvas Studio 16", 10), ("CodeCraft Nomad 14", 10),
         ("DeskMate Prime 15", 5), ("DevCore Matrix 16", 8), ("ChronoWork Lite 14", 4)]

# Питання для агента. У ньому має бути перелік усіх шести позицій.
QUESTION = (
    "Для кожного з шести ноутбуків: Nexora StudyTab 13 на 10 місяців, VividCanvas Studio 16 на 10 місяців, "
    "CodeCraft Nomad 14 на 10 місяців, DeskMate Prime 15 на 5 місяців, DevCore Matrix 16 на 8 місяців, "
    "ChronoWork Lite 14 на 4 місяці. Для кожного: (а) знайди в корпусі описів, для чого призначена модель, "
    "і наведи одним реченням; (б) знайди в довіднику ціну моделі; (в) порахуй щомісячний платіж "
    "при розстрочці на вказану кількість місяців без переплати (переплата 0%). "
    "У кінці назви суму щомісячних платежів за всіма шістьма ноутбуками одним числом."
)

# Мінімум викликів інструментів для повного розв'язання: шість позицій по три інструменти.
MIN_CALLS = 18


def price_of(model):
    """Ціна моделі з довідника: дістаємо число з тексту, який повертає laptop_info."""
    return float(re.search(r"Ціна: (\d+)", laptop_info(model)).group(1))


def payment_of_one(model, months):
    """Щомісячний платіж за однією моделлю: через calc_installment без переплати."""
    text = calc_installment(price_of(model), months, 0)
    return float(text.split(" грн")[0])


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
