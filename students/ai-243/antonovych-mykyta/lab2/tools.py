import csv
import os


def search_recipes(query: str) -> str:
    q = query.lower()
    found = []
    folder = "data/corpus"
    for filename in sorted(os.listdir(folder)):
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            text = f.read()
        if q in text.lower():
            found.append(text.split("\n")[0])
    if not found:
        return f"За запитом '{query}' нічого не знайдено."
    return " | ".join(found)


def product_info(product: str) -> str:
    with open("data/products.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["product"].lower() == product.lower():
                return (f"Калорійність: {row['kcal_per_100g']} ккал "
                        f"на 100 г, ціна: {row['price_per_kg']} грн/кг")
    return f"Продукту '{product}' немає в довіднику."


def scale_amount(amount: float, base_servings: float,
                 target_servings: float) -> str:
    if base_servings <= 0:
        return "Помилка: кількість порцій має бути більшою за нуль."
    return str(round(amount * target_servings / base_servings, 1))


TOOLS = {
    "search_recipes": search_recipes,
    "product_info": product_info,
    "scale_amount": scale_amount,
}
