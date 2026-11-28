"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів (Варіант 4)."""
import json

from tools import calc_calories, schedule_info, search_exercises

# Шість позицій: (заняття з розкладу, запит для корпусу вправ, тривалість у хв, вага в кг, MET)
ITEMS = [
    ("йога", "спина", 45, 70, 3),
    ("кардіо", "ноги", 30, 65, 8),
    ("пілатес", "прес", 50, 60, 4),
    ("розтяжка", "руки", 40, 75, 2.5),
    ("силове", "груди", 60, 80, 6),
    ("кардіо", "початковий", 35, 70, 7),
]

QUESTION = (
    "Для кожної з шести позицій: "
    "1) йога (вправа для групи 'спина', 45 хв, вага 70 кг, MET 3); "
    "2) кардіо (вправа для групи 'ноги', 30 хв, вага 65 кг, MET 8); "
    "3) пілатес (вправа для групи 'прес', 50 хв, вага 60 кг, MET 4); "
    "4) розтяжка (вправа для групи 'руки', 40 хв, вага 75 кг, MET 2.5); "
    "5) силове (вправа для групи 'груди', 60 хв, вага 80 кг, MET 6); "
    "6) кардіо (вправа рівня 'початковий', 35 хв, вага 70 кг, MET 7). "
    "Для кожної позиції: (а) знайди в корпусі вправ відповідну вправу за вказаним запитом і наведи одним реченням; "
    "(б) знайди в розкладі день, час і тренера заняття; "
    "(в) порахуй витрату калорій за заняття інструментом calc_calories. "
    "У кінці назви сумарну витрату калорій за всі шість занять одним числом."
)

MIN_CALLS = 18


def calories_of_one(activity, query, minutes, weight_kg, met):
    """Перевіряє корпус і розклад та обчислює витрату калорій за одне заняття."""
    ex = search_exercises(query)
    assert "нічого не знайдено" not in ex, f"Не знайдено вправ за запитом: {query}"
    sched = schedule_info(activity)
    assert "немає в розкладі" not in sched, f"Не знайдено заняття в розкладі: {activity}"
    raw = calc_calories(minutes, weight_kg, met)   # повертає рядок виду '165 ккал'
    return int(raw.split()[0])


def compute():
    """Правильна відповідь: сумарна витрата калорій по всіх шести позиціях."""
    total = 0
    for activity, query, minutes, weight_kg, met in ITEMS:
        total += calories_of_one(activity, query, minutes, weight_kg, met)
    return total


def save_task(total):
    """Записує питання, правильну відповідь і MIN_CALLS у файл long_task.json."""
    task = {
        "id": "L1",
        "question": QUESTION,
        "expected": str(total),
        "min_calls": MIN_CALLS,
    }
    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


if __name__ == "__main__":
    task = save_task(compute())
    print("Правильна відповідь:", task["expected"])
    print("Файл long_task.json записано")