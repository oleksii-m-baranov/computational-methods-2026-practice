"""Перевірки змісту аргументів."""
import csv

# Завантажуємо довідник ноутбуків з CSV
with open("data/laptops.csv", encoding="utf-8") as f:
    MODELS = [row["model"] for row in csv.DictReader(f)]

def check_meaning(name, args):
    if name == "laptop_info":
        if args.model not in MODELS:
            return (f"Помилка: моделі '{args.model}' немає в довіднику. "
                    f"Доступні: {', '.join(MODELS)}. "
                    "Виправ назву моделі або повідом користувачу, що даних про неї немає.")
    return None