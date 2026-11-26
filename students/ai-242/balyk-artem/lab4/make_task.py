import json
import re

# Беремо власні функції-інструменти з tools.py.
from tools import search_recipes, product_info, scale_amount

# Шість позицій. У варіанті 2 кожна позиція - продукт із рецепта та вага порції в грамах.
ITEMS = [
    ("рис", 150),
    ("куряче філе", 200),
    ("морква", 80),
    ("цибуля", 50),
    ("картопля", 200),
    ("яблуко", 120)
]

# Питання для агента. У ньому має бути перелік усіх шести позицій.
QUESTION = (
    "Для кожного з шести продуктів: рис 150 г, куряче філе 200 г, морква 80 г, цибуля 50 г, "
    "картопля 200 г, яблуко 120 г. Для кожного: (а) знайди в корпусі рецепти, у яких використовується "
    "цей продукт, і наведи знайдені назви одним реченням; (б) знайди в довіднику калорійність продукту "
    "на 100 г; (в) порахуй калорійність порції заданої ваги. "
    "У кінці назви сумарну калорійність усіх шести порцій одним числом."
)

# Мінімум викликів інструментів для повного розв'язання: шість позицій по три інструменти.
MIN_CALLS = 18


def calories_of_one(product, weight):
    """Калорійність однієї порції: вага, помножена на калорійність продукту на 100 г і поділена на 100."""
    info = product_info(product)                       # калорійність з довідника
    match = re.search(r"Калорійність:\s*(\d+(?:[.,]\d+)?)", info)
    if not match:
        raise ValueError(f"Не вдалося отримати калорійність продукту: {product}")
    calories = float(match.group(1).replace(",", "."))
    return float(scale_amount(calories, 100, weight))  # обчислення калорійності порції


def compute():
    """Правильна відповідь: сума по всіх шести позиціях. Рахуємо самі, без моделі."""
    total = 0.0
    for product, weight in ITEMS:
        recipes = search_recipes(product)              # пошук рецептів у корпусі
        if "нічого не знайдено" in recipes.lower():
            raise ValueError(f"Для продукту '{product}' не знайдено рецептів.")
        total = total + calories_of_one(product, weight)
    return total


def save_task(total):
    """Записує питання, правильну відповідь і MIN_CALLS у файл long_task.json."""
    task = {
        "id": "L1",
        "question": QUESTION,
        "expected": format(round(total, 2), "g"),   # число як текст, без зайвих нулів: 142.5
        "min_calls": MIN_CALLS,
    }
    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


task = save_task(compute())
print("Правильна відповідь:", task["expected"])
print("Файл long_task.json записано")
