"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py
"""
import json
import os

from tools import calc_calories

# Шість позицій: (назва заняття, тривалість у хв, вага у кг, коефіцієнт MET)
ITEMS = [
    ("Пульсарний жим", 45.0, 70.0, 5.0),
    ("Присідання \"Сталевий маятник\"", 60.0, 70.0, 7.5),
    ("Тяга \"Кібер-лісоруб\"", 40.0, 70.0, 6.0),
    ("Скручування \"Неоновий вихор\"", 30.0, 70.0, 4.5),
    ("Пульсарний жим з розворотом", 50.0, 70.0, 8.0),
    ("Планка \"Титан\"", 20.0, 70.0, 3.5),
]

QUESTION = (
    "Для кожної з шести позицій: "
    "Пульсарний жим (45 хв, вага 70 кг, MET 5.0), "
    "Присідання \"Сталевий маятник\" (60 хв, вага 70 кг, MET 7.5), "
    "Тяга \"Кібер-лісоруб\" (40 хв, вага 70 кг, MET 6.0), "
    "Скручування \"Неоновий вихор\" (30 хв, вага 70 кг, MET 4.5), "
    "Пульсарний жим з розворотом (50 хв, вага 70 кг, MET 8.0), "
    "Планка \"Титан\" (20 хв, вага 70 кг, MET 3.5). "
    "Для кожної: "
    "(а) знайди в корпусі через search_exercises опис техніки виконання і наведи одним реченням; "
    "(б) знайди в розкладі через schedule_info день і час початку; "
    "(в) порахуй через calc_calories витрату калорій. "
    "Опрацьовуй заняття по черзі (по одному заняттю за крок, не викликай усі інструменти одночасно): "
    "У кінці назви сумарну витрату калорій для всіх занять одним числом."
)

# Мінімум викликів інструментів для повного розв'язання: шість позицій по три інструменти.
MIN_CALLS = 18


def cost_of_one(minutes, weight_kg, met):
    """Витрата калорій за одне заняття: викликаємо калькулятор калорій."""
    cal_str = calc_calories(minutes, weight_kg, met)
    return float(cal_str.replace(" ккал", "").strip())


def compute():
    """Правильна відповідь: сума по всіх шести позиціях. Рахуємо самі, без моделі."""
    total = 0.0
    for _, minutes, weight_kg, met in ITEMS:
        total += cost_of_one(minutes, weight_kg, met)
    return total


def save_task(total):
    """Записує питання, правильну відповідь і MIN_CALLS у файл long_task.json."""
    task = {
        "id": "L1",
        "question": QUESTION,
        "expected": format(round(total, 2), "g"),
        "min_calls": MIN_CALLS,
    }
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "long_task.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


if __name__ == "__main__":
    task = save_task(compute())
    print("Правильна відповідь:", task["expected"])
    print("Файл long_task.json записано успішно!")
