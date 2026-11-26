"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск: python make_task.py
"""
import json
import re

from tools import calc_dose, fertilizer_info, search_plants

# Шість позицій для варіанта 5: пара (назва рослини, об'єм горщика в літрах)
ITEMS = [
    ("Фікус Бенджаміна", 2.0),
    ("Монстера Деліціоза", 4.0),
    ("Спатифілум", 1.5),
    ("Заміокулькас", 3.0),
    ("Антуріум Андре", 2.5),
    ("Орхідея Фаленопсис", 1.0),
]

QUESTION = (
    "Для кожної з шести рослин: Фікус Бенджаміна (горщик 2.0 л), "
    "Монстера Деліціоза (горщик 4.0 л), Спатифілум (горщик 1.5 л), "
    "Заміокулькас (горщик 3.0 л), Антуріум Андре (горщик 2.5 л), "
    "Орхідея Фаленопсис (горщик 1.0 л). Для кожної: "
    "(а) знайди в базі знань інформацію про рослину та наведи одним реченням; "
    "(б) знайди в довіднику періодичність підживлення та дозу добрива на літр; "
    "(в) порахуй потрібну дозу добрива для вказаного об'єму горщика. "
    "У кінці назви сумарну дозу добрива для всіх шести рослин одним числом."
)

# Мінімум викликів інструментів для повного розв'язання: 6 рослин * 3 інструменти = 18
MIN_CALLS = 18


def dose_of_one(plant: str, pot_liters: float) -> float:
    """Рахує дозу добрива для однієї рослини прямими викликами інструментів."""
    _ = search_plants(plant)
    info = fertilizer_info(plant)
    match = re.search(r"Доза:\s*(\d+(?:\.\d+)?)", info)
    if not match:
        raise ValueError(f"Не вдалося витягнути дозу з рядка: {info}")
    dose_per_liter = float(match.group(1))
    dose_str = calc_dose(pot_liters, dose_per_liter)
    return float(dose_str.split()[0])


def compute() -> float:
    """Правильна відповідь: сума доз по всіх шести рослинах."""
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