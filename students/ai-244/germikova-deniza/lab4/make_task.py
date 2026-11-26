"""ЛР4, варіант 2. Генерація довгої задачі для кулінарного агента."""

import csv
import json
import re
from decimal import Decimal
from pathlib import Path

from tools import search_recipes, product_info, scale_amount

# Маса порції кожного продукту у грамах
WEIGHTS = {
    "рис": 150,
    "куряче філе": 180,
    "морква": 120,
    "картопля": 200,
    "помідори": 160,
    "вівсяні пластівці": 90,
    "яблука": 140,
    "гарбуз": 220,
    "яйця": 120,
    "макарони": 180,
    "цибуля": 80,
    "олія": 20,
    "молоко": 250,
    "йогурт": 180,
    "борошно": 100,
    "вершки": 120,
    "масло": 30,
    "цукор": 25,
    "огірки": 180,
}

MIN_CALLS = 18
items = []

with open("data/products.csv", encoding="utf-8", newline="") as f:
    catalog = {
        row["product"].strip(): row
        for row in csv.DictReader(f)
    }

# Обираємо лише продукти, які реально є в рецептах і довіднику
for product, grams in WEIGHTS.items():
    if product not in catalog:
        continue

    recipes = search_recipes(product)

    if "нічого не знайдено" in recipes.lower():
        continue

    info = product_info(product)
    match = re.search(
        r"Калорійність:\s*([\d.,]+)\s*ккал",
        info
    )

    if not match:
        continue

    kcal_100 = float(match.group(1).replace(",", "."))

    if kcal_100 <= 0:
        continue

    # Перерахунок калорійності зі 100 г на задану масу
    kcal_portion = Decimal(
        scale_amount(kcal_100, 100, grams)
    )

    items.append(
        (product, grams, recipes, kcal_100, kcal_portion)
    )

    if len(items) == 6:
        break

if len(items) != 6:
    raise SystemExit(
        f"ПОМИЛКА: у рецептах знайдено лише {len(items)} "
        "відповідних продуктів. Потрібно перевірити дані."
    )

positions = "; ".join(
    f"{product} — {grams} г"
    for product, grams, *_ in items
)

QUESTION = (
    f"Для кожного з шести продуктів ({positions}) "
    "виконай три окремі дії: "
    "(а) через search_recipes знайди рецепт із цим "
    "продуктом і назви його; "
    "(б) через product_info знайди калорійність "
    "цього продукту на 100 г; "
    "(в) через scale_amount обчисли калорійність "
    "зазначеної порції: amount = ккал на 100 г, "
    "base_servings = 100, "
    "target_servings = маса порції в грамах. "
    "Для кожного продукту наведи результат у ккал. "
    "У кінці назви сумарну калорійність усіх "
    "шести порцій одним числом у ккал. "
    "Не вигадуй дані — використовуй інструменти "
    "для кожної позиції."
)

total = sum(
    (item[4] for item in items),
    Decimal("0")
)

task = {
    "id": "L1",
    "question": QUESTION,
    "expected": format(total.normalize(), "f"),
    "min_calls": MIN_CALLS,
}

output = Path("long_task.json")

if output.exists():
    previous = json.loads(output.read_text(encoding="utf-8"))
    if previous != task:
        raise SystemExit(
            "УВАГА: long_task.json уже існує з іншими "
            "даними. Не перезаписуємо правильну відповідь."
        )
    print("long_task.json вже існує, без змін")
else:
    output.write_text(
        json.dumps(task, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print("УСПІХ: long_task.json створено!")

print("\n=== ШІСТЬ ПРОДУКТІВ ===")
for i, (product, grams, recipes, kcal_100, portion) in enumerate(items, 1):
    print(
        f"{i}. {product}: {grams} г, "
        f"{kcal_100} ккал/100 г -> {portion} ккал"
    )
    print(f"   Рецепти: {recipes}")

print("\nПРАВИЛЬНА ВІДПОВІДЬ:", task["expected"])
print("МІНІМУМ ВИКЛИКІВ:", task["min_calls"])
