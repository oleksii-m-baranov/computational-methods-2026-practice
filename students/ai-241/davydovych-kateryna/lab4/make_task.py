"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py

Варіант 9 (вибір ноутбука): шість моделей, для кожної – опис з корпусу,
ціна з довідника і щомісячний платіж при розстрочці на задану кількість місяців.
"""
import json

# Власні функції-інструменти з tools.py
from tools import calc_installment, laptop_info, search_laptops

OVERPAY = 10   # переплата за весь строк розстрочки, %

# Шість позицій: (модель, кількість місяців розстрочки)
ITEMS = [("StudyBook 14", 6), ("OfficeMate 15", 10), ("NovaStrike G5", 18),
         ("PaperLite Air", 12), ("CodeMaster Pro", 16), ("PixelCanvas 16", 20)]

# Питання для агента. У ньому перелік усіх шести позицій.
QUESTION = (
    "Для кожної з шести моделей ноутбуків: StudyBook 14 (розстрочка на 6 місяців), "
    "OfficeMate 15 (на 10 місяців), NovaStrike G5 (на 18 місяців), PaperLite Air (на 12 місяців), "
    "CodeMaster Pro (на 16 місяців), PixelCanvas 16 (на 20 місяців). "
    "Для кожної: (а) знайди в каталозі опис моделі і наведи одним реченням, для чого вона; "
    "(б) знайди в довіднику ціну моделі; "
    "(в) порахуй щомісячний платіж при розстрочці на вказану кількість місяців з переплатою 10%. "
    "У кінці назви суму щомісячних платежів усіх шести моделей одним числом."
)

# Мінімум викликів інструментів: шість позицій по три інструменти
MIN_CALLS = 18


def price_of(model):
    """Ціна моделі з довідника: дістаємо число з тексту, який повертає laptop_info."""
    text = laptop_info(model)                      # "Ціна: 24000 грн, на складі: ..."
    return float(text.split("Ціна: ")[1].split(" грн")[0])


def payment_of_one(model, months):
    """Щомісячний платіж за однією моделлю: через той самий інструмент, що й агент."""
    assert model in search_laptops(model)          # модель справді є в корпусі
    text = calc_installment(price_of(model), months, OVERPAY)   # "4400.0 грн на місяць, ..."
    return float(text.split(" грн на місяць")[0])


def compute():
    """Правильна відповідь: сума щомісячних платежів по всіх шести моделях, без моделі."""
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
