"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py
"""
import json
import re

from tools import calc_calories, schedule_info, search_exercises

ITEMS = [
    ("йога", 60),
    ("пілатес", 50),
    ("силове", 60),
    ("розтяжка", 45),
    ("кардіо", 45),
    ("стретчинг", 45),
]

WEIGHT_KG = 70
MET = 5

QUESTION = (
    "Для кожної з шести занять: йога (60 хв), пілатес (50 хв), силове (60 хв), "
    "розтяжка (45 хв), кардіо (45 хв), стретчинг (45 хв). "
    "Для кожної: (а) знайди в корпусі вправи за назвою/темою заняття та наведи одним реченням; "
    "(б) знайди в розкладі день, час і тренера заняття; "
    "(в) порахуй витрату калорій за тривалістю заняття (вага 70 кг, MET 5). "
    "У кінці назви сумарну витрату калорій усіх шести занять одним числом."
)

MIN_CALLS = 18


def parse_kcal(result_text: str) -> float:
    """Дістає число калорій з рядка виду '368 ккал'."""
    match = re.search(r"[-+]?\d+(?:[.,]\d+)?", result_text.replace(",", "."))
    if not match:
        raise ValueError(f"Не вдалося витягти калорії з рядка: {result_text!r}")
    return float(match.group(0))


def kcal_of_one(activity: str, minutes: int) -> float:
    """Виконує 3 інструменти для одного заняття й повертає витрату калорій."""
    search_exercises(activity)
    schedule_info(activity)
    res = calc_calories(minutes=minutes, weight_kg=WEIGHT_KG, met=MET)
    return parse_kcal(res)


def compute() -> float:
    """Правильна відповідь: сума витрат калорій по всіх шести заняттях."""
    total = 0.0
    for activity, minutes in ITEMS:
        total += kcal_of_one(activity, minutes)
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
