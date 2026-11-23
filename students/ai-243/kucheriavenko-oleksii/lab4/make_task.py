"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів."""
import json
import re

from tools import calc_dose, fertilizer_info, search_plants

ITEMS = [
    ("Фікус Бенджаміна", 2.0),
    ("Фікус Лірата", 1.5),
    ("Сансевієрія трисмугова", 3.0),
    ("Монстера делікатесна", 2.0),
    ("Спатифілум Уолліса", 2.5),
    ("Алое вера", 1.0),
]

QUESTION = (
    "Для кожної з шести рослин: Фікус Бенджаміна (горщик 2.0 л), Фікус Лірата (горщик 1.5 л), "
    "Сансевієрія трисмугова (горщик 3.0 л), Монстера делікатесна (горщик 2.0 л), "
    "Спатифілум Уолліса (горщик 2.5 л), Алое вера (горщик 1.0 л). "
    "Для кожної: (а) знайди в корпусі опис догляду за рослиною і наведи одним реченням; "
    "(б) знайди в довіднику дозу добрива на літр; "
    "(в) порахуй дозу добрива для вказаного об'єму горщика. "
    "У кінці назви сумарну дозу добрива для всіх шести рослин одним числом."
)

MIN_CALLS = 18


def dose_of_one(plant, pot_liters):
    _ = search_plants(plant)
    info = fertilizer_info(plant)
    m = re.search(r"Доза:\s*([0-9.]+)", info)
    dose_per_liter = float(m.group(1))
    res = calc_dose(pot_liters, dose_per_liter)
    return float(res.replace(" мл", ""))


def compute():
    total = 0.0
    for plant, pot in ITEMS:
        total += dose_of_one(plant, pot)
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