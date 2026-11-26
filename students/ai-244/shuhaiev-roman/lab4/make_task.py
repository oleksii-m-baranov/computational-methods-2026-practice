"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py

Варіант 4 (тренування): шість занять із розкладу. Для кожного:
пошук вправ у каталозі, тривалість заняття з розкладу, витрата калорій.
"""
import json

# Власні функції-інструменти з tools.py
from tools import calc_calories, find_session

WEIGHT_KG = 70

# Шість позицій: (заняття з розкладу, що шукати в каталозі вправ, коефіцієнт MET)
ITEMS = [("йога", "спина", 2.5), ("пілатес", "прес", 3),
         ("силове", "груди", 5), ("розтяжка", "ноги", 2.5),
         ("кардіо", "руки", 7), ("кросфіт", "просунутий", 8)]

# Питання для агента. У ньому є перелік усіх шести позицій.
QUESTION = (
    "Я важу 70 кг. Для кожного з шести занять: йога (MET 2.5, вправи на спину), "
    "пілатес (MET 3, вправи на прес), силове (MET 5, вправи на груди), "
    "розтяжка (MET 2.5, вправи на ноги), кардіо (MET 7, вправи на руки), "
    "кросфіт (MET 8, вправи просунутого рівня). Для кожного: (а) знайди в каталозі "
    "вказані вправи і наведи їх одним реченням; (б) знайди в розкладі тривалість заняття "
    "в хвилинах; (в) порахуй витрату калорій за заняття. "
    "У кінці назви сумарну витрату калорій за всі шість занять одним числом."
)

# Мінімум викликів інструментів для повного розв'язання: шість позицій по три інструменти.
MIN_CALLS = 18


def calories_of_one(activity, met):
    """Витрата калорій за одне заняття: тривалість з розкладу, розрахунок інструментом."""
    minutes = float(find_session(activity)["duration_min"])        # тривалість з довідника
    text = calc_calories(minutes, WEIGHT_KG, met)                   # "NNN ккал"
    return int(text.split()[0])


def compute():
    """Правильна відповідь: сума по всіх шести позиціях. Рахуємо самі, без моделі."""
    total = 0
    for activity, _, met in ITEMS:
        total = total + calories_of_one(activity, met)
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
    for activity, query, met in ITEMS:
        print(f"{activity}: {find_session(activity)['duration_min']} хв, "
              f"{calories_of_one(activity, met)} ккал")
    task = save_task(compute())
    print("Правильна відповідь:", task["expected"])
    print("Файл long_task.json записано")
