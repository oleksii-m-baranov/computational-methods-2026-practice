"""Перевірки змісту аргументів."""
import csv

# Завантажуємо довідник ноутбуків з CSV
with open("data/laptops.csv", encoding="utf-8") as f:
    ROWS = list(csv.DictReader(f))
    MODELS = [row["model"] for row in ROWS]
    PRICES = [float(row["price"]) for row in ROWS]


def check_meaning(name, args):
    if name == "laptop_info":
        if args.model not in MODELS:
            return (f"Помилка: моделі '{args.model}' немає в довіднику. "
                    f"Доступні: {', '.join(MODELS)}. "
                    "Спочатку знайди точну назву моделі через search_laptops.")
    if name == "calc_installment":
        if args.price not in PRICES:
            return (f"Помилка: ціни {args.price} грн немає в довіднику ноутбуків. "
                    "Спочатку дізнайся точну ціну моделі через laptop_info, а потім викликай calc_installment.")
    return None
