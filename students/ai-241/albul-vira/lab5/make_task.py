"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск: python make_task.py
"""
import csv
import json
import re

from tools import book_info, calculate

# Беремо перші 6 книжок із довідника data/books.csv
with open("data/books.csv", encoding="utf-8-sig") as f:
    ITEMS = [row["title"] for row in list(csv.DictReader(f))[:6]]

if len(ITEMS) < 6:
    raise RuntimeError(f"У data/books.csv знайдено лише {len(ITEMS)} книжок, потрібно мінімум 6!")

books_list = ", ".join(ITEMS)

QUESTION = (
    f"Для кожної з шести книжок: {books_list}. "
    "Виконуй завдання по черзі: викликай суворо один інструмент за один крок (не викликай кілька інструментів одночасно). "
    "Для кожної книжки: (а) знайди в корпусі бібліотеки згадку про книжку за одним ключовим словом у search_books і наведи одним реченням; "
    "(б) знайди в довіднику через book_info термін видачі в днях та штраф за день прострочення; "
    "(в) порахуй через calculate штраф за три дні затримки (множення штрафу за день на 3). "
    "У кінці порахуй через calculate загальний штраф за всі шість книжок і назви його одним числом."
)

MIN_CALLS = 18


def cost_of_one(title):
    """Штраф за 3 дні затримки однієї книжки: штраф за день * 3."""
    info = book_info(title)
    match = re.search(r"штраф:\s*([0-9]+(?:[.,][0-9]+)?)", info)
    if not match:
        raise ValueError(f"Не вдалося знайти штраф у відповіді book_info для '{title}': {info}")
    fine_per_day = float(match.group(1).replace(",", "."))
    return float(calculate("mul", fine_per_day, 3))


def compute():
    """Правильна відповідь: сума штрафів по всіх шести книжках. Рахуємо самі, без моделі."""
    total = 0.0
    for title in ITEMS:
        total += cost_of_one(title)
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
    task = save_task(compute())
    print("Книжки:", ITEMS)
    print("Питання:", task["question"])
    print("Правильна відповідь:", task["expected"])
    print("Файл long_task.json записано")