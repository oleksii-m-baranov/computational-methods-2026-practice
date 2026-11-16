"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py

Варіант 1 (Бібліотека). Шість позицій - шість книжок з довідника.
Для кожної: знайти анотацію в корпусі, дізнатися термін видачі в довіднику,
порахувати штраф за три дні затримки (штраф за день, помножений на 3).
"""
import csv
import json

# Беремо власну функцію-інструмент з tools.py.
from tools import calculate

# Шість книжок з довідника (усі присутні в data/books.csv).
ITEMS = [
    "Основи алгоритмів",
    "Таємний острів драконів",
    "Таємний острів привидів",
    "Кулінарія для лінивих",
    "Хроніки Великого Степу",
    "Місто вічної ночі",
]

# Питання для агента. У ньому має бути перелік усіх шести позицій.
QUESTION = (
    "Для кожної з шести книжок: Основи алгоритмів, Таємний острів драконів, "
    "Таємний острів привидів, Кулінарія для лінивих, Хроніки Великого Степу, "
    "Місто вічної ночі. Для кожної: (а) знайди в корпусі анотацію і наведи "
    "одним реченням, що в ній сказано; (б) знайди в довіднику термін видачі "
    "в днях; (в) порахуй штраф за три дні затримки — штраф за день з "
    "довідника, помножений на 3. У кінці назви загальний штраф за всі шість "
    "книжок одним числом."
)

# Мінімум викликів інструментів для повного розв'язання: шість позицій по три інструменти.
MIN_CALLS = 18


def fine_per_day(title):
    """Штраф за день прострочення з довідника data/books.csv."""
    with open("data/books.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["title"] == title:
                return float(row["fine_per_day"])
    raise KeyError(title)


def cost_of_one(title):
    """Штраф за три дні затримки для однієї книжки: fine_per_day * 3."""
    fine = fine_per_day(title)
    return float(calculate("mul", fine, 3))   # множення через калькулятор


def compute():
    """Правильна відповідь: сума по всіх шести позиціях. Рахуємо самі, без моделі."""
    total = 0.0
    for title in ITEMS:
        total = total + cost_of_one(title)
    return total


def save_task(total):
    """Записує питання, правильну відповідь і MIN_CALLS у файл long_task.json."""
    task = {
        "id": "L1",
        "question": QUESTION,
        "expected": format(round(total, 2), "g"),   # число як текст, без зайвих нулів
        "min_calls": MIN_CALLS,
    }
    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


if __name__ == "__main__":
    task = save_task(compute())
    print("Правильна відповідь:", task["expected"])
    print("Файл long_task.json записано")
