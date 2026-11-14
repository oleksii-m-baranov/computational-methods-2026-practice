"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.
Запуск:  python make_task.py
Варіант 5: догляд за кімнатними рослинами.
"""

import json
import re
from tools import search_plants, fertilizer_info, calc_dose

ITEMS = [
    ("Фікус", 3.0),
    ("Заміокулькас", 2.0),
    ("Спатифілум", 1.5),
    ("Драцена", 4.0),
    ("Алое вера", 1.0),
    ("Калатея", 2.5),
]

QUESTION = (
    "Оброби по черзі кожну з 6 рослин (для КОЖНОЇ рослини виконай 3 окремі кроки: "
    "(а) search_plants для опису з корпусу одним реченням, "
    "(б) fertilizer_info для дози на літр і періодичності з довідника, "
    "(в) calc_dose для розрахунку дози на вказаний об'єм горщика):\n"
    "1. Фікус — горщик 3.0 л\n"
    "2. Заміокулькас — горщик 2.0 л\n"
    "3. Спатифілум — горщик 1.5 л\n"
    "4. Драцена — горщик 4.0 л\n"
    "5. Алое вера — горщик 1.0 л\n"
    "6. Калатея — горщик 2.5 л\n"
    "Лише після виконання всіх 18 викликів (для всіх 6 рослин включно з Калатеєю) "
    "наведи короткий підсумок по кожній рослині та в кінці назви сумарну дозу добрива "
    "в мілілітрах для всіх шести рослин одним числом."
)

MIN_CALLS = 18


def dose_of_one(plant: str, pot_liters: float) -> float:
    """Доза добрива для однієї рослини: перевіряємо корпус, довідник і рахуємо через calc_dose."""
    _ = search_plants(plant)
    info = fertilizer_info(plant)
    match = re.search(r"Доза:\s*([0-9.]+)", info)
    dose_per_liter = float(match.group(1))
    calc_res = calc_dose(pot_liters, dose_per_liter)
    return float(calc_res.split()[0])


def compute() -> float:
    """Правильна відповідь: сумарна доза добрива по всіх шести рослинах."""
    total = 0.0
    for plant, pot_liters in ITEMS:
        total += dose_of_one(plant, pot_liters)
    return total


def save_task(total: float) -> dict:
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