
import json
import re

from tools import search_recipes, product_info, scale_amount

ITEMS = [
    ("рис", 150),
    ("курка", 200),
    ("морква", 100),
    ("цибуля", 80),
    ("картопля", 250),
    ("яйце", 120),
]


QUESTION = """
Для шести продуктів розрахуй калорійність:

1. рис — 150 г
2. курка — 200 г
3. морква — 100 г
4. цибуля — 80 г
5. картопля — 250 г
6. яйце — 120 г

Для КОЖНОГО продукту обов'язково виконай:

1. search_recipes — знайди рецепти з продуктом.
2. product_info — отримай калорійність на 100 г.
3. scale_amount — розрахуй калорійність порції.

ВАЖЛИВО: scale_amount приймає:
- amount = калорійність продукту на 100 г,
  отримана саме з product_info;
- base_servings = 10;
- target_servings = вага продукту в грамах / 10.

Приклад ТІЛЬКИ для пояснення:
якщо продукт має 200 ккал на 100 г,
а порція важить 150 г, викликай:
scale_amount(
    amount=200,
    base_servings=10,
    target_servings=15
)

Не передавай вагу продукту без ділення на 10.
Не використовуй однакове amount для різних продуктів.
Не повторюй уже успішно виконані виклики.

Після отримання результатів усіх шести продуктів
вкажи сумарну калорійність у ккал.
"""


MIN_CALLS = 18


def compute():
    total = 0.0

    for product, weight in ITEMS:
        search_recipes(product)

        info = product_info(product)
        match = re.search(
            r"Калорійність:\s*([\d.,]+)",
            info
        )

        if not match:
            raise ValueError(
                f"Не знайдено калорійність: {product}: {info}"
            )

        kcal_100 = float(match.group(1).replace(",", "."))

        portion_kcal = float(
            scale_amount(
                kcal_100,
                10,
                weight // 10
            )
        )

        total += portion_kcal

    return round(total, 2)


task = {
    "id": "L1",
    "question": QUESTION,
    "expected": format(compute(), "g"),
    "min_calls": MIN_CALLS
}

with open("long_task.json", "w", encoding="utf-8") as f:
    json.dump(task, f, ensure_ascii=False, indent=2)

print("Правильна відповідь:", task["expected"])
print("Файл long_task.json створено")
