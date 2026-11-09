"""Freeze the long task and compute the answer directly from the cooking tools."""

import json
import re
from decimal import Decimal
from pathlib import Path

from tools import product_info, scale_amount, search_recipes

ITEMS = [("рис", 175), ("курка", 230), ("морква", 120), ("цибуля", 80),
         ("картопля", 250), ("молоко", 150)]

QUESTION = (
    "Підготуй таблицю калорійності для шести продуктів: "
    + ", ".join(f"{name} — {grams} г" for name, grams in ITEMS)
    + ". Для кожного продукту по черзі: (а) виклич search_recipes з його назвою "
    "та наведи одну знайдену страву; (б) виклич product_info та візьми ккал на 100 г; "
    "(в) виклич scale_amount, передавши калорійність як amount, 100 як base_servings "
    "і вагу продукту як target_servings. Збережи всі шість рядків. "
    "Не завершуй, доки не маєш результатів для всіх шести продуктів. "
    "В останньому рядку напиши суму калорій шести порцій у форматі «Разом: число ккал»."
)


def reference():
    rows = []
    for name, grams in ITEMS:
        recipes = search_recipes(name)
        if "нічого не знайдено" in recipes:
            raise ValueError(f"No recipe contains {name}")
        match = re.search(r"Калорійність: (\d+) ккал", product_info(name))
        kcal = int(match[1])
        scaled = Decimal(scale_amount(kcal, 100, grams))
        rows.append({"product": name, "grams": grams, "recipe": recipes.splitlines()[0],
                     "kcal_per_100g": kcal, "portion_kcal": str(scaled)})
    return rows


if __name__ == "__main__":
    rows = reference()
    total = sum(Decimal(row["portion_kcal"]) for row in rows)
    task = {"id": "L1", "question": QUESTION, "expected": format(total.normalize(), "f"),
            "min_calls": 3 * len(ITEMS), "reference": rows}
    Path("long_task.json").write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
    print(task["expected"])
