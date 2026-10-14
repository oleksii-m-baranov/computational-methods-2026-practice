"""Інструменти агента. Варіант 9 — Вибір ноутбука."""
import csv
import os


def search_laptops(query: str) -> str:
    """Шукає ноутбуки в корпусі за ключовим словом."""
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


def laptop_info(model: str) -> str:
    """Шукає модель у довіднику та повертає ціну, наявність і гарантію."""
    with open("data/laptops.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["model"].lower() == model.lower():
                return (f"Ціна: {row['price']} грн, "
                        f"на складі: {row['in_stock']} шт., "
                        f"гарантія: {row['warranty_months']} міс.")
    return f"Моделі '{model}' немає в довіднику."


def calc_installment(price: float, months: float,
                     overpay_percent: float) -> str:
    """Обчислює щомісячний платіж при розстрочці."""
    if months <= 0:
        return "Помилка: кількість місяців має бути більшою за нуль."
    total = price * (1 + overpay_percent / 100)
    return (f"{round(total / months, 2)} грн на місяць, "
            f"усього {round(total, 2)} грн")


TOOLS = {
    "search_laptops": search_laptops,
    "laptop_info": laptop_info,
    "calc_installment": calc_installment,
}
