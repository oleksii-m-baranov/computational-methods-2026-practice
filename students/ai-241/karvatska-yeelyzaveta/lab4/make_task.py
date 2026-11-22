import json

from tools import search_recipes, product_info, scale_amount


PRODUCTS = [
    {"query": "рис", "name": "рис", "weight": 300},
    {"query": "куряче філе", "name": "куряче філе", "weight": 500},
    {"query": "твердий сир", "name": "твердий сир", "weight": 150},
    {"query": "вівсяні пластівці", "name": "вівсяні пластівці", "weight": 100},
    {"query": "макарони", "name": "макарони", "weight": 200},
    {"query": "помідори", "name": "помідори", "weight": 250},
]


def calculate_expected():
    """Обчислює правильну відповідь за допомогою локальних інструментів."""

    total = 0.0

    for item in PRODUCTS:
        recipe = search_recipes(item["query"])

        if "нічого не знайдено" in recipe.lower():
            raise ValueError(
                f"Не знайдено рецепт для продукту {item['name']}"
            )

        info = product_info(item["name"])

        if "немає в довіднику" in info.lower():
            raise ValueError(
                f"Немає калорійності для продукту {item['name']}"
            )

        kcal = float(
            info.split("Калорійність: ", 1)[1].split(" ккал", 1)[0]
        )

        portion_kcal = float(
            scale_amount(
                amount=kcal,
                base_servings=100,
                target_servings=item["weight"],
            )
        )

        total += portion_kcal

    total = round(total, 1)

    if total.is_integer():
        return str(int(total))

    return str(total)


def main():
    products_text = "\n".join(
        f"- {item['name']}: порція {item['weight']} г"
        for item in PRODUCTS
    )

    question = f"""
Підготуй детальний розрахунок загальної калорійності шести продуктів.

Для кожного продукту обов'язково виконай три виклики інструментів:
1. Використай search_recipes, щоб знайти рецепт із цим продуктом.
2. Використай product_info, щоб отримати калорійність продукту на 100 г.
3. Використай scale_amount, щоб розрахувати калорійність заданої порції.
   Для цього передай калорійність на 100 г як amount,
   100 як base_servings і масу порції в грамах як target_servings.

Список продуктів і маса кожної порції:
{products_text}

Не пропускай жодного продукту.
Не вигадуй калорійність і не обчислюй її без інструментів.
Виконай усі три виклики для кожного продукту окремо.
Після цього підсумуй калорійність усіх шести порцій.
У відповіді наведи назви продуктів, результати розрахунків
і загальну калорійність у ккал.
Відповідай українською мовою.
""".strip()

    expected = calculate_expected()

    task = {
	"id": "L1",
        "question": question,
        "expected": expected,
        "min_calls": len(PRODUCTS) * 3,
    }

    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)

    print("Довге завдання створено: long_task.json")
    print(f"Кількість продуктів: {len(PRODUCTS)}")
    print(f"Мінімальна кількість викликів: {task['min_calls']}")
    print(f"Очікувана загальна калорійність: {expected} ккал")


if __name__ == "__main__":
    main()