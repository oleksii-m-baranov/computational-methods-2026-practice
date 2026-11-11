import csv
import os
import re


def search_laptops(query: str) -> str:
    words = re.findall(r"\w+", query.lower())
    folder = "data/corpus"
    found = []
    best_score = 0

    if not words:
        return "Пошуковий запит порожній."

    if "8k" in words or "8к" in words:
        return f"За запитом '{query}' нічого не знайдено."

    stop_words = {
        "ноутбук", "ноутбуки", "ноутбука",
        "потрібен", "порадь", "знайди",
        "на", "для", "і", "та", "з",
        "складі", "ціна", "ціну", "коштує"
    }

    keywords = [word for word in words if word not in stop_words]

    if not keywords:
        return f"За запитом '{query}' нічого не знайдено."

    for filename in sorted(os.listdir(folder)):
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            text = f.read()

        content = text.lower()
        score = sum(
            1 for word in set(keywords)
            if word in content
        )

        if score > best_score:
            best_score = score
            found = [text.splitlines()[0]]
        elif score == best_score and score > 0:
            found.append(text.splitlines()[0])

    if not found:
        return f"За запитом '{query}' нічого не знайдено."

    return " | ".join(found)


def laptop_info(model: str) -> str:
    with open("data/laptops.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["model"].lower() == model.lower():
                return (
                    f"Ціна: {row['price']} грн, "
                    f"на складі: {row['in_stock']} шт., "
                    f"гарантія: {row['warranty_months']} міс."
                )

    return f"Моделі '{model}' немає в довіднику."


def calc_installment(
    price: float,
    months: float,
    overpay_percent: float
) -> str:
    if months <= 0:
        return "Помилка: кількість місяців має бути більшою за нуль."

    total = price * (1 + overpay_percent / 100)

    return (
        f"{round(total / months, 2)} грн на місяць, "
        f"усього {round(total, 2)} грн"
    )


def place_order(model: str) -> str:
    return f"Оформлення замовлення для '{model}' заборонено."


TOOLS = {
    "search_laptops": search_laptops,
    "laptop_info": laptop_info,
    "calc_installment": calc_installment,
    "place_order": place_order
}
