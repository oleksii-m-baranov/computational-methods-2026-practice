"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py

Варіант 2 (Кулінарія): шість продуктів, для кожного — калорійність порції.
"""
import json

# Беремо власні функції-інструменти з tools.py
from tools import product_info, scale_amount

# Шість продуктів і їхня вага порції в грамах
ITEMS = [
    ("рис", 200),
    ("курка", 150),
    ("морква", 100),
    ("сир", 50),
    ("шоколад", 30),
    ("картопля", 250),
]

# Питання для агента
QUESTION = (
    "Для кожного з шести продуктів: рис 200 г, курка 150 г, морква 100 г, "
    "сир 50 г, шоколад 30 г, картопля 250 г. Для кожного: "
    "(а) знайди в корпусі рецепт, де використовується цей продукт, і наведи його назву одним реченням; "
    "(б) знайди в довіднику калорійність цього продукту на 100 г; "
    "(в) порахуй калорійність порції заданої ваги (калорійність на 100 г × вага / 100). "
    "У кінці назви сумарну калорійність усіх шести порцій одним числом."
)

# Мінімум викликів інструментів: 6 позицій × 3 інструменти = 18
MIN_CALLS = 18


def calories_of_one(product, grams):
    """Калорійність порції: калорійність на 100 г × вага / 100."""
    # Отримуємо рядок "Калорійність: 344 ккал на 100 г, ціна: 45 грн/кг"
    info = product_info(product)
    # Витягуємо число калорійності
    import re
    match = re.search(r"Калорійність:\s*(\d+)\s*ккал", info)
    if not match:
        raise ValueError(f"Не вдалося отримати калорійність для '{product}': {info}")
    kcal_per_100g = float(match.group(1))
    # Рахуємо калорійність порції
    return kcal_per_100g * grams / 100


def compute():
    """Правильна відповідь: сума калорійності всіх шести порцій."""
    total = 0.0
    for product, grams in ITEMS:
        total += calories_of_one(product, grams)
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
    print("Правильна відповідь:", task["expected"])
    print("Файл long_task.json записано")