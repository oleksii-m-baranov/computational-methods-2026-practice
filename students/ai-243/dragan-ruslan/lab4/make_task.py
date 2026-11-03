"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py

Варіант 9 (Вибір ноутбука).
"""
import json

from tools import calc_installment, get_laptop_price

# Шість позицій: пара (модель ноутбука, кількість місяців розстрочки) при переплаті 10%.
ITEMS = [
    ("StudyBook 14", 10),
    ("DevForge 15", 10),
    ("PixelArtisan 16", 10),
    ("VortexBlade 17", 20),
    ("DeskMaster 15", 11),
    ("WorkStation Lite 14", 10),
]

OVERPAY_PERCENT = 10

# Питання для агента. У ньому є перелік усіх шести позицій.
QUESTION = (
    "Для кожної з шести моделей ноутбуків: "
    "StudyBook 14 (розстрочка 10 міс.), DevForge 15 (розстрочка 10 міс.), "
    "PixelArtisan 16 (розстрочка 10 міс.), VortexBlade 17 (розстрочка 20 міс.), "
    "DeskMaster 15 (розстрочка 11 міс.), WorkStation Lite 14 (розстрочка 10 міс.). "
    "Для кожної моделі виконай по черзі: "
    "(а) знайди в корпусі через search_laptops, що про неї сказано, і наведи одним реченням; "
    "(б) знайди в довіднику через laptop_info ціну моделі; "
    "(в) порахуй через calc_installment щомісячний платіж при розстрочці на задану кількість місяців з переплатою 10% (використовуй лише точну ціну з laptop_info). "
    "У кінці назви загальну суму щомісячних платежів для усіх шести ноутбуків одним числом."
)

# Мінімум викликів інструментів для повного розв'язання: шість позицій по три інструменти.
MIN_CALLS = 18


def payment_of_one(model, months):
    """Щомісячний платіж при розстрочці для однієї моделі."""
    price = get_laptop_price(model)
    res = calc_installment(price, months, OVERPAY_PERCENT)
    return float(res.split()[0])


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
        "expected": format(round(total, 2), "g"),
        "min_calls": MIN_CALLS,
    }
    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


if __name__ == "__main__":
    task = save_task(compute())
    print("Правильна відповідь:", task["expected"])
    print("Файл long_task.json записано")
