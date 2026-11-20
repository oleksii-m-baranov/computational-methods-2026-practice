"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py

Варіант 4 (тренування): шість занять із розкладу. Для кожного заняття
пошук у корпусі за ключовим словом, тривалість із розкладу і витрата калорій.
"""
import json
import re

from tools import schedule_info, calc_calories

WEIGHT = 70   # вага людини, кг

# Шість позицій: (заняття, ключове слово для пошуку в корпусі, MET заняття)
ITEMS = [("кардіо", "ноги", 7.0), ("йога", "спина", 2.5), ("силове", "груди", 5.0),
         ("пілатес", "прес", 3.0), ("розтяжка", "руки", 2.3), ("кросфіт", "просунутий", 8.0)]

# Питання за шаблоном методички: перелік шести занять, (а) пошук у корпусі,
# (б) тривалість у довіднику розкладу, (в) витрата калорій, підсумок одним числом.
QUESTION = (
    "Для кожного з шести занять (вага людини 70 кг): "
    "кардіо (пошук у корпусі за словом «ноги», MET 7.0), "
    "йога (за словом «спина», MET 2.5), "
    "силове (за словом «груди», MET 5.0), "
    "пілатес (за словом «прес», MET 3.0), "
    "розтяжка (за словом «руки», MET 2.3), "
    "кросфіт (за словом «просунутий», MET 8.0). "
    "Для кожного: (а) знайди в корпусі вправи за вказаним словом і наведи одним реченням; "
    "(б) знайди в довіднику розкладу тривалість заняття; "
    "(в) порахуй витрату калорій за заняття. "
    "У кінці назви сумарну витрату калорій за всі шість занять одним числом."
)

# Мінімум викликів інструментів: шість позицій по три інструменти.
MIN_CALLS = 18


def minutes_of(activity):
    """Тривалість заняття з розкладу: беремо число з відповіді schedule_info."""
    info = schedule_info(activity)
    return float(re.search(r"тривалість: (\d+)", info).group(1))


def calories_of_one(activity, met):
    """Витрата калорій за одне заняття: рахуємо тим самим інструментом, що й агент."""
    answer = calc_calories(minutes_of(activity), WEIGHT, met)
    return int(answer.split()[0])


def compute():
    """Правильна відповідь: сума по всіх шести заняттях. Рахуємо самі, без моделі."""
    total = 0
    for activity, word, met in ITEMS:
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


for activity, word, met in ITEMS:
    print(f"{activity}: {minutes_of(activity):g} хв, MET {met}, "
          f"{calories_of_one(activity, met)} ккал")
task = save_task(compute())
print("Правильна відповідь:", task["expected"])
print("Файл long_task.json записано")
