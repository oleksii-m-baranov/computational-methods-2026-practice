"""Creates long_task.json: question, expected answer, and minimum tool calls.
Variant 11 (Library).
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import json
import csv
from tools import calculate


# Six books for Variant 11 (Library)
ITEMS = [
    "Основи алгоритмів",
    "Зоряний експрес",
    "Місто вічної ночі",
    "Кулінарія для лінивих",
    "Хроніки Марсіанської бази",
    "Чистий код у Python",
]

QUESTION = (
    "Для кожної з шести книжок: Основи алгоритмів, Зоряний експрес, Місто вічної ночі, "
    "Кулінарія для лінивих, Хроніки Марсіанської бази, Чистий код у Python. "
    "Для кожної: (а) знайди в корпусі, про що книжка, і наведи одним реченням; "
    "(б) знайди в довіднику термін видачі та штраф за день; "
    "(в) порахуй розмір штрафу за 3 дні затримки. "
    "У кінці назви загальну суму штрафу для усіх шести книжок одним числом."
)

MIN_CALLS = 18


def get_fine_per_day(book_title: str) -> float:
    """Read fine_per_day from data/books.csv."""
    with open("data/books.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["title"].strip().lower() == book_title.strip().lower():
                return float(row["fine_per_day"])
    return 0.0


def cost_of_one(book_title: str) -> float:
    """Calculate fine for 3 days of delay using calculate tool."""
    fine_rate = get_fine_per_day(book_title)
    res = calculate("mul", 3, fine_rate)
    return float(res)


def compute() -> float:
    """Compute exact total fine across all 6 books without LLM."""
    total = 0.0
    for book in ITEMS:
        total += cost_of_one(book)
    return total


def save_task(total: float):
    """Save long_task.json with question, expected, and min_calls."""
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
