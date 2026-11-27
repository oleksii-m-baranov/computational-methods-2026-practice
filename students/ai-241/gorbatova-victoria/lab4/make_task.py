"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів (Варіант 7)."""
import json
import csv
from tools import transport_info, calc_budget

ITEMS = [
    ("Кам'янець-Подільський", 4),
    ("Яремче", 2),
    ("Львів Гастрономічний", 3),
    ("Одеса", 5),
    ("Чернівці", 2),
    ("Синевир", 4)
]

QUESTION = (
    "Розрахуй загальний бюджет для шести поїздок для груп різної чисельності: "
    "1) Кам'янець-Подільський для 4 людей; "
    "2) Яремче для 2 людей; "
    "3) Львів Гастрономічний для 3 людей; "
    "4) Одеса для 5 людей; "
    "5) Чернівці для 2 людей; "
    "6) Синевир для 4 людей. "
    "Для кожної поїздки: (а) знайди в довіднику вартість проїзду на одну особу через transport_info; "
    "(б) порахуй бюджет поїздки для групи через calc_budget (додаткові витрати extra = 0). "
    "У кінці назви загальну суму бюджету всіх шести поїздок одним числом."
)

MIN_CALLS = 12


def get_price(route_name):
    with open("data/transport.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["route"].lower() == route_name.lower():
                return float(row["price"])
    return 0.0


def compute():
    total = 0.0
    for route, people in ITEMS:
        price = get_price(route)
        # Викликаємо calc_budget замість calculate_trip
        res_str = calc_budget(price, people, 0)
        import re
        nums = re.findall(r"[\d\.]+", res_str)
        if nums:
            total += float(nums[0])
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