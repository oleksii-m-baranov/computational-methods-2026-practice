import json
import re

from tools import search_plants, fertilizer_info, calc_dose


ITEMS = [
    ("Фіалка зоряна", 1.0),
    ("Драцена смарагдова", 1.5),
    ("Пальма місячна", 2.0),
    ("Фікус сріблястий", 2.5),
    ("Маранта смугаста", 3.0),
    ("Азалія рожева", 4.0),
]


QUESTION = (
    "Для кожної з шести рослин: Фіалка зоряна (1.0 л), "
    "Драцена смарагдова (1.5 л), Пальма місячна (2.0 л), "
    "Фікус сріблястий (2.5 л), Маранта смугаста (3.0 л), "
    "Азалія рожева (4.0 л). "
    "Для кожної рослини: "
    "(а) знайди інформацію про неї в корпусі та наведи одним реченням; "
    "(б) знайди в довіднику періодичність підживлення; "
    "(в) розрахуй дозу добрива для вказаного об'єму горщика. "
    "У кінці назви сумарну дозу добрива для всіх шести рослин одним числом."
)


MIN_CALLS = 18


def dose_of_one(plant, pot_liters):
    """Обчислює дозу добрива для однієї рослини."""
    found = search_plants(plant)
    if plant.lower() not in found.lower():
        raise ValueError(f"Рослину не знайдено в корпусі: {plant}")

    info = fertilizer_info(plant)

    match = re.search(r"Доза:\s*([\d.,]+)\s*мл", info)
    if not match:
        raise ValueError(f"Не знайдено дозу для рослини: {plant}")

    dose_per_liter = float(match.group(1).replace(",", "."))
    result = calc_dose(pot_liters, dose_per_liter)

    return float(result.replace("мл", "").strip().replace(",", "."))


def compute():
    """Рахує правильну сумарну дозу без використання моделі."""
    total = 0.0

    for plant, pot_liters in ITEMS:
        total += dose_of_one(plant, pot_liters)

    return total


def save_task(total):
    """Записує завдання та правильну відповідь у long_task.json."""
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
