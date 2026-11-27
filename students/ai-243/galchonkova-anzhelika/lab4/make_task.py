"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів."""
import json
import re

from tools import search_plants, fertilizer_info, calc_dose

ITEMS = [
    ("Фікус Бенджаміна", 2.0),
    ("Фікус Лірата", 3.0),
    ("Заміокулькас", 4.0),
    ("Монстера Деліціоза", 5.0),
    ("Спатифілум", 2.5),
    ("Драцена Маргіната", 3.0),
]

QUESTION = (
    "Для кожної з шести рослин: Фікус Бенджаміна (горщик 2 л), Фікус Лірата (горщик 3 л), "
    "Заміокулькас (горщик 4 л), Монстера Деліціоза (горщик 5 л), Спатифілум (горщик 2.5 л), "
    "Драцена Маргіната (горщик 3 л). Для кожної: (а) знайди в корпусі режим поливу і наведи одним реченням; "
    "(б) знайди в довіднику періодичність підживлення та дозу на літр; "
    "(в) порахуй інструментом загальну дозу добрива для вказаного об'єму горщика. "
    "У кінці назви сумарну дозу добрива для всіх шести рослин у мілілітрах одним числом."
)

MIN_CALLS = 18


def dose_of_one(plant, pot_liters):
    """Обчислює дозу добрива для однієї рослини викликами інструментів."""
    _ = search_plants(plant)
    info = fertilizer_info(plant)
    m = re.search(r"Доза:\s*([0-9.]+)", info)
    dose_per_liter = float(m.group(1))
    res = calc_dose(pot_liters, dose_per_liter)
    return float(res.replace("мл", "").strip())


def compute():
    """Правильна відповідь: сумарна доза добрива по всіх шести позиціях."""
    total = 0.0
    for plant, pot_liters in ITEMS:
        total = total + dose_of_one(plant, pot_liters)
    return total


def save_task(total):
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
